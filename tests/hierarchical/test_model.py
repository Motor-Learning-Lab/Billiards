import unittest
import numpy as np
import pymc as pm
from scipy.stats import t
from analysis.hierarchical.model import build_model, validate_data, summarize_posterior


def toy_data(seed=42, per_group=3, trials=12):
    rng=np.random.default_rng(seed)
    n=per_group*3
    p=np.repeat(np.arange(n),2*trials)
    stage=np.tile(np.repeat([0,1],trials),n)
    group=np.repeat(np.arange(3),per_group)
    baseline=np.array([.4,0.,-.4])
    change=np.array([-.3,.0,.3])
    person=rng.normal(0,.05,n)
    mean=baseline[group[p]]+person[p]+stage*change[group[p]]
    y=mean+.2*rng.standard_t(5,len(p))
    censor=np.zeros(len(y),int)
    censor[y<-.8]=-1; censor[y>.8]=1
    y=np.clip(y,-.8,.8)
    return dict(y=y,censor=censor,participant_index=p,stage_index=stage,
                group_index_per_participant=group,scale=.5)


class HierarchicalTests(unittest.TestCase):
    def test_orthogonal_reparameterization_preserves_group_prior(self):
        from scipy.linalg import helmert
        q=helmert(3,full=False).T
        for prior_sd,tau in [(1.5,.75),(.75,.5),(.5,.35)]:
            covariance=(prior_sd**2+tau**2/3)*np.ones((3,3))+tau**2*q@q.T
            np.testing.assert_allclose(covariance,prior_sd**2*np.ones((3,3))+tau**2*np.eye(3))

    def test_censor_probability_matches_scipy(self):
        y=np.array([-1.,.25,1.])
        rv=pm.Censored.dist(pm.StudentT.dist(nu=5,mu=.1,sigma=.7),
                             lower=np.array([-1.,-np.inf,-np.inf]),
                             upper=np.array([np.inf,np.inf,1.]))
        expected=np.array([t.logcdf((-1-.1)/.7,5),
                           t.logpdf((.25-.1)/.7,5)-np.log(.7),
                           t.logsf((1-.1)/.7,5)])
        np.testing.assert_allclose(pm.logp(rv,y).eval(),expected,rtol=1e-6)

    def test_validation_preserves_zero_target_and_pairing(self):
        d=toy_data()
        y,*_=validate_data(d)
        np.testing.assert_allclose(y,d['y']/.5)
        d['stage_index'][:24]=0
        with self.assertRaisesRegex(ValueError,'baseline and post-test'):
            validate_data(d)

    def test_logp_gradient_finite_and_variance_formula(self):
        model=build_model(toy_data())
        initial=model.initial_point()
        self.assertTrue(np.isfinite(model.compile_logp()(initial)))
        self.assertTrue(np.isfinite(model.compile_dlogp()(initial)).all())
        with model:
            prior=pm.sample_prior_predictive(samples=5,random_seed=55,
                var_names=['group_within_variance','logscale_baseline','logscale_change',
                           'person_logscale_baseline_sd','person_logscale_change_sd'])
        p=prior.prior
        ls0=p.logscale_baseline.values; delta=p.logscale_change.values
        v0=p.person_logscale_baseline_sd.values[...,None]**2
        vd=p.person_logscale_change_sd.values[...,None]**2
        expected=.5**2*5/3*np.exp(2*np.stack([ls0,ls0+delta],axis=-1)+
                                 2*np.stack([v0+np.zeros_like(ls0),v0+vd+np.zeros_like(ls0)],axis=-1))
        np.testing.assert_allclose(p.group_within_variance.values,expected)


if __name__=='__main__': unittest.main()
