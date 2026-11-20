"""Posterior group points and direct contrasts; no significance-star conversion."""
from pathlib import Path
import argparse
import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from common.publication_data import GROUPS,COLORS
from common.group_inference_data import ENDPOINTS
from plots.group_inference.figures import style,save

def _check_snapshots(out):
    snapshot=json.loads((out/"source_hashes.json").read_text(encoding="utf-8"))
    digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()
    for task,ch in ENDPOINTS:
        manifest=json.loads((out/"bayes"/(task+"_"+ch)/"posterior_manifest.json").read_text(encoding="utf-8"))
        if manifest.get("source_snapshot_sha256") != digest:
            raise ValueError("Cannot combine posterior endpoints from different source snapshots")


def draw_variance_scatter(out):
    """Overlay individual stage fits with trial-level hierarchical group parameters."""
    out = Path(out)
    _check_snapshots(out)
    pairs = pd.read_csv(out / "participant_pairs.csv", dtype={"participant": str})
    if pairs.duplicated(["task", "channel", "participant"]).any():
        raise ValueError("Duplicate participant within a variance panel")
    style()
    fig, axes = plt.subplots(2, 2, figsize=(8.6, 8.5))
    fig.subplots_adjust(left=.105, right=.965, bottom=.135, top=.82, wspace=.29, hspace=.43)
    fig.suptitle("Baseline and post-test variance", x=.105, y=.974, ha="left",
                 fontsize=18, fontweight="bold")
    fig.text(.105, .925, "Small symbols: individual stage fits     Large symbols: hierarchical population estimates", fontsize=10)
    shapes = {"both": "o", "strength": "s", "angle": "^"}
    handles = [Line2D([], [], marker=shapes[g], linestyle="none", color=COLORS[g],
                      label=g.title() + " training") for g in GROUPS]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.09, .906),
               ncol=3, frameon=False)
    rows = []
    ranges = {}
    for index, (ax, (task, channel)) in enumerate(zip(axes.flat, ENDPOINTS)):
        folder = out / "bayes" / f"{task}_{channel}"
        stages = pd.read_csv(folder / "group_stages.csv")
        stages = stages.loc[stages.metric == "within_variance"].set_index(["group", "stage"], verify_integrity=True)
        participants = pairs[(pairs.task == task) & (pairs.channel == channel)]
        unit = "deg²" if channel == "angle" else "strength units²"
        for group in GROUPS:
            people = participants.loc[participants.group == group, ["variance_pre", "variance_post"]].dropna()
            x, y = people.to_numpy().T
            pre = stages.loc[(group, "baseline")]
            post = stages.loc[(group, "test")]
            bounds = np.array([pre.cri_low, pre["median"], pre.cri_high,
                               post.cri_low, post["median"], post.cri_high])
            values = np.r_[x, y, bounds]
            if not np.isfinite(values).all() or np.any(values <= 0):
                raise ValueError(f"Invalid variance for logarithmic axes in {task}/{channel}/{group}")
            ranges.setdefault(channel, []).extend(values)
            ax.scatter(x, y, color=COLORS[group], marker=shapes[group], s=22, alpha=.38,
                       linewidths=0, zorder=2, gid=f"individual-{group}")
            ax.errorbar(pre["median"], post["median"],
                        xerr=[[pre["median"] - pre.cri_low], [pre.cri_high - pre["median"]]],
                        yerr=[[post["median"] - post.cri_low], [post.cri_high - post["median"]]],
                        fmt=shapes[group], color=COLORS[group], markeredgecolor="black",
                        markeredgewidth=.8, markersize=8, elinewidth=1.4, capsize=2.8, zorder=4)
            rows.append(dict(task=task, channel=channel, group=group, n_plotted_pairs=len(people),
                             baseline_median=pre["median"], baseline_low=pre.cri_low, baseline_high=pre.cri_high,
                             post_median=post["median"], post_low=post.cri_low, post_high=post.cri_high))
        ax.set(xscale="log", yscale="log", xlabel=f"Baseline variance ({unit})",
               ylabel=f"Post-test variance ({unit})")
        ax.set_title(f"{'abcd'[index]}    {task.title()} task / {channel}", loc="left", fontweight="bold")
        ax.grid(which="major", alpha=.2)
        ax.set_aspect("equal", adjustable="box")
    for ax, (_, channel) in zip(axes.flat, ENDPOINTS):
        lo, hi = min(ranges[channel]), max(ranges[channel])
        pad = max((hi / lo) ** .045, 1.1)
        limits = (lo / pad, hi * pad)
        ax.plot(limits, limits, ls="--", color=".45", lw=.85, zorder=1)
        ax.set(xlim=limits, ylim=limits)
    fig.text(.105, .045, "Crosshairs show marginal 95% credible intervals. The dashed diagonal marks equal variance.",
             fontsize=9)
    save(fig, out, "hierarchical_variance_scatter")
    pd.DataFrame(rows).to_csv(out / "hierarchical_variance_scatter.csv", index=False, lineterminator="\n")


