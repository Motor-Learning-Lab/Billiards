"""Additional paired estimation and error decomposition figures; sources read-only.

Run python plot_supplementary_analyses.py. Reuses the audited publication loader.
All uncertainty resamples participants, never treats shots as independent people.
"""
from pathlib import Path
import argparse
import hashlib
import json
import warnings

import numpy as np
import pandas as pd
from scipy.stats import bootstrap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from common.publication_data import load_data, GROUPS, COLORS
from common.paths import PARTICIPANT_ROOT, output_path
import matplotlib.pyplot as plt

from plots.supplementary.schema import ENDPOINTS, CONTRASTS
from plots.supplementary.statistics import paired_metrics, bootstrap_mean, summarize
from plots.supplementary.style import save_figure, interval, format_axes, match_row_limits
from plots.supplementary.paired_effects import draw_estimation
from plots.supplementary.group_contrasts import draw_contrasts
from plots.supplementary.decomposition import draw_decomposition




















def write_readme(out, within, contrasts, components, seed, resamples):
    rows = []
    for _, r in within.iterrows():
        rows.append(f'|{r.task}/{r.channel}|{r.group}|{r.n}|{r.estimate:.3f}|[{r.low:.3f}, {r.high:.3f}]|')
    angle = components[(components.task=='angle') & (components.channel=='angle') & (components.group=='angle')].set_index('component')
    variance = angle.loc['variance']
    contrast_crossing = int(((contrasts.low <= 0) & (contrasts.high >= 0)).sum())
    text = f'''# Supplementary figures: questions for further study

Run `run_supplementary_analyses.bat` in the root, or `python plot_supplementary_analyses.py`.
Options include `--root`, `--out`, `--seed`, and `--resamples`. Dependencies remain in `requirements_publication.txt`.

## Three worthwhile questions

1. Figure 5: How large is each group's change, how consistent are individuals, and how precise is the estimate? Individual MAE changes and 95% intervals for group means complement the original raincloud significance tests.
2. Figure 6: Does improvement reflect reduced mean aiming bias or reduced trial variability? Exactly decompose the same person's observed MSE rather than mixing both mechanisms in MAE.
3. Figure 7: Does combined training yield greater transfer than single-task training? Estimate differences in changes directly between groups. “Significant in one group but not another” is not a between-group comparison.

## Data and methods

Reuse the actual-source loader from plot_publication_figures.py; IDs 01–30 form three groups of 10.
These new figures analyze only baseline/test from processed_csv. Training reading/verification retains the strict scored AND outlier!=1 rule, but training does not enter these three figures' statistics.
Each channel includes only finite, scored observations; outlier=1 is excluded when that field exists. Unmeasured channels are not zero-imputed. Calculations use actual rows per person/stage; each participant has equal weight within a group.
All tables are written as utf-8-sig to a separate output directory; no source CSV or label is modified.
BCa bootstrap uses {resamples} resamples and seed {seed}. Form individual paired changes first, then resample participants; groups are resampled independently. Shots are never treated as independent participants.
Implementation reference: [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).
The method column explicitly records the interval algorithm used for degenerate distributions. Intervals are not estimated with fewer than 3 participants.

MSE = signed_mean² + population_variance, where population_variance = sample_SD² × (n−1)/n.
component_statistics.csv also reports the finite-sample sensitivity decomposition: (signed_mean² − sample_SD²/n) + sample_SD².
The latter corrects sampling bias in the squared mean but assumes independent identically distributed observations within a stage; squared-bias estimates can be negative and are not truncated to zero.

## Current paired MAE results (original units)
| Task/channel | Group | n | Mean change | 95% BCa CI |
|---|---|---:|---:|---|
{chr(10).join(rows)}

## Current finding most worth further testing

The Angle group's empirical variance change in the angle-only task is {variance.estimate:.2f} deg², with 95% interval [{variance.low:.2f}, {variance.high:.2f}].
Its mean squared-bias change is {angle.loc['bias_squared','estimate']:.2f} deg²; total MSE change is {angle.loc['mse','estimate']:.2f} deg².
This suggests that reductions in bias and variability need not coincide, but the interval is wide and does not establish increased variance.
Of 12 direct group contrasts, {contrast_crossing} exploratory 95% intervals cross zero. The remaining intervals are also unadjusted for multiplicity and must not replace the original Tukey results or be selected as confirmatory findings.
Exact values are in group_contrast_statistics.csv and component_statistics.csv.

## Interpretation limits

- Intervals are exploratory, pointwise, and unadjusted for multiple comparisons. They cannot replace Figure3 Tukey tests or support selective reporting of significant findings.
- An interval crossing zero indicates uncertainty in direction/magnitude, not proof of no difference or equivalence.
- Each group contains only 10 participants. Bootstrap cannot create information; extreme participants affect MSE and intervals. Valid extreme observations are not deleted to smooth figures.
- Approximately 10 baseline versus 30 post-test trials give different mean precision. Consult the finite-sample sensitivity table; do not interpret all reduction in empirical squared bias as bias learning.
- Strength is capped. These figures describe recorded scores, do not recover unobserved tails, and do not replace the existing Student-t/true-censoring model.
- Within-stage variance may include systematic drift, fatigue, and measurement error; it cannot simply be called “pure internal motor noise.”
- There is no untrained control group; within-group pre/post changes alone cannot exclude repeated-testing effects.

For further mechanism research, prioritize a group×stage model with a common endpoint, and repeated baseline/delayed retention tests.
Covariance-ellipse shrinkage in these data cannot directly establish decoupled strength/angle control; simple baseline-versus-change correlations are also unsuitable as proof of learning potential.
'''
    (out/'README_RESULTS.md').write_text(text, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=PARTICIPANT_ROOT)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--seed', type=int, default=20261108)
    parser.add_argument('--resamples', type=int, default=9999)
    args = parser.parse_args()
    if args.resamples < 1000:
        parser.error('--resamples must be at least 1000')
    root = args.root.resolve()
    out = (args.out or output_path(root, 'supplementary_figures')).resolve()
    # Derived output must not enter participant source trees.
    if any(out == root/f'{i:02d}' or root/f'{i:02d}' in out.parents for i in range(1,31)):
        parser.error('Output must be outside participant folders')
    stages, _, _, _, hashes = load_data(root)
    paired = paired_metrics(stages)
    within, contrasts, components = summarize(paired, args.seed, args.resamples)
    out.mkdir(parents=True, exist_ok=True)
    for name, table in [('participant_paired_metrics', paired), ('paired_effect_statistics', within),
                        ('group_contrast_statistics', contrasts), ('component_statistics', components)]:
        table.to_csv(out/(name+'.csv'), index=False, encoding='utf-8-sig', na_rep='')
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10, 'pdf.fonttype':42,
                         'axes.spines.top':False, 'axes.spines.right':False, 'savefig.dpi':300})
    draw_estimation(paired, within, out)
    draw_decomposition(components, out)
    draw_contrasts(contrasts, out)
    write_readme(out, within, contrasts, components, args.seed, args.resamples)
    changed = [p for p, digest in hashes.items() if hashlib.sha256(Path(p).read_bytes()).hexdigest() != digest]
    if changed:
        raise RuntimeError(f'Inputs changed during execution: {changed}')
    (out/'source_hashes.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')
    manifest = dict(seed=args.seed, resamples=args.resamples, confidence_level=.95,
                    input_files_unchanged=len(hashes), participants=int(paired.participant.nunique()),
                    paired_endpoints=len(paired), eligible_mae=int(paired.eligible_mae.sum()),
                    eligible_decomposition=int(paired.eligible_decomposition.sum()))
    (out/'run_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))
    print(f'Figures and tables saved: {out}')


if __name__ == '__main__':
    main()
