> Follow-up update, 2026-11-02: the current primary analysis is `run_robust_analysis.bat` (Student-t likelihood, separate mean/variance fits, true censoring). The OLS/Bonferroni batch description below remains applicable to the historical outlier-labeling tool, but the new learning/transfer figures no longer hard-delete these labels. See TASK_STATE.md for the latest overall status, and CENSOR_AUDIT.md and robust_validation.md for methodological evidence.

# Billiard motor-learning experiment: Outlier Batch Tool handoff

> **Purpose:** help the next engineer or language model (such as GPT) quickly understand the design context, architecture, data flow, statistical principles, completed verification, and possible extensions.

---

## 1. Project and experimental context

This project automatically detects and labels statistical outliers in sequential time-series data from a **billiard motor-learning experiment (140 shots per participant)**.

- **Root:** `D:\experiment`
- **Participants:** `01` through `30`, each with a separate numbered directory.
- **Three training modes:**
  1. `training_both_140shots`: combined angle and strength training.
  2. `training_angle_140shots`: angle-only training.
  3. `training_strength_140shots`: strength-only training.
- **Related systems:**
  - Upstream extraction stores cleaned shot data in each participant's `processed_csv/` directory.
  - Downstream visualization: `D:\experiment\learning_curve_tool\learning_curves.py`. Its learning-curve script reads labeled CSVs from this tool's `outlier_results/labeled_csv/` and excludes outlier=1 points from plotting calculations by setting them to NaN.

---

## 2. Files and execution

Source code and batch launchers reside in `D:\experiment\tools\outlier_batch\`:

```text
D:\experiment\tools\outlier_batch\
├── run.bat              # Windows double-click launcher; detects/builds a venv and runs
├── outlier_batch.py     # Core statistical detection and batch program
├── requirements.txt     # Python dependencies
├── README.md            # Tool documentation (English)
├── HANDOFF.md           # This handoff
└── logs\                # Automatically timestamped batch logs
```

### Execution

1. Double-click `run.bat`, or run:

   ```cmd
   cd D:\experiment\tools\outlier_batch
   python outlier_batch.py [participant input]
   ```

The program recursively scans each participant's `processed_csv/`, including `processed_csv/csv/`. Training-mode keywords identify files; filename prefixes are accepted. Fields are accessed by column name.

2. Supported input:
   - One participant: `01` or `1`.
   - Several participants: `01,02,05`.
   - Range: `01-30`.
   - All participants: `all`, or Enter at the prompt (blank input/EOF defaults to all).

---

## 3. Statistical method and algorithm

The 140 shots contain progressive learning (a nonstationary time series), so a conventional mean/SD-based 3-sigma test cannot be directly applied.

### Detailed steps

1. **Independent channel fits:**
   - Angle (`angle`) and strength (`strength`) are modeled strictly independently; values must not be pooled.
   - An unrequested strength channel in a single-task mode such as `training_angle_140shots` is automatically skipped (0 eligible).
2. **Data quality and eligibility mask:**
   - A point enters the spline fit only if all conditions hold:
     - Channel status: `{channel}_status == 'scored'`.
     - Score complete: `score_complete == 1`.
     - Channel validity: `{channel}_valid == 1`.
     - Retained data were manually reviewed: historical `{channel}_needs_review` and `needs_review` fields are ignored and no longer exclude observations.
     - A valid finite numeric value (not NaN/Inf). A valid 0 can be tested; placeholders for incomplete scores remain excluded.
   - **New requirement, 2026-11-02:** review flags neither affect eligibility nor directly determine outliers. Keep scored, score_complete, valid, and finite-value requirements.
3. **Cubic B-spline learning trend:**
   - Predictor: shot number `shot`.
   - Construct the cubic B-spline basis with `patsy.dmatrix("bs(x, df=df_spline, degree=3, include_intercept=True) - 1")`.
   - Default degrees of freedom $df = 6$; with too few eligible observations, dynamically use $\min(6, n-2)$.
   - Estimate trend $\hat{y}_i$ using `statsmodels.api.OLS`; residual $e_i = y_i - \hat{y}_i$.
4. **Externally studentized residuals:**
   - Compute leverage (hat-matrix diagonal $h_{ii}$).
   - Residual variance after removing observation $i$:

     $$s_{(i)}^2 = \frac{\sum e^2 - \frac{e_i^2}{1 - h_{ii}}}{n - p - 1}$$

   - Externally studentized residual:

     $$t_i = \frac{e_i}{s_{(i)} \sqrt{1 - h_{ii}}}$$

5. **Hypothesis tests and multiple-comparison correction:**
   - Two-sided raw $p$ values from a $t$ distribution with $dof = n - p - 1$:

     $$p_{\text{raw}} = 2 \times (1 - F_t(|t_i|, dof))$$

   - Bonferroni correction, with $m$ the number of eligible tested observations:

     $$p_{\text{adj}} = \min(p_{\text{raw}} \times m, 1.0)$$

   - If $p_{\text{adj}} < 0.05$, mark as a statistical outlier candidate (`1`); otherwise mark normal (`0`).
6. **Assumption diagnostics:**
   - Residual normality: Shapiro-Wilk test, warning when $p < 0.05$.
   - Heteroscedasticity: Breusch-Pagan test.
   - Autocorrelation: Durbin-Watson statistic, warning outside $1.5 \sim 2.5$.
   - All diagnostics are recorded in statistical reports.

---

## 4. Outputs and file rules

Participant `ID` outputs are saved in `D:\experiment\{ID}\outlier_results\`:

```text
D:\experiment\{ID}\outlier_results\
├── labeled_csv\
│   └── {original_filename}_outlier_labeled.csv  # CSV with added outlier flags
├── reports\
│   ├── {original_filename}_report.txt           # Detailed per-file test/diagnostic report
│   └── participant_{ID}_summary.txt             # Participant summary across files
└── plots\
    ├── {original_filename}_angle_outliers.png   # Angle fit and labeled outlier scatter
    └── {original_filename}_strength_outliers.png # Strength fit and labeled outlier scatter
