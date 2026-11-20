# Group points, estimator sensitivity and hierarchical inference

## What the existing scatterplot represents
The robust baseline-transfer plot is a two-stage analysis. A small point is one participant, with baseline on x and immediate post-test on y. For signed-location panels, each coordinate is the fitted constant Student-t location, with nu=5 and documented censoring. For variance panels it is the fitted scale squared times 5/3. For MAE it is the arithmetic mean absolute recorded error, not the latent expected absolute error. These three estimands must not be interchanged.
In the three robust overview figures, each large black-edged point is the location of a bivariate Student-t fit to one training group's paired participant coordinates (5 degrees of freedom and an unrestricted scatter matrix). Both coordinates of a participant receive the same likelihood weight. The fit uses the original units for signed location, variance and MAE, including on panels with logarithmic display scales. The figures show point estimates. The arithmetic means and marginal SEMs used in the earlier figures remain in the companion statistics tables. The paired t and Wilcoxon tests address within-group changes. See [the figure methods](../../results/baseline_vs_transfer_robust/METHODS.txt) and [the fitted locations](../../results/baseline_vs_transfer_robust/population_points.csv).

## New estimator sensitivity
`analysis/group_estimators/sensitivity.py` compares arithmetic mean, median and 20%-trimmed mean of the SAME participant stage estimates. Each group has ten participants. Baseline/post rows are resampled together, independently across groups, using9999percentile bootstrap replicates (seed20261114). Pointwise95% intervals concern the selected estimator. They are not posterior intervals and are not multiplicity adjusted.
The group change is estimator(post)-estimator(baseline). For a nonlinear estimator this is not generally estimator(post-baseline); both are exported explicitly. Direct group effects are change(A)-change(B). Mean-change contrasts also have Welch p-values and Holm adjustment over the full36comparison family (four endpoints x three metrics x three group pairs), plus Hedges g based on participant change-score SD. Median/trimmed contrasts do not inherit those mean-based p-values. Do not choose an estimator because its interval excludes zero. A KDE mode is not a default: with n=10 it is sensitive to bandwidth, ties and multiple peaks; median and trimmed mean provide more reproducible robustness checks.

## New Bayesian model
`analysis/hierarchical/model.py` fits each of four measured endpoints independently at the trial level. All retained baseline/post observations are jointly modeled with t5 likelihood. Group-level baseline/location change and baseline/logscale change have shared weakly informative hyperpriors. Participant baseline and change deviations use non-centered normal random effects, with shared SDs across groups. Baseline and change random effects are assumed independent; no unidentifiable unrestricted random-effect correlation matrix is fitted. Full equations and prior scales are in the model source and its README.
Units are divided by pooled observed baseline RMS for computation, without centering; zero remains the target. The scale is an empirical normalization constant, not another posterior parameter. Outputs restore physical units. Fixed nu=5 gives finite variance. Exact observations contribute density; documented left/right caps contribute CDF/survival probability. Uncapped extrapolations are never treated as observed scores.
Group location is a population-level parameter rather than an average of separately fitted participant locations. Group within-person variance integrates over the lognormal participant scale distribution: scale_unit^2*(5/3)*exp(2*group_logscale+2*random_logscale_variance). It excludes variation in participant means. The posterior tables give mean, median and equal-tailed95%credible intervals; figures use the posterior median with marginal intervals, not SEM.
Direct posterior contrasts compare location changes, expected within-person variance changes and log(post/pre variance ratios) between groups. P(A-B<0) is a posterior directional probability conditional on this model and priors, not a p-value or a multiplicity-adjusted discovery probability. Signed-location decreases do not necessarily represent improvement: closeness to zero matters. Variance reductions concern modeled trial variation, which can include drift/measurement effects, not proven internal motor noise.

## Eligibility and source contract
`common/group_inference_data.py` reads only processed baseline/test sources, uses original group_assignments.json IDs01-30, checks training filename/group agreement, requires finite scored observations, valid=1 when present, and excludes exactly outlier=1 whenever present. The old robust plot is not silently changed; its historical baseline/test rule ignores outlier flags. This new explicit flag exclusion is documented, not an unexplained change of estimand. Training is not included in these baseline/post fits. Duplicate stage/task sources are rejected. Actual counts are retained; no padding or imputation. Each endpoint requires at least five valid observations per participant stage.

## Running
From the repository root:
```powershell
python -m plots.group_inference.run
python -m plots.group_inference.run --bayesian --draws 1500 --tune 2000 --cores 1
python -m plots.group_inference.run --bayesian --endpoint both_strength
python -m plots.group_inference.posterior_figures
```
Install `requirements_hierarchical.txt` in the analysis environment for Bayesian runs. Existing frequentist pipelines remain available. Default output is results/group_inference. CSVs use UTF-8 BOM. Input SHA256 checks guard read-only source use. Full posterior NetCDF files retain chain/draw samples locally and are excluded from Git because trial log-likelihood arrays are large. Compact group posterior draws, checksums and diagnostics are versioned. All sampling settings are exported.

