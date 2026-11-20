import unittest

import numpy as np
from scipy.optimize import minimize
from scipy.stats import multivariate_t

from analysis.robust.bivariate_t import DF, fit_bivariate_t


class BivariateTTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(12)
        self.points = rng.multivariate_normal([1.2, -.4], [[2., .3], [.3, .8]], 10)
        self.points[-1] += [8., 10.]

    def test_matches_direct_likelihood_optimization(self):
        def unpack(theta):
            lower = np.array([[np.exp(theta[2]), 0], [theta[3], np.exp(theta[4])]])
            return theta[:2], lower @ lower.T

        def nll(theta):
            location, scatter = unpack(theta)
            return -multivariate_t.logpdf(self.points, loc=location, shape=scatter, df=DF).sum()

        direct = minimize(nll, [0., 0., 0., 0., 0.], method="BFGS", jac="3-point",
                          options={"gtol": 1e-7})
        self.assertTrue(direct.success, direct.message)
        mean, scatter = unpack(direct.x)
        fit = fit_bivariate_t(self.points)
        np.testing.assert_allclose(fit.location, mean, atol=5e-6)
        np.testing.assert_allclose(fit.scatter, scatter, atol=5e-6)
        self.assertAlmostEqual(fit.log_likelihood, -direct.fun, places=8)

    def test_affine_equivariance_and_pair_order(self):
        a = np.array([[.7, .2], [-4., 2.]])
        shift = np.array([-3., 17.])
        fit = fit_bivariate_t(self.points)
        other = fit_bivariate_t(self.points[::-1] @ a.T + shift)
        np.testing.assert_allclose(other.location, a @ fit.location + shift)
        np.testing.assert_allclose(other.scatter, a @ fit.scatter @ a.T)

    def test_insufficient_or_unidentified_support(self):
        line = [[i, 2 * i + 1] for i in range(6)]
        examples = ([], self.points[:2], [[0, 1], [1, 2], [2, np.nan]],
                    [[0, 0]] * 5 + [[1, 0], [0, 1]], line + [[4, 0]])
        for points in examples:
            with self.subTest(points=points):
                with self.assertRaises(ValueError):
                    fit_bivariate_t(points)


if __name__ == "__main__":
    unittest.main()
