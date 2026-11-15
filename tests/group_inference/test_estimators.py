import unittest
import numpy as np
import pandas as pd
from common.group_inference_data import eligible
from analysis.group_estimators.sensitivity import holm,compare_estimators

class EstimatorTests(unittest.TestCase):
    def test_flags_validity_and_missingness(self):
        d=pd.DataFrame({"angle_value":[1,2,3,4,np.nan],"angle_status":["scored"]*5,"angle_valid":[1,1,0,1,1],"angle_outlier":[0,1,0,0,0]})
        self.assertEqual(eligible(d,"angle").tolist(),[True,False,False,True,False])
    def test_holm_accounts_for_full_finite_family(self):
        np.testing.assert_allclose(holm([.01,.04,.03,np.nan])[:3],[.03,.06,.06])
    def test_paired_bootstrap_preserves_constant_shift_and_distinguishes_medians(self):
        rows=[]
        for g,shift in [("both",2),("strength",4),("angle",6)]:
            for i in range(10):
                for stage,v in [("baseline",float(i)),("test",float(i)+shift)]:
                    rows.append(dict(participant=str(i)+g,group=g,task="both",channel="angle",stage=stage,location=v,variance=v+1,mae=v+1))
        p,c,pairs=compare_estimators(pd.DataFrame(rows),resamples=300)
        q=p[p.group=="both"]
        np.testing.assert_allclose(q.change,2);np.testing.assert_allclose(q.change_low,2);np.testing.assert_allclose(q.change_high,2)
        np.testing.assert_allclose(c[(c.group_a=="both")&(c.group_b=="strength")].difference_in_changes,-2)
        self.assertEqual(len(pairs),30)