```

### Mandatory format rules

1. **Protect original files absolutely:**
   - Do not modify, overwrite, or delete originals under `processed_csv/`. The program verifies original-file integrity using SHA-256 before and after each run.
   - Do not create unauthorized backup copies of source CSVs on disk.
2. **Column positions and names:**
   - Insert `strength_outlier` immediately after `strength_value`.
   - Insert `angle_outlier` immediately after `angle_value`.
   - Do not change original column names or existing values, or delete rows.
3. **Flag values:**
   - `1`: statistical outlier candidate with Bonferroni-corrected $t$-test $p < 0.05$.
   - `0`: not flagged, including nonsignificant tests, unrequested channels, no valid measurement, too few eligible points, or uncomputable tests. A zero must not universally be interpreted as tested normal.
   - **No blank flags:** every row of `strength_outlier` and `angle_outlier` must contain integer `0` or `1`. Reports retain reasons for skipping.
   - **Excel/encoding compatibility:** write CSV as `utf-8-sig` with BOM to avoid garbled Chinese text in Excel. Original empty cells remain empty; never write the string `"nan"`. Flag columns have no missing values. Original columns are read as text, preserving cell contents exactly.
4. **Row-count preservation:**
   - The new CSV must retain exactly the original row count: typically 140, but some participants have 136, 138, or 139 because of hardware frame loss.

---

## 5. Historical verification before modification (not current results)

As of 2026-11-02, full runs and comprehensive tests for all 30 participants `01`–`30` had completed with **30/30 Success, 0 Errors**.

### Historical detected-outlier distribution

- **Angle:** 1–4 outlier shots in 13 participants: 01, 02, 04, 07, 10, 11, 13, 17, 20, 21, 23, 26, 29.
- **Strength:** 1 outlier in participant 12; 0 in the others.
- **Unrequested/untestable channels:** strength in single-task angle mode was correctly identified as 0 eligible and left entirely blank. Participant 19 had only 7 valid strength points (<15), so was correctly skipped and left blank.
- **Automated assertions:**
  - All 30 new CSV row counts match original CSVs.
  - Adjacent column-position checks pass.
  - Flags strictly belong to `{'', '0', '1'}`.
  - Source-file hashes are completely unchanged.

---

For current verification and work status, consult this directory's sole handoff-state entry, `TASK_STATE.md`. The historical counts and blank-flag behavior above have been superseded by new requirements.

## 6. Possible future changes for the next engineer/GPT

Choose future improvements according to research needs.

### A. Detection sensitivity and multiple-comparison correction

- **Current status:** highly conservative Bonferroni correction ($\alpha_{\text{Bonf}} = 0.05 / 140 \approx 0.000357$), with only 1 detected strength outlier.
- **Options:**
  - To increase sensitivity, introduce **FDR (False Discovery Rate, Benjamini-Hochberg)** by adding a `method="fdr_bh"` option in `_fit_channel()`, using `statsmodels.stats.multitest.multipletests` if appropriate.
  - Allow significance level $\alpha$ in CLI/configuration, e.g. $\alpha = 0.01, 0.05, 0.10$.

### B. Spline degrees of freedom and learning-trend fitting

- **Current status:** cubic B-spline with fixed 6 degrees of freedom ($df = 6$).
- **Options:**
  - Adaptive degrees-of-freedom selection by **AIC/BIC** or **cross-validation**, balancing underfitting and overfitting.
  - Compare boundary leverage for natural cubic splines and B-splines over shots 1–5 and the final 5 shots.

### C. Figure styling and customization

- **Current status:** 200 dpi PNG with gray points, blue trend, red outliers, and red shot-number labels. Needs review categories and orange diamonds have been removed.
- **Options:**
  - Add envelopes at $\pm 2$ or $\pm 3$ SD (Prediction Band / Confidence Envelope).
  - Support English/Chinese legends or journal formats, including vector PDF/SVG export.

### D. All-participant master summary

- **Current status:** each participant has a separate summary in `reports/participant_{ID}_summary.txt`.
- **Option:** after processing all participants, automatically create `all_participants_outliers_summary.xlsx` or `.csv` under `D:\experiment\tools\outlier_batch\` or a specified path, summarizing all 30 participants' outlier counts, rates, and early/middle/late-stage distributions.

---

## 7. GPT prompt template

The following historical template can be supplied when handing over changes:

```text
You are taking over the billiard motor-learning experiment's outlier batch tool (D:\experiment\tools\outlier_batch\).
Read the architecture and constraints in D:\experiment\tools\outlier_batch\HANDOFF.md carefully.

Mandatory rules:
1. Original CSVs in D:\experiment\{ID}\processed_csv\ are read-only source data. Never modify, overwrite, or delete them, and do not create backup-copy directories.
2. This workspace is not a Git repository; do not commit or reset with Git.
3. Flag columns must be strength_outlier and angle_outlier, immediately after the respective measurement columns, with values strictly 1 or 0. No blanks or "nan".
4. Preserve utf-8-sig encoding and all original rows.

Requested change:
[Enter the specific request, e.g. replace Bonferroni with FDR-BH or generate a global summary table for all 30 participants.]
```
