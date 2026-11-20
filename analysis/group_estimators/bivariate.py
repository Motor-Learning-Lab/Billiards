"""Bivariate Student-t centers and participant weights for baseline/post scatterplots."""
import numpy as np
import pandas as pd

from analysis.robust.bivariate_t import DF, fit_bivariate_t


METRICS = ("location", "variance", "mae")
KEYS = ["task", "channel", "metric", "group"]
CENTER_COLUMNS = KEYS + [
    "n_pairs", "participant_ids", "df", "status", "message", "baseline", "post",
    "scatter_xx", "scatter_xy", "scatter_yy", "iterations", "log_likelihood",
]
WEIGHT_COLUMNS = KEYS + [
    "participant", "baseline", "post", "mahalanobis_distance",
    "mahalanobis_squared", "weight", "normalized_weight",
]


def fit_group_points(pairs):
    """Fit the original (pre, post) coordinates independently for each metric and group.

    Input follows participant_pairs.csv. A fit requires finite values at both
    stages for its metric. Complete pairs stay in the participant table even if
    their group has insufficient support to estimate a nonsingular scatter.
    """
    pairs = pairs.copy()
    id_columns = ["participant", "task", "channel", "group"]
    if pairs[id_columns].isna().any().any():
        raise ValueError("Missing participant, task, channel or training group in paired summaries.")
    # Reading a CSV without an explicit dtype may turn '01' into integer 1.
    pairs["participant"] = pairs.participant.astype(str).str.zfill(2)
    if pairs.duplicated(["participant", "task", "channel"]).any():
        raise ValueError("Duplicate participant within a task/channel endpoint.")
    if pairs.groupby("participant").group.nunique().gt(1).any():
        raise ValueError("A participant has conflicting training-group assignments.")

    centers, observations = [], []
    for (task, channel, group), panel in pairs.groupby(["task", "channel", "group"], sort=True):
        panel = panel.sort_values("participant")
        for metric in METRICS:
            coordinates = panel[[metric + "_pre", metric + "_post"]].to_numpy(dtype=float)
            complete = np.isfinite(coordinates).all(axis=1)
            xy = coordinates[complete]
            ids = panel.participant[complete].tolist()
            keys = dict(task=task, channel=channel, metric=metric, group=group)
            center = dict(**keys, n_pairs=len(ids), participant_ids=",".join(ids), df=DF)
            records = pd.DataFrame(dict(**keys, participant=ids, baseline=xy[:, 0], post=xy[:, 1]))
            try:
                fit = fit_bivariate_t(xy)
            except ValueError as exc:
                center.update(status="unavailable", message=str(exc))
            else:
                center.update(status="ok", message="", baseline=fit.location[0], post=fit.location[1],
                              scatter_xx=fit.scatter[0, 0], scatter_xy=fit.scatter[0, 1],
                              scatter_yy=fit.scatter[1, 1], iterations=fit.iterations,
                              log_likelihood=fit.log_likelihood)
                chol = np.linalg.cholesky(fit.scatter)
                residuals = np.linalg.solve(chol, (xy - fit.location).T)
                distances_sq = (residuals ** 2).sum(axis=0)
                weights = (DF + 2) / (DF + distances_sq)
                records["mahalanobis_distance"] = np.sqrt(distances_sq)
                records["mahalanobis_squared"] = distances_sq
                records["weight"] = weights
                records["normalized_weight"] = weights / weights.sum()
            centers.append(center)
            observations.append(records)

    weights = pd.concat(observations, ignore_index=True) if observations else pd.DataFrame()
    return pd.DataFrame(centers, columns=CENTER_COLUMNS), weights.reindex(columns=WEIGHT_COLUMNS)
