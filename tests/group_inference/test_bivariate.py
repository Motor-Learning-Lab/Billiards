import unittest

import numpy as np
import pandas as pd

from analysis.group_estimators.bivariate import fit_group_points
from analysis.robust.bivariate_t import DF, fit_bivariate_t


class GroupBivariateTests(unittest.TestCase):
    def setUp(self):
        xy = np.array([[1., .2], [.4, .6], [1.4, 1.2], [2.1, .4], [.2, 1.8], [8., 9.]])
        rows = []
        for j, group in enumerate(["both", "strength"]):
            for i, (x, y) in enumerate(xy + 3 * j):
                rows.append(dict(participant=i + 1 + len(xy) * j, group=group, task="both", channel="angle",
                                 location_pre=x - 1, location_post=y - 1, variance_pre=x**2,
                                 variance_post=y**2, mae_pre=x, mae_post=y))
        self.pairs = pd.DataFrame(rows)

    def test_weights_and_scatter_match_paired_raw_scale_fit(self):
        centers, diagnostics = fit_group_points(self.pairs.sample(frac=1, random_state=1))
        self.assertEqual(len(centers), 6)
        self.assertTrue(centers.status.eq("ok").all())
        for c in centers.itertuples():
            w = diagnostics[(diagnostics.metric == c.metric) & (diagnostics.group == c.group)]
            xy = self.pairs.loc[self.pairs.group == c.group, [c.metric + "_pre", c.metric + "_post"]]
            np.testing.assert_array_equal(w[["baseline", "post"]], xy)
            self.assertEqual(c.n_pairs, 6)
            self.assertEqual(c.participant_ids, ",".join(w.participant))
            fit = fit_bivariate_t(xy)
            np.testing.assert_allclose([c.baseline, c.post], fit.location)
            np.testing.assert_allclose([c.scatter_xx, c.scatter_xy, c.scatter_yy], fit.scatter[[0, 0, 1], [0, 1, 1]])
            residuals = xy.to_numpy() - fit.location
            d2 = np.einsum("ij,jk,ik->i", residuals, np.linalg.inv(fit.scatter), residuals)
            np.testing.assert_allclose(w.mahalanobis_squared, d2)
            np.testing.assert_allclose(w.mahalanobis_distance, np.sqrt(d2))
            np.testing.assert_allclose(w.weight, (DF + 2) / (DF + d2))
            self.assertAlmostEqual(w.normalized_weight.sum(), 1)
            np.testing.assert_allclose(w.normalized_weight @ xy.to_numpy(), fit.location, atol=1e-8)

    def test_metric_specific_complete_pairs_and_unavailable_fit(self):
        rows = self.pairs[self.pairs.group == "both"].copy()
        rows.loc[0, "mae_pre"] = np.inf
        rows.loc[1, "mae_post"] = np.nan
        rows["variance_post"] = rows.variance_pre * 2
        centers, weights = fit_group_points(rows)
        c = centers.set_index("metric")
        self.assertEqual(c.loc["location", "n_pairs"], 6)
        self.assertEqual(c.loc["mae", "participant_ids"], "03,04,05,06")
        self.assertEqual(c.loc["mae", "status"], "ok")
        self.assertEqual(c.loc["variance", "status"], "unavailable")
        self.assertTrue(np.isnan(c.loc["variance", "baseline"]))
        w = weights[weights.metric == "variance"]
        self.assertEqual(len(w), 6)
        self.assertTrue(w.normalized_weight.isna().all())

    def test_duplicate_participant_and_insufficient_pairs(self):
        duplicate = pd.concat([self.pairs, self.pairs.iloc[[0]]])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            fit_group_points(duplicate)
        sparse = self.pairs.iloc[:2].copy()
        sparse["location_pre"] = np.nan
        centers, weights = fit_group_points(sparse)
        self.assertTrue(centers.status.eq("unavailable").all())
        self.assertEqual(centers.loc[centers.metric == "location", "n_pairs"].item(), 0)
        self.assertEqual(len(weights), 4)


if __name__ == "__main__":
    unittest.main()
