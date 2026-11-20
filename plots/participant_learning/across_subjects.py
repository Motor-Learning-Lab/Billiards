"""Group learning curves from participant-specific training location/scale fits."""
import hashlib
import json

from plots.participant_learning.app import FILE_PATTERN, load_series
from analysis.robust.censoring import censor_codes, censor_values
from analysis.robust.student_t import fit_student_t
from common.paths import ASSIGNMENTS_PATH, OUTPUT_ROOT, PARTICIPANT_ROOT
from common.publication_data import CHANNELS, COLORS
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


TRIALS = np.arange(1, 141)
UNITS = {"strength": "origin_to_strip", "angle": "degree"}
OUTPUT = OUTPUT_ROOT / "across_subject_learning"


def collect_predictions():
    assignments = json.loads(ASSIGNMENTS_PATH.read_text(encoding="utf-8-sig"))["assignments"]
    groups = {f"{i:02d}": assignments[f"{i:02d}"].lower() for i in range(1, 31)}
    if any(list(groups.values()).count(group) != 10 for group in CHANNELS):
        raise ValueError("Expected ten participants in each training group.")
    curves, audit = [], []
    for participant, group in groups.items():
        folder = PARTICIPANT_ROOT / participant / "outlier_results" / "labeled_csv"
        files = []
        for path in sorted(folder.rglob("*.csv")):
            match = FILE_PATTERN.match(path.stem)
            if match and match[3].lower() == "training":
                task = match[4].lower()
                if int(match[1]) != int(participant) or (group != task and (group, task) != ("both", "regular")):
                    raise ValueError(f"Training file conflicts with assignment for {participant}: {path}")
                files.append(path)
        if len(files) != 1:
            raise ValueError(f"Expected one labeled training file for {participant}, found {len(files)}.")
        path = files[0]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        source = pd.read_csv(path).sort_values("shot")
        for channel in CHANNELS[group]:
            if channel + "_outlier" not in source:
                raise ValueError(f"Missing {channel} outlier flags in {path.name}")
            series = load_series(path, "training", group, metric=channel)
            if series.units != (UNITS[channel],) or not np.isin(series.shot, TRIALS).all():
                raise ValueError(f"Unexpected trial range or {channel} units in {path.name}")
            if not np.array_equal(source.shot.to_numpy(), series.shot):
                raise ValueError(f"Trial alignment failed in {path.name}")
            values = censor_values(source, channel)
            values[~np.isfinite(series.value)] = np.nan
            fit = fit_student_t(series.shot, values, censor=censor_codes(source, channel))
            if not fit.success:
                raise ValueError(f"Fit unavailable for {participant}/{channel}: {fit.message}")
            trials = TRIALS[(TRIALS >= fit.xmin) & (TRIALS <= fit.xmax)]
            prediction = fit.predict(trials)
            keys = dict(participant=participant, group=group, channel=channel)
            curves.append(pd.DataFrame(dict(**keys, trial=trials, mean=prediction["mean"],
                                            variance=prediction["variance"])))
            audit.append(dict(**keys, source=path.relative_to(PARTICIPANT_ROOT).as_posix(),
                              sha256=digest, recorded=len(source), outlier_flags=int(series.outlier.sum()),
                              n_used=fit.n_obs, n_censored=fit.n_censored,
                              first_trial=int(trials[0]), last_trial=int(trials[-1])))
    return pd.concat(curves, ignore_index=True), pd.DataFrame(audit)


def summarize(curves):
    by_trial = curves.groupby(["group", "channel", "trial"])
    summary = by_trial[["mean", "variance"]].mean()
    summary["n"] = by_trial.participant.nunique()
    summary["participants"] = by_trial.participant.agg(",".join)
    for metric in ("mean", "variance"):
        summary[metric + "_q25"] = by_trial[metric].quantile(.25)
        summary[metric + "_q75"] = by_trial[metric].quantile(.75)
    return summary.reset_index()


def render(summary, output):
    fig, axes = plt.subplots(3, 2, sharex=True, figsize=(10.5, 8.3),
                             gridspec_kw={"height_ratios": [1, 1, .46]})
    fig.subplots_adjust(left=.10, right=.98, bottom=.12, top=.83, hspace=.50, wspace=.31)
    fig.suptitle("Learning curves across subjects", x=.10, y=.975, ha="left",
                 fontsize=19, fontweight="bold")
    handles = [Line2D([], [], color=COLORS[g], lw=2.5, ls="-" if g == "both" else "--",
                      label=label) for g, label in (("both", "Both"), ("strength", "Strength only"),
                                                    ("angle", "Angle only"))]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(.092, .929),
               ncol=3, frameon=False, title="Training group", alignment="left")
    for col, channel in enumerate(("strength", "angle")):
        unit = "origin-to-strip units" if channel == "strength" else "degrees"
        titles = (f"{channel.title()} · Mean signed error", f"{channel.title()} · Within-person variance",
                  f"{channel.title()} · Contributing participants")
        for row, metric in enumerate(("mean", "variance", "n")):
            ax = axes[row, col]
            ax.set_title(f"{'abcdef'[2 * row + col]}    {titles[row]}", loc="left",
                         fontsize=11, weight="bold", pad=7)
            ax.grid(axis="y", color="#e4e7e9", linewidth=.7)
            ax.set_axisbelow(True)
            for group in ("both", channel):
                part = summary[(summary.group == group) & (summary.channel == channel)]
                part = part.set_index("trial").reindex(TRIALS)
                color = COLORS[group]
                style = "-" if group == "both" else "--"
                if metric == "n":
                    ax.step(TRIALS, part.n.fillna(0), where="mid", color=color, ls=style, lw=1.8)
                else:
                    segments = part.participants.ne(part.participants.shift()).cumsum()
                    for _, segment in part.dropna(subset=[metric]).groupby(segments):
                        ax.fill_between(segment.index, segment[metric + "_q25"].to_numpy(),
                                        segment[metric + "_q75"].to_numpy(), color=color, alpha=.14, lw=0)
                        ax.plot(segment.index, segment[metric], color=color, ls=style, lw=2.2,
                                marker="o" if len(segment) < 5 else None, ms=3)
                        if len(segment) == 1:
                            ax.vlines(segment.index, segment[metric + "_q25"], segment[metric + "_q75"],
                                      color=color, alpha=.35, linewidth=1)
            if metric == "mean":
                ax.axhline(0, color="#525a60", lw=.7, ls=":", zorder=1)
                ax.set_ylabel(unit)
            elif metric == "variance":
                ax.set_ylim(bottom=0)
                ax.set_ylabel(f"({unit})²")
            else:
                lowest = int(summary.n.min()) if len(summary) == len(TRIALS) * 4 else 0
                ax.set(ylim=(lowest - .35, 10.35), yticks=range(lowest, 11),
                       ylabel="Participants", xlabel="Training trial")
            ax.set(xlim=(0, 141), xticks=[1, 35, 70, 105, 140])
    fig.text(.10, .028, "Lines show equal-weight group averages and break when contributors change.\n"
             "Shading and vertical bars span the middle 50% of individual fitted curves.",
             fontsize=9)
    for extension in ("png", "pdf"):
        fig.savefig(output / f"learning_curves_across_subjects.{extension}", dpi=220)
    plt.close(fig)


def main():
    curves, audit = collect_predictions()
    summary = summarize(curves)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    render(summary, OUTPUT)
    for name, frame in (("group_curves", summary), ("participant_curves", curves), ("fit_audit", audit)):
        frame.to_csv(OUTPUT / f"{name}.csv", index=False, lineterminator="\n")


if __name__ == "__main__":
    main()
