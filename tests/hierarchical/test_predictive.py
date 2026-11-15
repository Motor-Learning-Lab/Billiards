import unittest
from unittest.mock import patch
import numpy as np
import arviz as az
from .test_model import toy_data
from analysis.hierarchical.predictive import predictive_checks


class PredictiveTests(unittest.TestCase):
    def posterior(self,data):
        n=len(data['group_index_per_participant'])
        coords={'participant':[str(i) for i in range(n)],'stage':['baseline','test']}
        dims={'participant_location':['participant','stage'],'participant_within_variance':['participant','stage']}
        arrays={'participant_location':np.zeros((1,10,n,2)),
                'participant_within_variance':np.full((1,10,n,2),.1)}
        return az.from_dict(posterior=arrays,prior=arrays,coords=coords,dims=dims)

    def test_unknown_design_does_not_claim_censor_rate_or_coverage(self):
        data=toy_data();idata=self.posterior(data)
        self.assertTrue(np.any(data['censor']))
        with patch('analysis.hierarchical.predictive.pm.sample_prior_predictive',return_value=idata):
            table,meta=predictive_checks(data,idata,replicates=10)
        self.assertTrue(meta['latent_only'])
        self.assertFalse(meta['censor_rate_check_available'])
        self.assertNotIn('censor_rate',set(table.metric))
        self.assertTrue(table.inside_95_predictive_interval.isna().all())

    def test_known_protocol_bounds_enable_clipped_checks(self):
        data=toy_data();idata=self.posterior(data)
        data['lower_bound']=np.full(len(data['y']),-.8)
        data['upper_bound']=np.full(len(data['y']),.8)
        with patch('analysis.hierarchical.predictive.pm.sample_prior_predictive',return_value=idata):
            table,meta=predictive_checks(data,idata,replicates=10)
        self.assertFalse(meta['latent_only'])
        self.assertIn('censor_rate',set(table.metric))
        self.assertTrue(meta['censor_rate_check_available'])


if __name__=='__main__': unittest.main()
