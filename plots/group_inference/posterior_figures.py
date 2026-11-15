"""Posterior group points and direct contrasts; no significance-star conversion."""
from pathlib import Path
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

def draw_posteriors(out):
    out=Path(out)
    snapshot=json.loads((out/"source_hashes.json").read_text(encoding="utf-8"))
    digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()
    for task,ch in ENDPOINTS:
        manifest=json.loads((out/"bayes"/(task+"_"+ch)/"posterior_manifest.json").read_text(encoding="utf-8"))
        if manifest.get("source_snapshot_sha256") != digest:
            raise ValueError("Cannot combine posterior endpoints from different source snapshots")
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
    print(json.dumps(draw_posteriors(OUTPUT_ROOT/"group_inference"),indent=2))