def draw_posteriors(out):
    out=Path(out)
    _check_snapshots(out)
    style();fig,axes=plt.subplots(2,4,figsize=(15,8),layout="constrained")
    fig.get_layout_engine().set(hspace=.12)
    effect,ea=plt.subplots(3,4,figsize=(16,10),layout="constrained")
    comparisons=[("both","strength"),("both","angle"),("strength","angle")]
    statuses={}
    for col,(task,ch) in enumerate(ENDPOINTS):
        folder=out/"bayes"/(task+"_"+ch)
        diagnostics=json.loads((folder/"diagnostics.json").read_text());statuses[task+"_"+ch]=diagnostics
        stages=pd.read_csv(folder/"group_stages.csv");contrasts=pd.read_csv(folder/"between_group_contrasts.csv")
        note="" if diagnostics["sampling_adequate"] else " [diagnostics pending]"
        for row,metric in enumerate(("location","within_variance")):
            ax=axes[row,col];sub=stages[stages.metric==metric]
            for group in GROUPS:
                g=sub[sub.group==group].set_index("stage");x=g.loc["baseline"];y=g.loc["test"]
                ax.errorbar(x["median"],y["median"],xerr=[[x["median"]-x.cri_low],[x.cri_high-x["median"]]],
                    yerr=[[y["median"]-y.cri_low],[y.cri_high-y["median"]]],fmt="o",color=COLORS[group],capsize=3,markersize=6)
            values=np.r_[sub.cri_low,sub.cri_high];mx=max(np.max(np.abs(values))*1.1,1e-4)
            limits=(-mx,mx) if metric=="location" else (max(float(values.min())*.85,1e-12),mx)
            if metric=="within_variance":
                ax.set_xscale("log");ax.set_yscale("log")
            ax.plot(limits,limits,color=".5",ls="--",lw=.8);ax.set_xlim(limits);ax.set_ylim(limits);ax.set_box_aspect(1)
            ax.set_title(task.title()+" / "+ch+" / "+metric.replace("_"," ")+note,fontsize=8)
            unit="deg" if ch=="angle" else "strength units"
            if metric=="within_variance":unit+=" squared"
            ax.set_xlabel("Baseline ("+unit+")");ax.set_ylabel("Post-test ("+unit+")");ax.grid(alpha=.15)
        for row,metric in enumerate(("location_change","variance_change","log_variance_ratio")):
            ax=ea[row,col];sub=contrasts[contrasts.metric==metric]
            for j,(a,b) in enumerate(comparisons):
                q=sub[(sub.group_a==a)&(sub.group_b==b)].iloc[0]
                ax.plot([q.cri_low,q.cri_high],[j,j],color=COLORS[a]);ax.scatter(q["median"],j,color=COLORS[a],s=25)
                ax.text(.99,j+.2,f"P(A-B<0)={q.prob_less_zero:.3f}",transform=ax.get_yaxis_transform(),ha="right",fontsize=7)
            ax.axvline(0,color=".4",ls="--",lw=.8);ax.set_yticks(range(3),["Both - Strength","Both - Angle","Strength - Angle"] if col==0 else [])
            ax.set_ylim(2.6,-.5);ax.set_title(task.title()+" / "+ch+" / "+metric.replace("_"," ")+note,fontsize=8)
            ax.set_xlabel("Group A change minus group B change");ax.grid(axis="x",alpha=.15)
    fig.legend(handles=[Line2D([],[],marker="o",ls="",color=COLORS[g],label=g.title()) for g in GROUPS],loc="outside lower center",ncol=3)
    fig.suptitle("Hierarchical group points\nPosterior median with marginal 95% credible intervals (not SEM)",fontsize=12)
    effect.suptitle("Between-group effects: posterior median, 95% credible intervals and directional probability",fontsize=12)
    save(fig,out,"hierarchical_group_points");save(effect,out,"hierarchical_group_effects")
    return statuses

if __name__=="__main__":
    from common.paths import OUTPUT_ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variance-only", action="store_true", help="Render the standalone paired variance figure")
    root = OUTPUT_ROOT / "group_inference"
    if parser.parse_args().variance_only:
        draw_variance_scatter(root)
    else:
        print(json.dumps(draw_posteriors(root),indent=2))
