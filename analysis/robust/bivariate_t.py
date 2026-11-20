"""Maximum-likelihood location and scatter of one group of paired stage summaries."""
from dataclasses import dataclass
from itertools import combinations

import numpy as np


DF = 5


@dataclass(frozen=True)
class BivariateTFit:
    location: np.ndarray
    scatter: np.ndarray  # Student-t shape matrix; covariance is DF/(DF-2) times scatter.
    iterations: int
    log_likelihood: float


def _check_support(points):
    """Check the affine-subspace mass condition for an unrestricted t fit in 2D."""
    unique, counts = np.unique(points, axis=0, return_counts=True)
    n = len(points)
    if counts.max() * (DF + 2) >= n * DF:
        raise ValueError("Too many identical pairs for a nonsingular bivariate Student-t fit.")
    for a, b in combinations(unique, 2):
        dx, dy = b - a
        left = dx * (unique[:, 1] - a[1])
        right = dy * (unique[:, 0] - a[0])
        roundoff = 32 * np.finfo(float).eps * (np.abs(left) + np.abs(right))
        on_line = np.abs(left - right) <= roundoff
        if counts[on_line].sum() * (DF + 2) >= n * (DF + 1):
            raise ValueError("Too many collinear pairs for a nonsingular bivariate Student-t fit.")


def fit_bivariate_t(points):
    """Fit a df=5 bivariate t to finite (baseline, post-test) pairs using EM.

    Each pair receives one weight based on its joint Mahalanobis distance. The
    unrestricted scatter update divides by the number of pairs. Coordinates
    are standardized internally and returned on the original measurement scale.
    Invalid or unidentified fits raise ValueError.
    """
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 3:
        raise ValueError("The bivariate fit needs at least three complete pairs.")
    if not np.isfinite(points).all():
        raise ValueError("The bivariate fit requires finite paired coordinates.")
    center = points.mean(axis=0)
    units = points.std(axis=0)
    if np.any(units == 0):
        raise ValueError("A constant coordinate cannot identify a bivariate scatter matrix.")
    z = (points - center) / units
    _check_support(z)
    location = z.mean(axis=0)
    scatter = np.cov(z, rowvar=False, bias=True)
    n = len(points)
    try:
        for iteration in range(1, 1001):
            chol = np.linalg.cholesky(scatter)
            residuals = np.linalg.solve(chol, (z - location).T)
            squared_distances = (residuals ** 2).sum(axis=0)
            weights = (DF + 2) / (DF + squared_distances)
            next_location = np.average(z, weights=weights, axis=0)
            offsets = z - next_location
            next_scatter = (offsets.T * weights) @ offsets / n

            # Assess changes in the current scatter's units on both axes.
            mean_step = np.linalg.solve(chol, next_location - location)
            scatter_step = np.linalg.solve(chol, next_scatter - scatter)
            scatter_step = np.linalg.solve(chol, scatter_step.T)
            location, scatter = next_location, next_scatter
            if max(np.linalg.norm(mean_step), np.linalg.norm(scatter_step)) < 1e-9:
                break
        else:
            raise ValueError("The bivariate Student-t fit did not converge within 1000 EM iterations.")
        chol = np.linalg.cholesky(scatter)
        residuals = np.linalg.solve(chol, (z - location).T)
    except np.linalg.LinAlgError as exc:
        raise ValueError("The bivariate scatter matrix is numerically singular.") from exc

    # In two dimensions the t density at its center is 1/(2*pi*sqrt(det(scatter))).
    log_volume = np.log(np.diag(chol)).sum() + np.log(units).sum()
    log_likelihood = -n * (np.log(2 * np.pi) + log_volume)
    log_likelihood -= .5 * (DF + 2) * np.log1p((residuals ** 2).sum(axis=0) / DF).sum()
    return BivariateTFit(center + units * location, scatter * np.outer(units, units),
                         iteration, float(log_likelihood))