## Diagnostics and limitations
Four chains, rank-normalized Rhat<=1.01, bulk/tail ESS>=400 zero divergences, BFMI>=0.3 and no maximum-tree-depth hits are the recorded convergence checks. Short toy runs only test execution. Diagnostics apply to latent and hyperparameters, not just polished group summaries. Inspect prior and posterior predictive behavior as well. In capped endpoints, full pre-specified per-trial measurement bounds are not established for every trial; selected uncensored observations cannot be treated as an unbiased latent predictive sample or used to claim an observed censor-rate check. Predictive metadata states this limitation.
With three groups of ten, hierarchical hyperparameters and expected variances can remain weakly identified. Group differences are observational comparisons within this experimental assignment, not proof of a specific neural mechanism. No untrained control or delayed retention inference is supplied. Four endpoint models are separate; posterior intervals are not simultaneous across endpoints. Primary-analysis choice and researcher understanding remain pending, even when tests and diagnostics pass.

## Reference documentation
- [PyMC censored likelihood](https://www.pymc.io/projects/docs/en/v5.16.0/api/distributions/censored.html)
- [PyMC Student-t](https://www.pymc.io/projects/docs/en/stable/api/distributions/generated/pymc.StudentT.html)
- [Rank-normalized Rhat and ESS](https://sites.stat.columbia.edu/gelman/research/published/Vehtari_etal_2020_rhat_ess.pdf)

### Equivalent computational parameterization
The independent group deviations contain a common component redundant with the overall mean. The implementation integrates that component and uses G-1 orthonormal zero-sum Helmert contrasts: conditional on group SD tau, the sampled grand mean has SD sqrt(prior_sd^2+tau^2/G). The group-vector covariance remains prior_sd^2 J+tau^2 I exactly. Thus the prior and likelihood on scientific group parameters are unchanged; the discarded auxiliary direction is not a scientific estimand. A covariance identity test and real-data gradient/sampling checks verify this change. Recommended production settings are four sequential chains,1500retained draws,2000tuning iterations,target_accept=.995; consult each exported sampling_settings for the actual run.

The current181-file source audit identifies0proven censored observations across the four endpoints (counts1125,1150,1196,1191). This means no tail-likelihood terms are active in this run; it does not certify complete upstream censor metadata. Historical censor counts describe older inputs and must not be carried forward.


## Model equations and prior scales
For participant i in group g, let s=0 for baseline and s=1 for test. With physical normalization k, the latent response follows

`y_is / k ~ StudentT(nu=5, mu_g0 + u_i0 + s*(delta_mu_g + u_id), exp(l_g0 + v_i0 + s*(delta_l_g + v_id)))`.

Each group parameter vector has the original conditional prior `theta_g | m,tau ~ Normal(m,tau)`, with `m ~ Normal(a,b)` and `tau ~ HalfNormal(h)`. The orthogonal implementation integrates the redundant common deviation without changing this distribution.

| Parameter | a | b | h |
|---|---:|---:|---:|
| Baseline location | 0 | 1.5 | 0.75 |
| Location change | 0 | 0.75 | 0.5 |
| Baseline log scale | log(0.5) | 0.75 | 0.5 |
| Log scale change | 0 | 0.5 | 0.35 |

Participant deviations are independent zero-mean Normal variables. Their SD priors are HalfNormal(0.75), HalfNormal(0.5), HalfNormal(0.5), and HalfNormal(0.35), respectively for u_i0, u_id, v_i0, v_id. Trials are conditionally exchangeable within each stage. The group expected within-person variance at stage s is `k^2 * 5/3 * exp(2*(l_g0+s*delta_l_g) + 2*(sd_v0^2+s*sd_vid^2))`. This population expectation differs from both the variance of participant means and the variance of all pooled trials.

## Output files and interpretation
- `stage_estimates.csv`: one participant/task/channel/stage per row, with constant-t location/variance and observed MAE.
- `selection_audit.csv`: actual included/excluded trial counts and censor metadata audit; no trial count is padded.
- `participant_pairs.csv`: paired participant baseline/test summaries.
- `estimator_group_points.csv`: alternative group estimators and paired bootstrap intervals.
- `estimator_group_contrasts.csv`: direct changes, percentile intervals, and mean-only Welch/Holm/Hedges g.
- `bayes/<endpoint>/group_stages.csv`: population location and expected within-person variance, posterior mean/median/95% interval.
- `within_group_changes.csv` and `between_group_contrasts.csv`: posterior changes and direct group differences, including P(value<0).
- `diagnostic_table.csv`, `diagnostics.json`: all latent/hyperparameter sampling checks.
- `predictive_checks.csv`, `predictive_metadata.json`: prior and posterior design-matched checks; these intervals concern replicated statistics, not effect uncertainty.
- `group_posterior.npz`: compact group posterior draws, with chain and draw axes retained.
- `posterior_manifest.json`: exact model/settings, endpoint-array digest, source-snapshot digest and local full-trace checksum.
- `posterior.nc`: full local trace, excluded from Git. Source CSVs are never outputs.

PNG files use 300 DPI; PDF files retain vector graphics. Variance scatter axes use a symmetric-log display to retain zero without dropping extreme values. Intervals stay in physical squared units; axis transformation is not a log-variance estimand. The log-variance-ratio contrast is a separate estimand. Standalone posterior plotting rejects mixed source snapshots. A single-endpoint run does not automatically combine its results with old endpoints.


## Final four-endpoint result and display update
All four final endpoint runs pass sampling checks with zero divergences. Predictive discrepancies remain, especially for angle-only responses; see the versioned results/group_inference/README_RESULTS.md for the complete table and effect caveats. This is a candidate analysis, not accepted primary evidence. Focused figures now separate metrics and estimators in 2 x 2 layouts, with full-range insets whenever the main participant cloud is magnified. No measurements or computed estimates are moved. Posterior variance panels use positive log axes over all credible interval endpoints; sensitivity variance panels retain symmetric-log axes.
