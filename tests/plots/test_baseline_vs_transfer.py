import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plot_baseline_vs_transfer as p


class TransferTests(unittest.TestCase):
    def test_training_uses_finite_values_and_excludes_flag_one(self):
        df = pd.DataFrame({'strength_value': [1., 2., 3., np.nan, np.inf],
            'strength_outlier': [1, 0, 0, 0, 0],
            'strength_status': ['scored', 'unresolved', 'not_requested', 'scored', 'scored'],
            'strength_valid': [1, 0, 0, 1, 1], 'needs_review': 1})
        self.assertEqual(p.extract_clean_series(df, 'strength_value', 'strength_outlier',
                                               is_training=True).tolist(), [2., 3.])

    def test_publication_size_and_no_statistics_overlay(self):
        records=[]
        for task in ('both','strength','angle'):
            for i in range(10):
                r={'subject':f'{i:02d}', 'group':'both', 'task':task}
                for ch in ('strength','angle'):
                    r['baseline_'+ch+'_mean']=float(i-5)
                    r['transfer_'+ch+'_mean']=float(i-4 + (i % 3)*.3)
                records.append(r)
        figures=[]
        def inspect(fig, *args, **kwargs):
            self.assertTrue(np.allclose(fig.get_size_inches()*25.4,[180,170]))
            for ax in fig.axes:
                self.assertAlmostEqual(ax.get_xlim()[0],-ax.get_xlim()[1])
                self.assertFalse(any('mean change' in t.get_text() for t in ax.texts))
            figures.append(fig)
        with patch.object(plt.Figure, 'savefig', inspect):
            p.plot_overview_figure(pd.DataFrame(records), [p.PRIMARY_MEASURES[0],p.PRIMARY_MEASURES[2]],
                                  'Test',Path('unused'))
        self.assertEqual(len(figures),2)

    def test_channel_validity_is_independent(self):
        df = pd.DataFrame({'angle_value': [1., 2., 3., np.inf],
            'angle_status': ['scored', 'unresolved', 'scored', 'scored'],
            'angle_valid': [1, 1, 1, 1], 'score_complete': [0, 1, 1, 1],
            'angle_outlier': [1, 0, 0, 0], 'angle_needs_review': [1, 0, 0, 0]})
        self.assertEqual(p.extract_clean_series(df, 'angle_value', 'angle_outlier').tolist(), [1., 3.])

    def test_main_and_inset_use_same_joint_location_and_complete_pairs(self):
        rng = np.random.default_rng(23)
        pairs = rng.normal(size=(10, 2))
        pairs[-1] = [22, -17]
        df = pd.DataFrame(pairs, columns=['baseline_angle_mean', 'transfer_angle_mean'])
        df.loc[10] = [1, np.inf]
        df.loc[11] = [np.nan, 1]
        df['subject'] = [f'{i:02d}' for i in range(1, 13)]
        df['group'] = 'both'
        fig, ax = plt.subplots()
        self.addCleanup(plt.close, fig)
        records = p.draw_paired_scatter_panel(ax, df, 'angle_mean', 'Angle', 'deg', False,
                                              ['both'], 'Test')
        record, = records
        self.assertEqual(record['n_pairs'], 10)
        self.assertEqual(record['participants'], ','.join(df.subject[:10]))
        center = [record['baseline_location'], record['transfer_location']]
        self.assertFalse(np.allclose(center, pairs.mean(axis=0)))
        inset, = ax.child_axes
        for panel in (ax, inset):
            np.testing.assert_array_equal(panel.collections[0].get_offsets(), pairs)
            marker, = [line for line in panel.lines if line.get_gid() == 'population-both']
            np.testing.assert_allclose(np.asarray(marker.get_data()).ravel(), center)

    def test_robust_moments_keep_raw_sensitivity(self):
        rng = np.random.default_rng(17)
        y = np.r_[rng.normal(0, .2, 39), 25.]
        result = p.compute_stage_metrics(pd.DataFrame({'angle_value': y}))
        self.assertEqual(result['n_angle'], 40)
        self.assertTrue(result['angle_fit_success'])
        self.assertAlmostEqual(result['raw_angle_variance'], np.var(y, ddof=1))
        self.assertLess(abs(result['angle_mean']), abs(result['raw_angle_mean']))
        self.assertLess(result['angle_variance'], result['raw_angle_variance'])

    def test_variance_axis_preserves_all_points(self):
        df = pd.DataFrame({'subject': ['01', '02', '03'], 'group': ['both']*3,
            'baseline_angle_variance': [0., .2, 281.],
            'transfer_angle_variance': [.1, .4, 40.]})
        fig, ax = plt.subplots()
        p.draw_paired_scatter_panel(ax, df, 'angle_variance', 'Variance', 'deg²', True, ['both'], 'Test')
        self.assertEqual(ax.get_xscale(), 'symlog')
        self.assertEqual(len(ax.collections[0].get_offsets()), 3)
        self.assertGreater(ax.get_xlim()[1], 281)
        plt.close(fig)


if __name__ == '__main__':
    unittest.main()
