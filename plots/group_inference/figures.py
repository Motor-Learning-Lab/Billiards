"""English diagnostic figures for group estimands, with explicit interval semantics."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from common.publication_data import GROUPS, COLORS
from common.group_inference_data import ENDPOINTS
from analysis.group_estimators.bivariate import fit_group_points

MARKERS={"mean":"o","median":"s","trimmed_mean_20pct":"^"}


def draw_t_centers(ax, centers, task, channel, metric, size=86):
    """Use the same exported population coordinates wherever the panel occurs."""
    panel = centers[(centers.task == task) & (centers.channel == channel)
                    & (centers.metric == metric) & (centers.status == "ok")]
    for point in panel.itertuples():
        ax.scatter(point.baseline, point.post, marker="D", s=size, facecolors="none",
                   edgecolors=COLORS[point.group], linewidths=1.5, zorder=6,
                   gid=f"bivariate-t-{point.group}")


def t_legend_marker():
    return Line2D([], [], marker="D", ls="", markerfacecolor="none", markeredgecolor="black",
                  label="Bivariate t center")

def style():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"pdf.fonttype":42,"savefig.dpi":300})

def save(fig,out,name):
    fig.savefig(out/(name+".png"),dpi=300);fig.savefig(out/(name+".pdf"));plt.close(fig)

def draw_estimator_scatter(points,pairs,out,centers=None):
    if centers is None:
        centers, _ = fit_group_points(pairs)
    style();fig,axes=plt.subplots(3,4,figsize=(15,11),layout="constrained")
    for row,metric in enumerate(("location","variance","mae")):
        for col,(task,ch) in enumerate(ENDPOINTS):
            ax=axes[row,col];data=points[(points.task==task)&(points.channel==ch)&(points.metric==metric)]
            people=pairs[(pairs.task==task)&(pairs.channel==ch)]
            for group in GROUPS:
                part=people[people.group==group]
                ax.scatter(part[metric+"_pre"],part[metric+"_post"],s=13,color=COLORS[group],alpha=.22,zorder=1)
                for est,marker in MARKERS.items():
                    q=data[(data.group==group)&(data.estimator==est)].iloc[0]
                    ax.hlines(q.post,q.baseline_low,q.baseline_high,color=COLORS[group],alpha=.85,zorder=3)
                    ax.vlines(q.baseline,q.post_low,q.post_high,color=COLORS[group],alpha=.85,zorder=3)
                    ax.scatter(q.baseline,q.post,marker=marker,color=COLORS[group],s=25,zorder=4)
            draw_t_centers(ax, centers, task, ch, metric, size=68)
            a=np.r_[data.baseline_low,data.baseline_high,data.post_low,data.post_high,people[metric+"_pre"],people[metric+"_post"]]
            a=a[np.isfinite(a)];mx=max(np.max(np.abs(a))*1.12,1e-3)
            lim=(-mx,mx) if metric=="location" else (0,mx)
            if metric=="variance":
                threshold=.01 if ch=="strength" else .1
                ax.set_xscale("symlog",linthresh=threshold);ax.set_yscale("symlog",linthresh=threshold)
            ax.plot(lim,lim,color=".5",ls="--",lw=.8,zorder=0);ax.set_xlim(lim);ax.set_ylim(lim);ax.set_box_aspect(1)
            unit="deg" if ch=="angle" else "strength units"
            ax.set_title(f"{task.title()} task: {ch} / {metric}",fontsize=9)
            ax.set_xlabel("Baseline ("+unit+(" squared" if metric=="variance" else "")+")");ax.set_ylabel("Post-test");ax.grid(alpha=.15)
    handles=[Line2D([],[],marker="o",ls="",color=COLORS[g],label=g.title()) for g in GROUPS]
    handles += [Line2D([],[],marker=m,ls="",color="black",label=e.replace("_"," ")) for e,m in MARKERS.items()]
    fig.legend(handles=handles+[t_legend_marker()],loc="outside lower center",ncol=7)
    fig.suptitle("Group-point sensitivity\nOpen diamonds show paired bivariate t centers. Crosshairs show pointwise 95% bootstrap intervals for the other estimators.",fontsize=12)
    save(fig,out,"group_estimator_sensitivity")

def draw_estimator_effects(contrasts,out):
    style();fig,axes=plt.subplots(3,4,figsize=(15,10),layout="constrained")
    labels=["Both - Strength","Both - Angle","Strength - Angle"]
    comparisons=[("both","strength"),("both","angle"),("strength","angle")]
    for row,metric in enumerate(("location","variance","mae")):
        for col,(task,ch) in enumerate(ENDPOINTS):
            ax=axes[row,col];sub=contrasts[(contrasts.task==task)&(contrasts.channel==ch)&(contrasts.metric==metric)]
            for j,(a,b) in enumerate(comparisons):
                for k,(est,marker) in enumerate(MARKERS.items()):
                    q=sub[(sub.group_a==a)&(sub.group_b==b)&(sub.estimator==est)].iloc[0];y=j+(k-1)*.2
                    ax.plot([q.low,q.high],[y,y],color=COLORS[GROUPS[k]],lw=1.2)
                    ax.scatter(q.difference_in_changes,y,marker=marker,color=COLORS[GROUPS[k]],s=25)
            ax.axvline(0,color=".4",ls="--",lw=.8);ax.set_yticks(range(3),labels if col==0 else []);ax.invert_yaxis()
            ax.set_title(f"{task.title()} task: {ch} / {metric}",fontsize=9);ax.set_xlabel("Difference in changes (A - B)");ax.grid(axis="x",alpha=.15)
    fig.legend(handles=[Line2D([],[],color=COLORS[GROUPS[k]],marker=m,label=e.replace("_"," ")) for k,(e,m) in enumerate(MARKERS.items())],loc="outside lower center",ncol=3)
    fig.suptitle("Direct between-group effects: post-minus-baseline estimator changes; pointwise 95% bootstrap intervals",fontsize=12)
    save(fig,out,"group_estimator_contrasts")
