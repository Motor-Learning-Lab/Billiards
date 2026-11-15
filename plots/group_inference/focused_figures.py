"""Separate estimators and magnify central observations without hiding extremes."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from common.publication_data import GROUPS, COLORS
from common.group_inference_data import ENDPOINTS
from .figures import style, save, MARKERS


def draw_focused(points, pairs, out):
    out = Path(out)
    style()
    for metric in ("location", "variance", "mae"):
        for estimator, marker in MARKERS.items():
            fig, axes = plt.subplots(2, 2, figsize=(10, 9), layout="constrained")
            for ax, (task, channel) in zip(axes.flat, ENDPOINTS):
                data = points[(points.task == task) & (points.channel == channel)
                              & (points.metric == metric) & (points.estimator == estimator)]
                people = pairs[(pairs.task == task) & (pairs.channel == channel)]
                x = people[metric + "_pre"].to_numpy()
                y = people[metric + "_post"].to_numpy()
                bounds = data[["baseline_low", "baseline_high", "post_low", "post_high"]].to_numpy().ravel()
                full = max(np.max(np.abs(np.r_[x, y, bounds])) * 1.08, 1e-3)
                focus = max(np.quantile(np.abs(np.r_[x, y]), .9), np.max(np.abs(bounds)), 1e-3) * 1.08
                use_zoom = metric != "variance" and full > 1.4 * focus
                limit = focus if use_zoom else full
                limits = (-limit, limit) if metric == "location" else (0, limit)
                inset = ax.inset_axes([.12, .65, .28, .28]) if use_zoom else None
                for group in GROUPS:
                    part = people[people.group == group]
                    q = data[data.group == group].iloc[0]
                    ax.scatter(part[metric + "_pre"], part[metric + "_post"], s=19,
                               color=COLORS[group], alpha=.35, zorder=2)
                    ax.hlines(q.post, q.baseline_low, q.baseline_high, color=COLORS[group], zorder=3)
                    ax.vlines(q.baseline, q.post_low, q.post_high, color=COLORS[group], zorder=3)
                    ax.scatter(q.baseline, q.post, color=COLORS[group], marker=marker,
                               edgecolors="white", linewidths=.5, s=55, zorder=4)
                    if inset is not None:
                        inset.scatter(part[metric + "_pre"], part[metric + "_post"],
                                      s=8, color=COLORS[group], alpha=.55)
                if metric == "variance":
                    threshold = .01 if channel == "strength" else .1
                    ax.set_xscale("symlog", linthresh=threshold)
                    ax.set_yscale("symlog", linthresh=threshold)
                ax.plot(limits, limits, "--", color=".55", lw=.8, zorder=0)
                ax.set_xlim(limits); ax.set_ylim(limits); ax.set_box_aspect(1)
                unit = "deg" if channel == "angle" else "strength units"
                if metric == "variance": unit += " squared"
                ax.set_xlabel("Baseline (" + unit + ")")
                ax.set_ylabel("Post-test (" + unit + ")")
                ax.set_title(task.title() + " task / " + channel)
                ax.grid(alpha=.15)
                if inset is not None:
                    extent = (-full, full) if metric == "location" else (0, full)
                    inset.plot(extent, extent, "--", color=".6", lw=.6)
                    inset.set_xlim(extent); inset.set_ylim(extent)
                    from matplotlib.ticker import MaxNLocator
                    inset.xaxis.set_major_locator(MaxNLocator(3))
                    inset.yaxis.set_major_locator(MaxNLocator(3))
                    inset.tick_params(labelsize=6); inset.set_title("Full range", fontsize=7)
                    from matplotlib.patches import Rectangle
                    inset.add_patch(Rectangle((limits[0], limits[0]), limits[1]-limits[0],
                                             limits[1]-limits[0], fill=False, ec=".4", lw=.7))
                    outside = ((x < limits[0]) | (x > limits[1]) | (y < limits[0]) | (y > limits[1])).sum()
                    ax.text(.98, .03, f"{outside} participants outside zoom; shown in inset",
                            transform=ax.transAxes, ha="right", fontsize=7)
            fig.suptitle(metric.upper() + " / " + estimator.replace("_", " ") +
                         "\nGroup estimate and pointwise 95% paired-bootstrap intervals", fontsize=12)
            fig.legend(handles=[Line2D([], [], marker="o", ls="", color=COLORS[g],
                                      label=g.title()) for g in GROUPS],
                       loc="outside lower center", ncol=3)
            save(fig, out, "focused_" + metric + "_" + estimator)


if __name__ == "__main__":
    from common.paths import OUTPUT_ROOT
    root = OUTPUT_ROOT / "group_inference"
    draw_focused(pd.read_csv(root / "estimator_group_points.csv"),
                 pd.read_csv(root / "participant_pairs.csv"), root)
