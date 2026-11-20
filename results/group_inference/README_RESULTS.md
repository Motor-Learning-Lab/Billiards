# Group inference: current results

These results describe the current 181-file source snapshot. They are exploratory; scientific acceptance remains pending.

## Sampling and predictive checks

| Endpoint | Trials | Max Rhat | Min bulk ESS | Min tail ESS | Divergences | Posterior summaries within 95% predictive intervals |
|---|---:|---:|---:|---:|---:|---:|
| both_strength | 1125 | 1.00704 | 609 | 725 | 0 | 23/24 |
| strength_strength | 1150 | 1.00353 | 1052 | 887 | 0 | 22/24 |
| both_angle | 1196 | 1.00301 | 2091 | 2848 | 0 | 21/24 |
| angle_angle | 1191 | 1.00394 | 1779 | 1791 | 0 | 18/24 |

Four sequential chains per endpoint, 2,000 tuning iterations and 1,500 retained draws per chain, target_accept=0.995. All four endpoints pass the recorded computational criteria. There are zero proven censored events in the current inputs; no active censor-tail contributions occur. This does not establish complete upstream censor metadata.

Predictive diagnostics compare replicated group/stage mean, SD and fifth/ninety-fifth percentiles with observed values. These are descriptive checks, not calibrated goodness-of-fit tests. In particular, the angle-only endpoint has six of 24 observed summaries outside the posterior predictive intervals, including test SD in the Angle group (observed 4.265 degrees versus predicted interval 1.369 to 2.192). The fixed symmetric t5 model does not fully reproduce this distribution. Do not interpret convergence as model adequacy or remove observations to improve this diagnostic.

## Direct group differences

None of the 36 mean-change Welch comparisons survives the global Holm correction at 0.05. This is not evidence of equivalence. Median and 20%-trimmed-mean sensitivity results have participant-paired, pointwise percentile bootstrap intervals, not adjusted p-values.

Of 36 Bayesian pairwise contrasts, 35 equal-tailed 95% intervals include zero. The Strength-minus-Angle location-change contrast in the strength-only task has posterior median -0.1960 strength units, interval [-0.3975, -0.0010], and P(difference<0)=0.9767. Its upper limit is close to zero. It is a model-conditional exploratory result, not a multiplicity-adjusted discovery, and a signed-location decrease does not automatically mean improved accuracy. The posterior contrasts concern location change, expected within-person variance change, and log variance ratio; they are not MAE contrasts.

## Less crowded figures

### Bivariate Student-t centers in the scatterplots

The nine focused figures and the estimator sensitivity overview show each training group's bivariate Student-t location as an open diamond. In these plots, the filled estimator markers and their bootstrap crosshairs retain the meaning given by the filename or legend. Three dedicated figures show only the centers on linear axes: `bivariate_t_location`, `bivariate_t_variance` and `bivariate_t_mae` (PNG/PDF). The overview and focused variance panels use a symmetric-log display. All fits use the original measurement units.

Each location comes from a separate full-scatter, fixed-df=5 fit to the paired baseline/post-test participant coordinates in this directory's `participant_pairs.csv`. There are 36 fits of ten participants each (four task/channel combinations, three metrics and three training groups). Each participant's joint squared Mahalanobis distance determines a common weight for both stages. These fits condition on the individual stage estimates. The diamonds show point estimates.

Run `python -m plots.group_inference.bivariate_figures` from the repository root to rebuild these 13 figures and both numerical exports from the saved inputs. `bivariate_t_group_points.csv` records the center, scatter, sample size, IDs and fit status. Multiplying each coordinate in `bivariate_t_participant_weights.csv` by its normalized weight and summing within the panel and training group recovers the corresponding center. For example, the Both training group's Both-task strength MAE center is (0.520969, 0.303691). The [Wiki figure guide](https://github.com/Motor-Learning-Lab/Billiards/wiki/Figure-Group-Inference-Bivariate-Centers) follows this example from the individual trials to the open diamond.

The focused_<metric>_<estimator>.png/.pdf files split each metric and estimator into its own 2 x 2 figure, avoiding nine overlapping group crosshairs per panel. Main views use the 90th percentile of absolute participant coordinates or the largest group interval boundary, whichever is larger, with 8% padding. If the full range is more than 1.4 times that view, a full-range inset retains every participant and a rectangle marks the zoomed region. The count outside the main view is labeled. No point is jittered or deleted. Variance sensitivity figures retain symmetric-log axes.

hierarchical_group_points.png/.pdf shows posterior medians and marginal 95% credible intervals. Its strictly positive variance panels use log axes bounded by the complete interval range, avoiding empty zero-to-tail space. hierarchical_group_effects.png/.pdf shows direct contrasts and directional probabilities. All PNGs are 300 DPI; PDFs retain vectors.

## Reproducibility and limits

### Hierarchical variance scatterplot

`hierarchical_variance_scatter.png` and its vector PDF show individual paired stage variances and the group-level expected within-participant variance. Each small marker uses one participant's separate Student-t stage fits. Each large marker uses the median of the hierarchical group's marginal posterior at baseline (x) and post-test (y). Horizontal and vertical bars span the corresponding 2.5th and 97.5th posterior percentiles. The 12 group points and limits are in `hierarchical_variance_scatter.csv`. Both axes use logarithmic scales with matched limits across the two tasks for a given channel.

For the Both training group on Both-task strength, the baseline posterior median is 0.456 (95% credible interval 0.294–0.707) and the post-test median is 0.182 (0.123–0.290), in squared strength units. The point summarizes expected trial-to-trial variation within a person drawn from the group. The model integrates over differences in participant scales. The plotted intervals describe the two stage parameters separately; posterior draws of their paired difference are the appropriate source for inference about change. The angle-only posterior predictive limitation above also applies to this figure.

Run `python -m plots.group_inference.posterior_figures --variance-only` to regenerate it from `participant_pairs.csv` and the four saved `bayes/<endpoint>/group_stages.csv` tables, with no resampling.

Use `python -m plots.group_inference.run --bayesian` for a fresh complete analysis. Use `python -m plots.group_inference.focused_figures` or `python -m plots.group_inference.posterior_figures` to redraw saved summaries without MCMC. Source CSVs and videos remain unchanged. Full posterior.nc files stay local; compact group draws, settings, diagnostics and checksums are versioned. Earlier failed sampling attempts are preserved in attempt folders and are not the final results.

Full regression: 68 tests passed; the added mixed-source plot regression passed separately (69 distinct tests). The finalized CLI was exercised without rerunning MCMC. A single simulated recovery dataset covered all six known locations and five of six variances; this is not a calibration study. Fixed nu, shared random-effect SDs, independent baseline/change deviations, empirical baseline-RMS normalization and conditional within-stage exchangeability remain assumptions. Prior sensitivity, serial dependence, asymmetric tails and primary-method selection remain scientific review topics under Issue #2.
