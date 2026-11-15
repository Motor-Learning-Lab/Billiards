# Three core figures: execution and results

Run by double-clicking run_publication_figures.bat in D:/experiment, or execute:

```powershell
python plot_publication_figures.py --root D:/experiment --out D:/experiment/publication_figures
```

Dependency installation on another computer: `python -m pip install -r requirements_publication.txt`. The main entry calls publication_raincloud.py and publication_phase_space.py in the same directory; keep these three files together. Inputs are read only; the default output is publication_figures. The code has no path that writes back to source CSVs.

## Verified limitations and handling

- group_assignments.json includes 01–60; this task uses only 01–30, with 10 participants per group.
- Training strictly requires status=scored and outlier!=1. Original shot positions define 14 windows of 10 shots; retained observations are not regrouped after exclusions. SEM for partial blocks uses actual participant counts.
- Groups train different measures, so angle (deg) and strength cannot be directly averaged. Figure2 therefore uses training measures normalized by each participant's matched-task baseline RMS; Both averages its two normalized channels with equal weights. It compares relative changes in the respective trained tasks, not between-group efficacy on a common raw endpoint. All raw-unit channel values are separately exported to CSV.
- Figure3 has no Strength records in the Angle-only task and no Angle records in the Strength-only task. Both cells explicitly say Not measured; no zero imputation or invented sets of 10 points.
- Figure4 uses each participant's signed mean from jointly valid both-task trials. Each axis is divided by the SD of all baseline participant means (without subtracting the mean, preserving target 0). Ellipses are 95% normal-reference covariance contours of participant means, not 95% CIs of group means or within-person trial noise. Baseline 10 versus approximately 30 post-test trials yields different precision of means, which can also affect area changes.

## Actual results

All 12 Tukey HSD comparisons across the four measured transfer panels are n.s.; group-specific transfer cannot be claimed as established. The four Holm-adjusted ANOVA p-values are 0.661, 0.247, 1, and 1. Raw statistics and Levene diagnostics are in figure3_statistics.csv.

The Strength and Angle groups' Figure2 SD decay rates cannot be reliably identified within the observed 14 blocks. Legends explicitly indicate this; extreme tau returned by the numerical optimizer is not interpreted as a learning rate. All fit parameters and numerical diagnostics are in figure2_decay_fits.csv.

The following are actual Figure4 descriptive statistics. Variance ratio=Post/Pre; <1 means a decrease, >1 an increase.

| Group | Ellipse area change | Angle variance ratio | Strength variance ratio | Baseline centroid distance to target | Post-test centroid distance to target |
|---|---:|---:|---:|---:|---:|
|both|-48.35%|0.209|0.944|0.288|0.311|
|strength|-77.21%|0.462|0.115|0.804|0.148|
|angle|-55.47%|0.177|0.291|0.609|0.499|

All three areas decrease, but Both barely contracts along strength, while Angle contracts in both directions. The figure does not establish the proposed mechanism “Both in both directions, Strength only Y, Angle only X.” All centroid/area calculations use actual data, without enforcing the hypothesis.

## Verification

10 tests passed; 30 participants, 40 training channels, and 420 participant×block summaries. Every measured Figure3 panel contains 10 independent individual changes per group. PNG dimensions are 3600×1500, 4500×2700, and 4500×1500 at 300 DPI. PDFs are 12×5, 15×9, and 15×5 inches, with embedded fonts and no raster-image objects. SHA-256 hashes of 211 read inputs (180 baseline/test CSVs, 30 labeled training CSVs, and group JSON) are unchanged before/after execution. Source data were neither copied into backups nor modified.

Captions and formula explanations are in METHODS.md, figure3_caption.txt, and fig4_phase_space_caption.txt. Submission must still follow the target journal's physical layout and statistical reporting requirements; publication-quality export does not establish a hypothesis.
