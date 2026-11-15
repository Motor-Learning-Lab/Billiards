# Investigation and corrections following supervisor feedback (2026-11-02)

## Problems identified

1. The first three figures came from learning_curve_tool/component_figures.py. The old version still connected 10-shot means and sample SDs; the outlier tool's OLS spline was not integrated into the learning figures.
2. A t-test of externally studentized residuals is not a Student-t likelihood for trial observations. The old method also did not separately fit practice-dependent means and variances.
3. Step four's actual script was plot_baseline_vs_transfer.py in the root. The old version included some values with unresolved status, using different eligibility rules from learning figures.
4. Angle variance is vulnerable to extremes in short baseline samples. Old angle-only baseline sample variances were 281.49 for 05, 110.87 for 02, and 96.49 deg² for 19; wide linear ranges compressed the main point cloud.
5. Clear score-capping evidence exists for 269 valid strength values: 158 training, 50 baseline, and 61 post-test. No angle censoring meeting the evidence criteria was found. Capped values cannot be treated as exact observations at the upper bound.

## Implemented

- Student-t likelihood with fixed nu=5; a 5-dimensional spline for training mean, 3-dimensional spline for log-scale, and second-difference smoothing penalty 1.
- Separate variance display, scale²×5/3. Blue shading and stage error bars represent model SD, not confidence intervals for means.
- Historical outlier labels remain unchanged, while the new robust model retains valid extreme observations and uses a heavy-tailed likelihood to reduce their influence on trends. Unscored/invalid measurements are excluded per channel; review flags no longer exclude observations.
- Capping is jointly established by value, maximum, and uncapped. The likelihood uses exact boundaries and CDF/survival probabilities. uncapped is a motion-model prediction of the stopping point, not a measured true stop.
- Baseline/post-test each use a constant Student-t mean/variance over the full stage, rather than dividing 30 shots into three volatile 10-shot summaries.
- Group variance plots use zero-preserving logarithmic coordinates and show every point. Angle learning plots use labeled symlog coordinates when needed to retain signed extremes and the main point cloud.
- Raw sample moments and block descriptions remain in CSV/JSON for checking. The old OLS outlier batch remains a historical diagnostic, not the new primary analysis.

## Verification and evidence

- All 30 participants were redrawn; 40 training-channel and 240 baseline/post-test-channel fits succeeded.
- 42 tests passed (27 learning-figure, 12 model/outlier/censor, 3 group-figure tests). SHA-256 hashes for 210 source CSVs match the pre-edit values.
- Held-out interpolation checks: mean negative log likelihood over 200 interleaved folds was 1.054 for the new model versus 1.413 for a constant-variance Gaussian with the same mean spline. Across 199 successful contiguous-block comparison folds, values were 1.102 versus 1.504. One contiguous-block comparison failed and was excluded from the mean. Lower is better; folds and observations are not independent. This is neither future forecasting nor a significance test.
- The comparison simultaneously changes heavy tails, variable variance, and penalization; all improvement cannot be attributed to the t distribution. Sensitivity results for nu=4/5/8 and penalties 0.3/1/3 are stored in robust_validation.json; defaults were not tuned to between-group effects.

## Outputs and use

- learning_curves/01.png through 30.png, alongside SVG and statistics JSON.
- baseline_vs_transfer_robust/fig1_primary_measures_baseline_vs_transfer.png/pdf.
- tools/outlier_batch/run_robust_analysis.bat redraws both sets. The original learning-curve desktop entry remains usable.

## Interpretation limits

Smoother curves do not mean raw noise has been deleted or prove training effects. Fixed nu, short baselines, the censoring model, and residual correlation affect results. Group SEM does not propagate stage-fit uncertainty; exploratory paired tests in CSV are unadjusted for multiple comparisons and are not confirmatory conclusions. Formal effect inference requires a separately designed hierarchical/repeated-measures model and uncertainty analysis.

## Method sources

- Robust Student-t observation model: https://mc-stan.org/docs/2_20/stan-users-guide/robust-noise-models.html
- True-censoring CDF/tail-probability likelihood: https://mc-stan.org/docs/stan-users-guide/censored-data.html
- Student-t density, CDF, and scale: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html
