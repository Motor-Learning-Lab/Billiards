# Candidate hierarchical baseline/post-test model

Each endpoint is fitted separately to trial-level signed measurements. Existing MLE methods remain separate. Input y is physical-unit value or proven signed censor boundary; normalize only by input scale, without centering. Censor codes -1/0/+1 use CDF/density/survival likelihood through PyMC Censored. Uncapped model predictions are never actual responses.

Group baseline/change location and logscale have shared weak Normal hyperpriors and non-centered group deviations. Participant random baseline/change location and logscale are independent non-centered Normals, with SDs shared across groups. No random-effect correlations are estimated. The exact prior scales are specified in model.build_model; all scales refer to normalized responses or logscale units. Fixed Student-t nu=5 is an assumption.

Population group_location is expected signed location. Population group_within_variance integrates participant lognormal scales: physical_scale^2 * 5/3 * exp(2*group_logscale + 2*(sd_v0^2 + stage*sd_vdelta^2)). It excludes between-person location variance and is neither SEM nor t scale squared. This expectation can have a long posterior upper tail; accompany its mean with median and full intervals.

Posterior changes are test minus baseline; pairwise contrasts are change(A)-change(B). group_log_variance_ratio compares multiplicative variance change. Negative signed location change is not necessarily movement toward zero. 95% intervals are equal-tailed posterior credible intervals. prob_less_zero is posterior probability, not a p-value or multiplicity-adjusted test. These independent endpoint models do not establish confirmatory multivariate effects.

Defaults are four NUTS chains, 1000 tuning +1000 retained draws, target_accept .99 and max tree depth12. NUMBA is optional and supported by the installed graph; errors are not silently downgraded to approximate inference. Windows callers must use a main guard for multiprocessing. Diagnostics use unrounded rank Rhat, bulk/tail ESS and divergences across all hierarchy variables. sampling_adequate requires4chains, max Rhat<=1.01, minimumESS>=400, minimumBFMI>=.3,0maximum-tree-depth hits and0divergences; this is only computational adequacy, not scientific acceptance.

Interfaces: build_model(data); sample_endpoint(data,draws,tune,chains,cores,seed,target_accept,compile_mode); summarize_posterior(idata). Full posterior retains group_location, group_within_variance, group_location_change, group_variance_change, group_log_variance_ratio and participant/hyperparameters. run_endpoint runs an audited NPZ endpoint and writes posterior.nc and summary CSV/JSON.

predictive.predictive_checks returns prior/posterior predictive mean, SD, fifth/ninety-fifth percentiles and censor-rate checks by group/stage. Bounds must describe every trial under the scoring protocol. If censoring exists but only observed censor event codes are supplied, these checks report unavailable; inventing limits from events would yield circular censor-rate checks.

Implementation verification: unit tests compare true censor likelihood with SciPy and verify finite model gradients, target-preserving units, pairing, and the integrated variance formula. Short toy MCMC is a smoke test, not parameter recovery or formal convergence.

References: https://www.pymc.io/projects/docs/en/stable/api/distributions/censored.html and https://www.pymc.io/projects/docs/en/stable/api/generated/pymc.sample.html . Installed PyMC5.20.0 / ArviZ0.20.0.

Actual sampling settings are saved in each posterior InferenceData sampling_settings attribute; they override documentation defaults. Failed-quality attempts are retained under attempt subdirectories and are not replaced silently. Conditional trial errors are exchangeable within stage; serial dependence is not modeled.

### Equivalent computational parameterization
The independent group deviations contain a common component redundant with the overall mean. The implementation integrates that component and uses G-1 orthonormal zero-sum Helmert contrasts: conditional on group SD tau, the sampled grand mean has SD sqrt(prior_sd^2+tau^2/G). The group-vector covariance remains prior_sd^2 J+tau^2 I exactly. Thus the prior and likelihood on scientific group parameters are unchanged; the discarded auxiliary direction is not a scientific estimand. A covariance identity test and real-data gradient/sampling checks verify this change. Recommended production settings are four sequential chains,1500retained draws,2000tuning iterations,target_accept=.995; consult each exported sampling_settings for the actual run.

The current181-file source audit identifies0proven censored observations across the four endpoints (counts1125,1150,1196,1191). This means no tail-likelihood terms are active in this run; it does not certify complete upstream censor metadata. Historical censor counts describe older inputs and must not be carried forward.
