"""Rebuild group-inference scatterplots from their own paired participant summaries."""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

from analysis.group_estimators.bivariate import METRICS, fit_group_points
from common.group_inference_data import ENDPOINTS
from common.paths import OUTPUT_ROOT
from common.publication_data import COLORS, GROUPS
from .figures import draw_estimator_scatter, draw_t_centers, save, style
from .focused_figures import draw_focused


TITLES = {"location": "Signed error", "variance": "Within-participant variance",
          "mae": "Mean absolute error"}


def draw_population_only(centers, out):
    style()
    for metric in METRICS:
        fig, axes = plt.subplots(2, 2, figsize=(9, 8), layout="constrained")
        for i, (ax, (task, channel)) in enumerate(zip(axes.flat, ENDPOINTS)):
            data = centers[(centers.task == task) & (centers.channel == channel)
                           & (centers.metric == metric) & (centers.status == "ok")]
            values = data[["baseline", "post"]].to_numpy()
            extent = max(np.abs(values).max(initial=0) * 1.18, 1e-3)
            limits = (-extent, extent) if metric == "location" else (0, extent)
            ax.plot(limits, limits, "--", color=".55", lw=.8, zorder=0)
            draw_t_centers(ax, centers, task, channel, metric, size=100)
            unit = "degrees" if channel == "angle" else "strength units"
            if metric == "variance":
                unit += "²"
            ax.set(xlim=limits, ylim=limits, xlabel=f"Baseline ({unit})", ylabel=f"Post-test ({unit})")
            ax.set_box_aspect(1)
            ax.set_title(f"{'abcd'[i]}    {task.title()} task / {channel}", loc="left")
            ax.grid(alpha=.16)
        handles = [Line2D([], [], marker="D", markerfacecolor="none", markeredgewidth=1.5,
                          ls="", color=COLORS[g], label=g.title() + " training") for g in GROUPS]
        fig.legend(handles=handles, loc="outside lower center", ncol=3, frameon=False)
        fig.suptitle(TITLES[metric] + "\nBivariate Student-t population centers (df = 5)")
        save(fig, out, "bivariate_t_" + metric)


def write_scatterplots(points, pairs, out):
    centers, weights = fit_group_points(pairs)
    centers.to_csv(out / "bivariate_t_group_points.csv", index=False, lineterminator="\n")
    weights.to_csv(out / "bivariate_t_participant_weights.csv", index=False, lineterminator="\n")
    draw_estimator_scatter(points, pairs, out, centers)
    draw_focused(points, pairs, out, centers)
    draw_population_only(centers, out)


if __name__ == "__main__":
    root = OUTPUT_ROOT / "group_inference"
    write_scatterplots(pd.read_csv(root / "estimator_group_points.csv"),
                       pd.read_csv(root / "participant_pairs.csv", dtype={"participant": str}), root)
