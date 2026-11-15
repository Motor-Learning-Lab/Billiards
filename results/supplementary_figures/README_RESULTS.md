# Supplementary figures: questions for further study

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
BCa bootstrap uses 9999 resamples and seed 20261108. Form individual paired changes first, then resample participants; groups are resampled independently. Shots are never treated as independent participants.
Implementation reference: [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).
The method column explicitly records the interval algorithm used for degenerate distributions. Intervals are not estimated with fewer than 3 participants.

MSE = signed_mean² + population_variance, where population_variance = sample_SD² × (n−1)/n.
component_statistics.csv also reports the finite-sample sensitivity decomposition: (signed_mean² − sample_SD²/n) + sample_SD².
The latter corrects sampling bias in the squared mean but assumes independent identically distributed observations within a stage; squared-bias estimates can be negative and are not truncated to zero.

## Current paired MAE results (original units)
| Task/channel | Group | n | Mean change | 95% BCa CI |
|---|---|---:|---:|---|
|both/strength|both|10|-0.101|[-0.196, 0.088]|
|both/strength|strength|10|-0.231|[-0.318, -0.158]|
|both/strength|angle|10|-0.134|[-0.211, -0.052]|
|strength/strength|both|10|-0.106|[-0.175, -0.031]|
|strength/strength|strength|10|-0.187|[-0.257, -0.116]|
|strength/strength|angle|10|-0.068|[-0.118, -0.032]|
|both/angle|both|10|-0.663|[-1.801, -0.015]|
|both/angle|strength|10|-1.020|[-2.047, -0.382]|
|both/angle|angle|10|-0.835|[-1.655, -0.239]|
|angle/angle|both|10|-0.887|[-1.844, -0.240]|
|angle/angle|strength|10|-1.492|[-2.558, -0.417]|
|angle/angle|angle|10|-0.784|[-3.261, 0.287]|

## Current finding most worth further testing

The Angle group's empirical variance change in the angle-only task is 6.84 deg², with 95% interval [-11.76, 52.48].
Its mean squared-bias change is -7.86 deg²; total MSE change is -1.02 deg².
This suggests that reductions in bias and variability need not coincide, but the interval is wide and does not establish increased variance.
Of 12 direct group contrasts, 10 exploratory 95% intervals cross zero. The remaining intervals are also unadjusted for multiplicity and must not replace the original Tukey results or be selected as confirmatory findings.
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
