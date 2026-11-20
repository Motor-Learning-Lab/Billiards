> Current resume entry: [Handoff 2026-11-21](#handoff-2026-11-21). Earlier sections are historical.

# Original Goal
Remove Needs review exclusion/display from the outlier batch tool because retained data have already been reviewed. Both outlier columns must always be 0 or 1.

## Requirements
Read-only processed_csv; no source backups; no Git operations. Preserve original cells, rows, UTF-8 BOM and adjacent strength_outlier/angle_outlier columns.

## Constraints
Keep channels independent and existing cubic spline, externally studentized residuals and Bonferroni thresholds. Keep scored, score_complete, valid and finite-value eligibility checks.

## Current Plan
Complete: implementation, regression checks, all-participant regeneration and integrity verification.

## Architecture / Important Decisions
Historical channel-specific and generic review flags are ignored. They are preserved unchanged in exported original columns. Eligible reviewed observations now participate in fitting. Only statistically significant results get 1; all other rows get 0, including skipped/undefined tests. Reports document that 0 does not imply successful testing. Plot ineligible category remains for other eligibility failures; Needs review category is removed. Original cell text is read separately for export to avoid numeric reformatting.

## Completed Work
Changed eligibility, binary output defaults, plotting and reporting. Regenerated CSVs, reports and plots for participants 01–30 on 2026-11-02. No source backups created.

## Files Changed
outlier_batch.py, README.md, HANDOFF.md; added test_outlier_batch.py, AGENTS.md, TASK_STATE.md. Derived files refreshed under each participant's outlier_results. Verification evidence under logs.

## Tests / Verification Performed
- Three unittest cases passed: review-flag invariance and known injected outlier detection; invalid/skipped channel binary defaults; CSV preservation, BOM, adjacency and absence of review legend.
- All-participant batch: 30 successes, 0 errors (logs/outlier_batch_20261102_154739.log; logs/binary_flags_rerun.txt).
- All 210 processed_csv SHA-256 hashes unchanged (logs/source_integrity_before.json contains hashes only, no source copies).
- 30 output CSVs, 4193 rows, 28 flags equal to 1 across both channels. Verified every original cell and row against sources, both flag columns strictly 0/1 and adjacent, BOM present (logs/binary_flags_verification.txt).
- Visually inspected regenerated participant 03 strength figure: review category absent, trend and remaining ineligible category rendered correctly.

## Known Issues
Unrequested/invalid/unscored rows remain untested and receive 0 by the requested binary convention. Reports retain eligibility counts and skipped reasons. Old detection counts in HANDOFF section 5 are explicitly historical.

## Remaining Work
None for this request.

## Recommended Next Step
Use run.bat as before for subsequent batches. Do not rerun unrelated filename/data migrations.

## Important Context for Next Session
This workspace is not a Git repository. Verify actual files and source hashes directly. HANDOFF.md holds architecture; this file is the sole current task-state document for outlier_batch. The learning-curve application's handoff is separate and was not changed.

## Follow-up: launcher input and nested discovery (2026-11-02)
- User reported `No input provided. Exiting.`. Code inspection confirmed this was the blank-input branch, before file discovery.
- Empty input or EOF now selects all participants; explicit participant selections remain supported. run.bat continues calling the same Python entry point unchanged.
- Discovery now recurses under processed_csv, supporting nested csv directories and prefixed filenames.
- Read all 30 actual training CSV schemas before the change: three training modes, 60–90 columns. Current sources are directly under processed_csv; field lookup is by name.
- Five unittest cases passed, including new nested discovery and blank/EOF default tests; existing reviewed-data/binary-output tests still pass.
- No actual desktop double-click verification performed. Input dispatch tested with mocks; no need to regenerate unchanged statistical results for this discovery/input-only change.
- Follow-up complete; original completed goal remains intact.

## New Original Goal: supervisor feedback / robust learning and transfer (2026-11-02)
Implement Student-t observation likelihood, separate smooth mean/variance, evidence-based true censor likelihood, and readable baseline/post-test plots; diagnose old noisy ten-trial summaries without altering sources or deleting observations to create effects.

## Requirements / Constraints
Retain signed values, original 210 processed CSVs, row counts and independent channels. Historical binary flags remain 0/1 and unchanged but are no longer automatic deletions in the new robust analysis. Fixed nu=5 and smoothing penalty=1 are disclosed assumptions, not effect-driven tuning. Unresolved/invalid channels excluded independently; generic score_complete is only fallback if channel status absent.

## Current Plan / Completed Work
New robust_model.py implements penalized Student-t mean/log-scale splines and constant stage fits; censoring.py uses value/maximum/uncapped evidence and exact signed bounds. learning_curve_tool now renders spline mean, separately modelled variance, full-stage t baseline/test mean +/- model SD. Old arithmetic block summaries retained in JSON. Root plot_baseline_vs_transfer.py uses consistent t stage fits and zero-safe log variance axes, retains raw moments in CSV. Historical outlier flags remain visible but valid extremes participate in robust likelihood. New run_robust_analysis.bat regenerates both output sets. No reset-card operation was performed; no such tool is available in this session.

## Architecture / Important Decisions
Shared model and censor helpers live here. Statistical fitting uses all valid scored observations, including old flagged points. The historical OLS/Bonferroni outlier_batch.py remains available as a diagnostic comparison and its binary CSV contract is unchanged; it does not implement the new primary analysis. Nu=5 gives finite variance scale^2*5/3. Censored strength values come from capped motion-model predictions, not measured final stops; interpretation concerns recorded scores. Mean uncertainty is not the plotted model SD. These are descriptive participant fits, not confirmatory treatment-effect inference.

## Files Changed
Added robust_model.py, censoring.py, their tests, validate_robust_model.py, CENSOR_AUDIT.md, robust_validation.json/md, run_robust_analysis.bat. Updated learning_curve_tool/learning_curves.py, component_figures.py, start.cmd and regression tests; plot_baseline_vs_transfer.py and root test_baseline_vs_transfer.py. Documentation updated. Outputs learning_curves/01..30.png/svg/statistics, baseline_vs_transfer_robust/PNG/PDF/CSV. No Git repository; no commits/reset or source copies.

## Tests / Verification Performed
27 learning regression tests, 12 outlier/model/censor tests and 3 transfer tests pass. Real batch: 30/30 figures, 40/40 training fits and 240/240 phase fits successful; training censor count 158. Entire source manifest (210 CSVs) unchanged by SHA-256, verified logs/final_robust_verification.txt. Inspected regenerated 04 learning plot and group primary plot. Scientific dependency mismatch resolved by preferring installed complete stack; start.cmd retains GUI entry and prefers system Python with scipy/pandas/matplotlib, because bundled desktop Python lacks scipy. GUI generation is covered by regression test; literal desktop shortcut double-click not manually exercised.

## Known Issues / Remaining Work
No remaining implementation work for current request. Inference limitations: fixed nu/smoothing sensitivity; baseline samples around 10; no propagation of stage-fit uncertainty to group SEM or exploratory CSV paired tests; residual serial dependence not explicitly modelled. Statistical outlier labels in old batch are historical diagnostics, not new model-tail p-values. Do not equate smoother curves or improved predictive fit with proven learning effects. See robust_validation.md for final sensitivity/holdout evidence.

## Recommended Next Step / Important Context
Use run_robust_analysis.bat for all robust figures; existing learning launcher also produces new component figures. Read this latest section before older completed tasks. This file is the sole overall handoff for the robust-analysis task; learning_curve_tool/TASK_STATE.md keeps its application-specific history and links here. Source truth is code/results/tests, not earlier outdated flag-removal descriptions.

Final holdout verification now uses independent channel eligibility consistent with figures: interleaved 200/200 comparisons; blocked 199/200 (one failed comparison excluded and disclosed). Overall report: ROBUST_ANALYSIS_REPORT.md. Obsolete automation-4 removed after completion.

## 2026-11-08 publication and authoritative-label revision (supersedes earlier retention rule)
Original Goal: improve group journal layout and participant plots; exclude user-authoritative training outlier=1 from all statistics and fits. Requirements: source CSV read-only, actual trial counts, labeled training only, no y=0 fabricated outlier positions, no empty censor panel, external captions and precise SD label.
Completed: learning app updated and all30 regenerated; group plot split into two180x170mm2x2 figures plus MAE with insets, signed symmetric shared limits, external three-rule statistics. Core change excerpts and full evidence: ../../baseline_vs_transfer_robust/CORE_CHANGES.md and REVISION_REPORT.md. Source code plot_baseline_vs_transfer.py, test_baseline_vs_transfer.py, learning_curve_tool/learning_curves.py/component_figures.py/verify_outputs.py and tests. Shared statistical model unchanged.
Verification: 27learning+5group tests pass; all40 training fits successful with correct retained counts; independent verification280 source metrics; all240CSV hashes unchanged vs logs/plot_revision_20261108_sources.json. Source audit CSV logs/training_source_audit_20261108.csv. PNG/PDF physically sized and inspected, captions exported. No Git repository.
Remaining: none for this request. Prior robust validation used different inclusion rules and is historical. Existing inference limitations persist. App-specific current handoff remains learning_curve_tool/TASK_STATE.md. Do not restore earlier flagged-data retention policy. Use new fig1a/fig1b outputs rather than preserved tall historical plots.

## 2026-11-08 new three-figure pipeline (separate from previous plotting revisions)
Original Goal: produce Figures2 learning/variability,3 transfer raincloud ANOVA/Tukey,4 joint phase-space for30 participants. Latest new-pipeline selection rule: status=scored AND outlier!=1; this supersedes the earlier all-finite rule for this new entry point. Existing earlier plotting programs were not rewritten in this task.
Requirements: group_assignments.json IDs01-30 authoritative,180baseline/test processed files and30labeled training files; no source writes; OkabeIto specified colors; requested physical dimensions and300DPI/vectorPDF.
Architecture: new root plot_publication_figures.py loads audited data and drawsFigure2; publication_raincloud.py drawsFigure3; publication_phase_space.py drawsFigure4. Different training units require matched-task baseline-RMS normalization andBoth equal component weighting. Missing cross-task modalities remain explicitly unmeasured. Figure4 uses jointly valid participant signed means normalized by pooled baseline participant SD, covariance distribution contours, not mean confidence intervals. Data do not get forced to confirm decoupling.
Completed Work / Files Changed: three new Python modules, three test modules, requirements_publication.txt, run_publication_figures.bat; outputs in publication_figures/ with input hashes,raw summaries,statistics,captions,METHODS.md andREADME_RESULTS.md. No existing source CSV modified. No Git repository.
Tests / Verification:10tests pass; actual full CLI completes;30participants(groups10each),40trainingchannels,420participant-block summaries. PNG dimensions/DPI andPDF physical sizes checked;PDF embedded-font objects present andno raster image objects. All211read-input hashes unchanged. All3plots visually checked.
Known Issues: twoFigure3cells not measured, all12Tukeypair testsn.s.; fixed single-exponential rate forStrength/Angle SDnot identifiable; normalized indices across different trained tasks aredescriptive. Across-participant mean ellipses cannot provewithin-person motor-noise decoupling;baseline/post averagingcounts differ. SeeREADME_RESULTS.mdforactual hypothesis check. Oldvalidation reports apply toolder rules.
Remaining Work: none for this implementation/export request. Recommended Next Step: run run_publication_figures.bat orpython plot_publication_figures.py; interpret withMETHODS.md. This issole overall task-state entry; existing app handoff still belongs tolearning_curve_tool/TASK_STATE.md.

## 2026-11-08 supplementary research figures (current completed request)

### Original Goal
Recommend scientifically useful additional figures based on existing results and implement a working batch program.

### Requirements / Constraints
Preserve all source CSVs, authoritative groups and existing outputs; no Git repository or Git operations. Use 01-30 and actual stage counts. Reuse the current publication data selection; no deleted valid extremes or manufactured significance. English figures, 300 DPI PNG and vector PDF; Chinese interpretation and one-click BAT.

### Current Plan
Implementation and verification complete. Supplement existing Figures2-4 with paired estimation, observed error decomposition, and direct group contrasts.

### Architecture / Important Decisions
Root plot_supplementary_analyses.py imports audited load_data from plot_publication_figures.py. The new statistics use baseline/test processed_csv only. Loader also audits training with scored AND outlier!=1; training does not contribute to these supplementary endpoints. Four measured task/channel combinations only. Participant pairing is by ID, never by row order. Each person has equal group weight. Figure5: individual MAE changes plus group mean 95% BCa CI. Figure6: exact empirical MSE = signed_mean^2 + population variance (ddof=0), with separate finite-n sensitivity partition (mean^2-s^2/n)+s^2 in CSV. Figure7: independent-group differences of participant paired MAE changes. Bootstrap uses9999resamples, seed20261108, sampling participants rather than trials. Pointwise exploratory intervals are explicitly not multiplicity/Tukey-adjusted; do not override earlier adjusted tests. Shared x limits within same-unit rows of Figures5/7; Figure6 panel scales explicitly differ.

### Completed Work / Files Changed
Added plot_supplementary_analyses.py, run_supplementary_analyses.bat, test_supplementary_analyses.py, verify_supplementary_analyses.py. Root AGENTS.md points here. Outputs supplementary_figures/: Figures5-7 PNG/PDF/captions, participant_paired_metrics.csv, paired_effect_statistics.csv, component_statistics.csv, group_contrast_statistics.csv, README_RESULTS.md, source_hashes.json, run_manifest.json and verification.json. Dependencies use existing requirements_publication.txt; verifier uses Pillow already supplied with Matplotlib dependencies.

### Tests / Verification Performed
5new numerical/pairing/bootstrap tests plus10existing publication tests pass(15total). Real batch completes:30participants,120paired endpoints, all120eligible for both MAE/decomposition. Independent verifier reads actual source CSVs and checks240stage summaries against direct MAE/MSE/variance/squared-mean calculations; both decomposition identities checked across120pairs. All211input SHA256 hashes unchanged and equal previous publication-run manifest. All3PNG3600x2400 at300DPI; PDF font embedding found with no raster image objects; derivedCSVutf-8-sig. All3figures visually inspected; initial left-label crowding fixed and Figures5/7 re-inspected. BAT invokes tested CLI; no literal desktop double-click test.

### Known Issues
Exploratory uncertainty with10people/group, no simultaneous confidence coverage.12direct group contrasts:10pointwise intervals cross0; remaining2are unadjusted and cannot be promoted over previousTukeyresults. Angle group's angle-only observed variance change estimate+6.84deg^2 has wide95%CI[-11.76,52.48]; observed bias^2 decreases7.86, totalMSE decreases1.02. This is a hypothesis-generating dissociation, not established variance increase. Finite-n correction assumes independent identically distributed stage trials and can yield negative squared-bias estimates; retained without clipping. Observed capped scores remain capped, not inferred latent scores. Stage variance includes drift and measurement error; cannot label it pure motor noise. No untrained control or delayed retention conclusions.

### Remaining Work
None for this requested batch implementation and export. Mechanistic/mixed-model inference or collecting repeated baseline/retention measurements is future research, not an unimplemented requirement of this batch.

### Recommended Next Step / Important Context for Next Session
Run run_supplementary_analyses.bat; read supplementary_figures/README_RESULTS.md with the figures. Use verify_supplementary_analyses.py for independent source/artifact audit. This file remains the unique overall handoff; do not replace older source selections in other applications merely because this supplemental entry reuses the newest publication loader.

## 2026-11-12 — HILD adoption and current research progress (read first)

### Original Goal
The overarching scientific goal remains the supervisor's five steps: finish preliminary processing; retain signed angle/strength with separate mean and variance; decide on Student-t/outlier/true-censoring treatment; compare baseline and transfer; fit learning splines with separate mean and variance. The current user request is to install HILD and begin managing progress. It does not authorize a new statistical redesign in this session.

### Requirements / Constraints
Participant source CSVs are read-only, no source backup folders, no Git initialization/commit/reset, no repeat filename migration. Preserve prior outputs and established handoffs. Separate implemented code, verified results, scientific acceptance and researcher-confirmed understanding. Do not mark research complete just because figure exports or HILD installation are complete.

### Current Plan
HILD local installation is complete and in use for orientation/journaling. The next **proposed**, not yet authorized, scientific scope is to agree on the primary analysis and its eligibility/censoring rules, then identify precisely which figures are descriptive supplements. Existing authorized figure-production tasks remain completed; this broader interpretation question remains open.

### Architecture / Important Decisions
See [HILD local configuration](../../HILD/LOCAL.md). The existing file you are reading remains the sole overall plan/current-state authority; [HILD/plan.md](../../HILD/plan.md) only links here. Application-specific history remains in [learning-curve TASK_STATE](../../learning_curve_tool/TASK_STATE.md). HILD journals live under [HILD/journal](../../HILD/journal/2026-11-12.md). There is no wiki or GitHub tracker. Local setup was requested by the user, but no separate scope-issue review, decision acceptance or understanding confirmation is inferred.

### Completed Work / Files Changed
Installed seven upstream skills under `.agents/skills/hild-*/` using the skill-installer helper. Installed reusable HILD process, templates and scripts pinned to [ab419eed1b50b0ea4fc639890edced0f5f4a01c9](https://github.com/Motor-Learning-Lab/HILD/tree/ab419eed1b50b0ea4fc639890edced0f5f4a01c9); [installation.json](../../HILD/installation.json) records original hashes. Added [LOCAL.md](../../HILD/LOCAL.md), a plan pointer, [local installation scope](../../HILD/scopes/0001-adopt-hild.md), decision-directory guidance and first journal. Appended a HILD pointer to root [AGENTS.md](../../AGENTS.md); preserved its prior rules. HILD README has one local-adaptation notice. No scientific program or data changed.

### Tests / Verification Performed
Upstream read-only verifier: `python HILD/scripts/install_hild.py --target D:/experiment --verify` verifies all27recorded upstream files. The README notice is an intentional local change against its preserved upstream hash. All seven skill files and required links are present.211analysis input hashes match the prior publication/supplementary manifest; no source change detected. `.git` remains absent. Scientific test suites were not rerun for a documentation/skill installation; previous test counts above remain dated historical evidence. `hild-integrate`, `hild-orient` and `hild-journal` were explicitly read and used. Automatic fresh-session skill discovery and hook behavior are unverified; no hooks were installed or claimed to run.

### Current Scientific Progress

| Workstream | Implementation / evidence | What remains unresolved |
|---|---|---|
| Preliminary processing and provenance | Actual source directories, flexible filenames, counts and groups audited; source hashes retained | Full upstream measurement validity is not newly established by plotting audits |
| Signed mean and variance | Present in [robust_model.py](robust_model.py), [component_figures.py](../../learning_curve_tool/component_figures.py), and [group comparison script](../../plot_baseline_vs_transfer.py) | Researcher confirmation of interpretation has not been recorded |
| Student-t and true censoring | Location/scale likelihood and censor helpers implemented; see [censor audit](CENSOR_AUDIT.md) | Final primary strategy and consistent selection across entry points still need explicit agreement |
| Baseline vs transfer | Robust group figures and descriptive Figures3-7 generated; historical verification above | Descriptive MAE/bootstrap outputs and robust latent/model summaries must not be presented as one uniform method |
| Learning curves | Per-participant Student-t mean/log-scale splines implemented; Figure2 separately uses10-shot normalized block summaries plus exponential least-squares fitting | Figure2 is not the supervisor's requested trial-level Student-t spline analysis; final primary figure choice remains open |

### Known Issues / Understanding Debt
1. The researcher asked which method was actually used. [Publication METHODS](../../publication_figures/METHODS.md) and [supplementary README](../../supplementary_figures/README_RESULTS.md) describe observed-score arithmetic summaries/Bootstrap, while the earlier robust app uses Student-t likelihood. Treat explaining this distinction as pending researcher review, not established understanding.
2. Current entry points do not have identical training eligibility: the robust learning app's labeled-training path uses finite nonflagged data, while the new publication loader additionally requires channel status=scored. Do not silently change either policy during HILD setup. A future unification needs a bounded scientific decision and matching validation.
3. SD, SEM, confidence intervals and participant covariance ellipses describe different quantities. Figures and captions have explicit labels; understanding has not been confirmed.
4. Recorded censoring, baseline/post sample-size differences, small groups and exploratory multiple comparisons constrain interpretation. Existing smoothness or ellipse contraction cannot prove motor-noise reduction or decoupling.
5. This is a manual local adaptation, not an upstream-supported automatic installation into a clean Git repository. Remote issue/PR review, wiki publication, hooks and Git-backed history are absent. There is no background monitoring service.

### Remaining Work
No remaining installation work for the user's HILD request. Scientific acceptance and pending understanding topics above are not complete and are not automatically authorized for implementation. A fresh session may verify automatic skill discovery; until then use explicit skill paths.

### Recommended Next Step
Present a concise HILD orientation and propose one bounded review: decide which analysis is primary for the supervisor's requirements, using the actual differences above. Before any scientific edits, record the user's intended scope; preserve already authorized routine autonomy.

### Important Context for Next Session
Read root AGENTS, [LOCAL.md](../../HILD/LOCAL.md), this latest section and the latest HILD journal. Use `hild-orient` / `hild-journal`; do not restart installation or rerun outlier labeling. Skills should be available on a subsequent turn, but actual automatic discovery must be observed rather than assumed. Only the researcher can confirm understanding or accept a proposed scientific decision.

## 2026-11-13 — Workspace cleanup and private Billiards migration (current)

### Original Goal / Requirements
Organize the multi-function experiment workspace, remove unnecessary old outputs, preserve every CSV and video, upload code and all CSVs, and manage work through HILD Issues/PR/Wiki. User chose video-local-only and subsequently changed Billiards from public to private. Keep it private. This request explicitly supersedes the earlier no-Git rule; source-data protection remains unchanged.

### Constraints / Important Decisions
No statistical-method changes, no rewritten CSV bytes, no video deletion/upload, no paid storage, no force/reset, no unapproved merge. Keep runtime/provenance dependencies and existing working paths. Functional classification is through existing module/output folders and the new README navigation, not arbitrary moves that break imports, launchers or historical links. Preserve all test/historical CSVs, including 1,437CSV files under `.test_runs`.

### Architecture / Current Plan
Repository: [ayyyeeeee/Billiards](https://github.com/ayyyeeeee/Billiards). Initial main commit555e295 contains overview/templates. Full migration branch `maintenance/organize-workspace`; a PR will present the full content for researcher review. [Issue1](https://github.com/ayyyeeeee/Billiards/issues/1) records the authorized scope. [Issue2](https://github.com/ayyyeeeee/Billiards/issues/2) tracks primary-method agreement, which is not implemented by this migration. [Issue3](https://github.com/ayyyeeeee/Billiards/issues/3) tracks Wiki web availability.

### Completed Work / Files Changed
Inventory:10,033files/42.772GiB, including2,523CSV and210MKV. Removed1,380 superseded preview/bytecode files,74,597,303bytes; specific paths/reasons in [cleanup_report](../../docs/maintenance/cleanup_report.json). Preserved every CSV and video, old migration/checkpoint evidence, logs, and needed `.deps`/`.tcl` locally. Added root README functional categories, ignore rules, CSV byte-preserving attributes, Issue/PR templates, source/video inventory and reproducible conservative cleanup script. Updated AGENTS/HILD configuration for authorized GitHub workflow. Wiki original Home preserved; draft Process-HILD/Guide-Functions/status/sidebar pushed as9230557.

### Tests / Verification Performed
15publication/supplementary unit tests pass. Original2,523CSV SHA256 and210video path/size/mtime checks pass after cleanup. Videos were not re-encoded or rewritten. Git-stage CSV-byte verification runs before commit; result recorded in [migration_verification](../../docs/maintenance/migration_verification.json). CSVs are explicitly force-added even under ignored runtime directories. No video is staged. Original bootstrap main pushed successfully; final migration remote verification is recorded below when complete.

### Known Issues
GitHub API reports private=true and has_wiki=false, despite successful Wiki Git clone/push. Wiki synchronization is verified; web UI feature availability is not. Do not change visibility or buy an account upgrade to bypass this. Browser control failed URL-policy verification during the earlier session; no further browser workaround was used. Scientific method/selection and understanding issues in prior entries remain open. Upstream HILD README/config local modifications are intentional.

### Remaining Work / Recommended Next Step
Migration uploaded and [PR4](https://github.com/ayyyeeeee/Billiards/pull/4) opened for researcher review; no merge performed. Remote recursive tree at commit dfe712f70b0ec0eab703e64d99e23e0c99723f76 is not truncated and contains4,708files, exactly2,523CSV and0videos. This was checked against the GitHub API after successful push. The original data-bearing commit remains available; final bookkeeping commits only update documentation. Wiki remote head92305577c353d1678a9c630ebbe27e2b8e737d71 was pushed successfully, preserving the original Home greeting. Local main/Wiki working trees were clean after their respective data commits. Researcher review/merge remains pending; Wiki website availability requires the account/settings check under Issue3, not further data uploads. Scientific Issue2 is not implemented by this task.

### Important Context for Next Session
Read this section before older no-Git entries. `wiki/` is its own ignored Git clone. No automatic hooks or background monitors are enabled. Never rerun `workspace_cleanup.py --apply` merely to regenerate its historical audit; preserve the original protection manifest and cleanup report. Do not delete any CSV just because it is under a test/backup path.


### 2026-11-14 recovery milestone
The 2026-11-13 final documentation push was prevented by automatic approval-review quota exhaustion; it did not execute. Recovery inspected both unstaged documentation edits and the clean index/Wiki worktree. Remote repository remains private and PR4 open/unmerged. Issue1 now reflects private visibility and completed data upload. This recovery commits the prepared verification record plus the new dated journal; no data or scientific program changed. Remaining external actions are researcher PR review/merge and Wiki web enablement under Issue3.

## 2026-11-14 — Functional separation and comprehensive Wiki (current, in progress)

### Original Goal / Requirements
Review old Issues/PRs; physically separate data, processing methods and plots; explain each method comprehensively in HILD Wiki. User explicitly confirmed PUBLIC repository continuation, superseding earlier private restrictions.
### Constraints
All CSV/video retained; no measurement/label/model change, video upload, destructive Git reset or unapproved merge.
### Current Plan / Architecture / Important Decisions
Branch codex/modularize-research-workflows, scope #5. Data under data/participants, methods under processing and analysis, plots separated by family, shared paths/loader under common, outputs under results. Compatibility root entries preserve launchers. Existing handoffs remain authoritative at original locations. Scientific Issue #2 is retained.
### Completed Work / Files Changed
Physical data/results relocation complete. docs/maintenance/relocation_verification.json maps protected paths. Closed initial completed scope #1 and obsolete private-Wiki question #3 with reasons. New scope #5 records authorization. Source module refactor and detailed Wiki drafts are IN PROGRESS.
### Tests / Verification Performed
Before/after data relocation: 2,523 original CSV SHA256 values unchanged; 210 video size/mtime records unchanged. No video bytes rewritten. Main worktree clean before new branch. Wiki fast-forward synchronization succeeded. API private=false, has_wiki=true.
### Known Issues
Code paths require adaptation following data relocation; WORKSPACE NOT YET VERIFIED RUNNABLE. Do not claim complete. Existing statistical eligibility differences remain deliberately unchanged. Wiki website rendering not inspected.
### Remaining Work / Recommended Next Step
Apply code migration script, run relevant tests and real read-only plotting smoke checks, finish Wiki, commit/push and open replacement PR before closing PR #4. Do not merge.
### Important Context for Next Session
Read actual Git diff and this latest section. Migration script must NOT be rerun after data moved. Original protection manifest is retained; use relocation mapping. All data present, current code integration pending.

### 2026-11-14 verification milestone (supersedes in-progress warning above)
Implementation: physical data/results relocation and package refactor applied. Shared loader in common/publication_data.py; common/paths.py separates data/config/output roots. Participant app, robust comparison, publication figures and supplementary figure methods now live in separate packages; supplementary statistics, paired effects, decomposition and contrasts have distinct modules. Old Python/BAT/desktop entry points remain compatibility bridges. Historical runtime and handoff locations are retained.
Verification: 59 tests pass using `python -m unittest discover -s tests -t . -p "test_*.py"`. Actual all-30 publication, supplementary and robust comparison runs complete; participant01 completes with actual251 rows. Independent supplementary verification checks240stage summaries/120paired endpoints,300DPI/vectorPDF/BOM and211input hashes. Supplementary batch rerun after function-level split completes. Original2523CSV SHA256 and210video size/mtime still match relocation map. No source data rewritten. Figure6 output visually inspected; desktop double-click/GUI not manually exercised.
Important finding: preserved publication outputs have62historical input-hash mismatches against current source. They are retained, not overwritten. Executing the original42b606a publication loader against current relocated data gives EXACTLY the same four dataframes and211hashes as the new loader. Thus historical-output differences do not originate in the path refactor. Evidence: docs/maintenance/refactor_validation.json.
Wiki:11method/figure drafts prepared with formula/filter/input/output/limitations and method distinctions. Drafts describe branch, not mergedmain; understanding/scientific acceptance pending. New code commits, remote PR replacement and Wiki publication remain to be finalized below.

### Final publication and handoff
Implementation and verification complete; researcher merge/understanding/scientific acceptance remain pending. Code commit952ad2831097863cb83951b5bfcb8cf5fdc04d0e pushed. Replacement PR #6 is open, unmerged, mergeable=true/clean. PR #4 closed as superseded while its import history is preserved in #6; #1 completed, #3 obsolete, #2 retained. #5 remains open until review/merge.
Remote recursive tree verified non-truncated:4836files,2546CSV (2523original+23newvalidation),0videos. Staged original CSV bytes independently matched protected hashes; no file>=100MiB. Local source preservation checks remain valid.
Wiki commit46331e1 pushed:11 detailed method/figure pages plus guide/process/navigation and draft status board. Each page links actual functions at exact code commit; concepts describe branch not mergedmain. HILD status checker ran; every page isdraft, no human understanding inferred. Website visual rendering itself remains unverified; Git publication verified.
Known limitations: initial unrestricted git diff --check reported historical CRLF/trailing whitespace in moved material; CSV bytes were intentionally preserved rather than normalized. No scientific changes were introduced to fix historical-input mismatches or eligibility differences. GUI desktop double-click untested; CLI/core tested.
Next step is researcher review of https://github.com/ayyyeeeee/Billiards/pull/6 and https://github.com/ayyyeeeee/Billiards/wiki/Guide-Functions . Do not merge automatically or rerun data migration. Current workspace runs from newdata paths; root compatibility launchers remain usable. Old completed handoff sections above are historical and do not override this status.

## 2026-11-15 — English Markdown and hierarchical group inference (IN PROGRESS)
### Original Goal
Translate all repository/Wiki Markdown into English. Explain individual and group scatter points. Audit/add Bayesian hierarchical group estimates, alternative estimators, and direct between-group effect inference.
### Requirements / Constraints
Issue #7 records explicit user authorization. Preserve all CSV/video and existing analysis outputs. No automatic merge or scientific-acceptance claim. Current branch codex/group-estimators-english-docs depends on unmerged PR #6.
### Current Plan / Architecture
common/group_inference_data.py reads baseline/test scored finite valid observations and excludes any flag=1, validates JSON groups and training filenames. Four measured task/channel endpoints. Existing robust pipeline is unchanged. analysis/group_estimators/sensitivity.py compares mean, median and20%-trimmed mean with paired participant bootstrap; Welch tests on participant changes receive Holm correction across36mean contrasts. analysis/hierarchical/model.py implements a new trial-level t5 censored hierarchical location/logscale model; not yet validated on real data or accepted as primary analysis.
### Completed Work / Files Changed
New read-only loader, estimator analysis, figures and tests exist as untracked files. Actual all30 input loading gives181unique files,240stage summaries, all240constant-t fits successful. Estimator output has108group points/108contrasts under results/group_inference. Three estimator tests passed. Hierarchical model and tests are drafted. English translation scripts are prepared but no Markdown translations have yet been applied in main worktree.
### Tests / Verification Performed
Estimator selection, Holm and paired constant-shift tests pass. Prior59tests have NOT yet been rerun for this scope. Bayesian real-data MCMC, convergence and output validation NOT completed. No new commit/push for this scope.
### Known Issues
Quota interrupted multiple agents. Wiki translation prior bulk replacement was rejected by approval review because substring matching could lose unmatched content; use exact verified replacements. Existing historical output/source mismatch remains recorded in prior section. New Bayesian inference must not be presented as validated until diagnostics are available.
### Remaining Work
Finish all Markdown translations and template outputs; verify Wiki point definitions. Integrate CLI, run full hierarchical model on four endpoints, check diagnostics/priors/predictive behavior, plot posterior group points/effects. Run regression/data-preservation/English audits, publish separate PR and Wiki updates. Keep #2primary strategy unresolved.
### Recommended Next Step / Important Context
Resume actual files, not old completed-refactor status. Current new modules are untracked; outputs already exist and all CSV must be retained. Do not rerun data relocation. Three agents own repository translations, Wiki translations and hierarchical-model tests/sampling respectively. Sampling is not assumed successful.

### 2026-11-15 recovery verification update
English translation now APPLIED:55trackedMarkdown documents plus supplementary README generator; elevenWiki method pages translated, all16Wiki pages have English prose. Literal Chinese filenames remain only as real path references. Agent audits preserved numeric tables, SHA strings, formulas and all Wiki URLs/draft states; generator AST differs only in text constants. No publication yet for this scope.
Implemented CLI plots/group_inference/run.py and plotting modules, optional Bayesian entry, requirements_hierarchical.txt, run_group_inference.bat.65tests passed before twoadditional predictive tests, which separately passed. Actual estimator outputs108group points/108contrasts; none of36mean-change Welch contrasts pass Holm .05. Existing scatter coordinates reproduce to the old CSV six-decimal rounding (maxdifference5e-7), not exactly bitwise because that CSV was rounded.
Known runtime blocker: PyMC5.20 NUMBA cores4 real-data sampling fails with specify_shape AssertionError; no formal posterior exists. Cores1 real-data smoke remained at compilation and was stopped. Agent is simplifying mathematically equivalent indexing and testing standard PyTensor before rerunning. Toy4chains20+20 succeeded but Rhat1.27/ESS18 and is NOT scientific inference. Do not claim Bayesian completion or NUMBA production support.
Remaining: repair and validate sampler, formal real-data posterior/diagnostics/predictive results, posterior figures, updated validation English/data audit, commit/PR/Wiki publication. Source data remain unchanged.

### Sampling repair and publication checkpoint
Wiki English translation and exact individual/group scatter explanations published at618b9b1. All source CSV/video protection rechecked:2523original CSV hashes,210video records and181current input hashes unchanged. New CLI frequentist validation is running in a temporary output directory. Full earlier65-test run plus2predictive tests and4post-reparameterization model tests passed (counts overlap; not an additional71unique tests).
Real MCMC runs now execute after replacing two-dimensional participant/stage advanced indexing with the equivalent per-trial expression. Initial formal4chain runs had divergences; their files are preserved under attempt1/before_orthogonal. A second exactly equivalent reparameterization integrates the redundant common group deviation, using G-1 Helmert contrasts. Conditional group prior covariance is unchanged, proven by numerical identity test. Current4endpoint production runs use1500retained+2000tune per chain, target_accept=.995, cores1; final diagnostics not yet available. No effect claim from failed runs.
Current source audit detects0proven censored observations at all four endpoints. Historical censor counts are not current evidence. Eligible counts:both-strength1125,strength-strength1150,both-angle1196,angle-angle1191. Model censor capability remains tested against SciPy.
Remaining: final sampler diagnostics and predictive checks, posterior plots, compact posterior export, final English/data audit, codePR and updated methodWiki publication. Full posterior.nc remains local under gitignore; every derivedCSV remains preserved.


### 2026-11-15 resumed verification milestone
PR #8 is open against the unmerged organization branch, at checkpoint d710456; Wiki English translation is published at 618b9b1. Neither PR #6 nor #8 is merged. The current request remains authorized.
All 68 regression tests passed in one run, and the newly added mixed-source posterior-plot regression passed separately. The independent read-only audit found no errors in pairing, Holm adjustment, t censor likelihood or integrated group variance; it identified a single-endpoint/old-endpoint mixing risk, now fixed by endpoint source manifests and version checks. Automatic combined posterior plotting now requires all endpoints to be sampled in the current run.
Both strength endpoints completed four chains with zero divergences and adequate sampling diagnostics (maximum Rhat 1.00705 and 1.00353). The angle endpoints are still running in the existing production process; do not launch duplicates. Predictive checks for strength show tail discrepancies (23/24 and 22/24 posterior summaries within pointwise intervals), so computational adequacy must not be presented as complete model fit.
Protection reverified: all 2523 original CSV hashes and 210 video size/mtime records unchanged; all 181 current source hashes match. All four sampling caches exactly match fresh loader arrays. Tracked Markdown English scan has only eight lines containing literal historical Chinese filenames, not untranslated prose. Updated estimator figures visually checked; titles and legends no longer overlap. Remaining: finish angle diagnostics, export posterior figures/results, update and publish final PR/Wiki evidence. No researcher scientific acceptance or understanding is inferred.


### Final analysis and display verification (2026-11-15)
All four endpoints completed four chains x 1500 retained draws with 2000 tuning iterations, target_accept .995, zero divergences. Maximum Rhat 1.00705; minimum bulk/tail ESS 609/725. Posterior exports, compact samples, predictive checks and figures are generated. Predictive checks retain 23/24, 22/24, 21/24 and 18/24 summaries in their pointwise intervals; angle-only SD/tail discrepancies remain a limitation. Of 36 Bayesian contrast intervals, 35 contain zero; the other signed-location contrast barely excludes zero and is not a confirmatory discovery. None of 36 mean-change Welch contrasts passes Holm .05.
User-requested less concentrated figures now separate each metric/estimator into 2x2 panels, with central views and complete-range insets. No point is moved or deleted. Posterior variance axes use the positive full credible-interval range on log scales. Display changes reuse completed results without MCMC. Full regression 68 tests plus one new mixed-source regression passed (69 distinct tests); final posterior rendering and source validation passed. Current 181 input hashes still match. All original 2523 CSV hashes and 210 video records passed protection checks in this completion stage. English method docs/results explain the remaining scientific limitations. Implementation complete; final PR/Wiki publication status follows. Researcher merge, scientific acceptance and understanding remain pending.

Final rendered review: focused MAE, posterior group points and direct contrasts inspected; corrected inset tick placement and posterior row spacing. All nine focused PNG/PDF pairs exist. Implementation and validation are complete; deliverables are submitted through PR #8, with no automatic merge. Remaining scientific acceptance and model-fit limitations are explicit in results/group_inference/README_RESULTS.md.


## Handoff 2026-11-21

This section is the current overall handoff. Earlier entries are historical milestones, including resolved sampler failures and obsolete IN PROGRESS statements. Do not restart finished work from those entries. The participant-app history remains separately at `learning_curve_tool/TASK_STATE.md`; this file is the only overall progress authority.

### Original Goal
Maintain the billiards motor-learning analysis for 30 participants; preserve original data; organize processing, analyses and figures; document methods through HILD/GitHub. The latest completed implementation translates Markdown to English, explains scatterplot estimands, adds alternative group estimators and Bayesian hierarchical group effects, and reduces figure crowding.

### Requirements
- Participants 01–30; Both, Strength and Angle training groups contain 10 people each, as defined in `data/group_assignments.json`.
- Nominal protocol: three 10-trial baseline tasks, 140 training trials, three 30-trial post-test tasks (260 total). Use actual rows and eligibility: missing trials are not padded or imputed.
- Baseline/test sources: `data/participants/{ID}/processed_csv/`, with nested CSV directories supported. Training sources: `{ID}/outlier_results/labeled_csv/`. Discover actual filenames; do not assume exact prefixes.
- An outlier flag equal to 1 excludes that channel from relevant analysis. The publication training loader additionally requires scored status. Existing pipelines have documented eligibility differences; do not silently unify them.
- Repository/Wiki prose and academic figures are English. Literal existing Chinese filenames remain valid references.
- Provide traceable algorithms, input/output definitions, uncertainty interpretation and validation evidence. Figure aesthetics must not change observations or manufacture effects.

### Constraints
All source CSVs are read-only. Preserve every CSV, including historical/test/result CSVs, and every video. Videos remain local and must not be uploaded. Preserve UTF-8 BOM and original rows/columns when working with existing CSV workflows. Do not rerun the completed regular-to-both migration, randomize assignments, reset/revert user work or overwrite source data. Outlier column names remain strength_outlier and angle_outlier; do not introduce literal nan labels. Current labeling request requires binary flags.
Git, repository branches, Issues, PRs and Wiki are authorized; merging is not authorized without researcher approval. Only the researcher can confirm understanding or select/accept the primary scientific analysis. Minimize repeated scans, model runs and tool calls: reuse saved results for plotting.

### Current Plan
Implementation and recorded verification are complete. Preserve this state and support researcher review. A new scientific model change needs a bounded question and suitable validation; do not repeatedly fit models just because a heartbeat says continue. For presentation changes, redraw from saved summaries without MCMC.

### Architecture / Important Decisions
| Area | Entry or implementation | Role |
|---|---|---|
| Shared data paths | common/paths.py | Participant/config/output roots |
| Existing publication loader | common/publication_data.py | Discovery and original publication eligibility |
| New inference loader | common/group_inference_data.py | Scored, finite, valid=1 when present, flag!=1; paired baseline/test; group/source audit |
| Data processing | processing/ | Signed preprocessing and historical outlier workflows |
| Existing robust methods | analysis/robust/, plots/baseline_transfer/robust_comparison.py | Separate participant constant-t fits and group comparisons |
| Participant learning | learning_curve_tool/learning_curves.py | Compatibility entry for participant application; keep desktop launcher |
| Group estimator sensitivity | analysis/group_estimators/sensitivity.py | Mean, median, 20% trimmed mean; paired bootstrap; direct contrasts |
| Bayesian model | analysis/hierarchical/model.py | Trial-level Student-t location/log-scale hierarchy |
| Posterior checks/export | analysis/hierarchical/predictive.py, artifacts.py | Predictive diagnostics, compact draws, source manifests |
| New batch entry | plots/group_inference/run.py, run_group_inference.bat | Optional Bayesian analysis and figures |
| Plot-only entries | plots/group_inference/focused_figures.py, posterior_figures.py | Redraw saved results without sampling |
| Other figure families | plots/, root compatibility launchers | Original publication and supplementary analyses remain separate |
| Results | results/group_inference/ | Summary CSVs, figures, diagnostics, cached inputs and local full traces |

The new Bayesian model fits four endpoints separately: both_strength, strength_strength, both_angle and angle_angle. It models baseline and post-test trials, not training. Signed responses are divided by pooled baseline RMS without centering; outputs restore physical units. Student-t nu=5 is fixed. Group baseline/change location and log-scale parameters partially pool; participant baseline/change effects are independent with shared SDs across groups. Group within-person variance integrates the lognormal scale distribution and excludes between-person location variation. Proven censor bounds can contribute CDF/survival likelihood, but the current dataset contains zero proven censor events.
The equivalent Helmert-contrast parameterization integrates a redundant common group deviation without altering the scientific group prior. NUMBA and sequential chains were used successfully. Earlier failed attempts remain in attempt1/before_orthogonal directories; their diagnostics are not final evidence.

### Completed Work
1. Physical module/data organization, compatibility launchers and detailed method Wiki were delivered in PR #6.
2. English translations cover repository Markdown prose and all 17 Wiki pages; the supplementary README generator also emits English. Historical filenames were not renamed.
3. The original scatterplot's individual/group estimands and SEM are documented. Alternative group estimators and direct effects are implemented separately.
4. Four real-data Bayesian endpoint fits completed. Compact posterior draws, checksums, sampling diagnostics, predictive checks and contrasts are exported. Large posterior.nc traces stay local and ignored by Git.
5. Nine focused figure pairs split three metrics by three estimators into 2x2 layouts. Central point clouds are enlarged when appropriate, with full-range insets retaining extremes and counts outside the zoom. No point is jittered or deleted. Posterior variance panels use positive log axes spanning all interval endpoints.
6. Final code/results and Wiki were pushed. No PR was merged by the agent.

### Files Changed
For the latest implemented feature, inspect common/group_inference_data.py; analysis/group_estimators/; analysis/hierarchical/; plots/group_inference/; tests/group_inference/; tests/hierarchical/; requirements_hierarchical.txt; run_group_inference.bat; results/group_inference/; translated Markdown and the supplementary README generator. Git commits provide the precise change list.
This handoff-only session changes tools/outlier_batch/TASK_STATE.md, appends the canonical repository note to AGENTS.md, and records HILD/journal/2026-11-21.md. No scientific code, CSV, video or figure is changed in this session. These documentation edits are left uncommitted for the next reviewer; do not assume a clean worktree after reading this handoff.

### Tests / Verification Performed
Recorded implementation verification on 2026-11-15: 68 tests passed in a full regression run, plus one new mixed-source plot test separately (69 distinct tests). Actual frequentist CLI execution, all four cache arrays versus fresh read-only loading, posterior export, figure rendering and 300 DPI PNG/PDF pairing were checked. All 240 stage fits succeeded. Estimator exports contain 108 group points and 108 contrasts.
Protection evidence: 2,523 original CSV SHA256 values, 210 video size/mtime records and 181 current input hashes were verified unchanged. See docs/maintenance/protected_files.json, relocation_verification.json and results/group_inference/verification.json. These full checks were not rerun just to write this handoff.
Final MCMC: four chains per endpoint, 2,000 tuning iterations and 1,500 retained draws per chain, target_accept=.995, cores=1. All have zero divergences, adequate ESS/BFMI and no maximum-depth hits. Worst Rhat=1.00705; smallest bulk/tail ESS=609/725. Eligible counts: 1125, 1150, 1196, 1191 respectively. Diagnostics were read again for this handoff; no sampling was rerun.
A single simulated recovery run covered six of six location truths and five of six variance truths; it is not a calibration study.

### Known Issues
- Computational convergence does not establish model adequacy. Observed summaries inside posterior predictive intervals: 23/24, 22/24, 21/24, 18/24 across the four endpoints. Angle-only tails and SD show material discrepancies. Do not remove observations to force a better-looking fit.
- None of 36 frequentist mean-change Welch comparisons passes global Holm .05. Of 36 Bayesian contrasts, 35 equal-tailed 95% intervals contain zero. The strength-only Strength-minus-Angle location-change contrast barely excludes zero (median -0.1960, interval [-0.3975,-0.0010], P<0=.9767). It is exploratory, not a multiplicity-adjusted discovery or automatic improvement in accuracy.
- Fixed nu, independent random baseline/change deviations, common random-effect SDs and within-stage exchangeability remain assumptions. Prior sensitivity, asymmetric tails and serial dependence are not resolved.
- Historical publication outputs have 62 input-hash mismatches against current source data; they were preserved. Earlier refactor checks showed exact loader equivalence on current data. Do not use old outputs as if generated from current inputs.
- Existing analysis families have different methods/filters. Figure2's normalized block averages/exponential fit is not the participant app's trial-level Student-t spline. Scientific Issue #2 remains the primary-method review topic.
- Wiki explains the Bayesian effects but does not yet contain a dedicated filename-titled, panel-by-panel reading tutorial. The user asked for explanations in chat; a tutorial update is a possible follow-up, not evidence of unfinished computation.
- automation-4 keeps sending continue. Deleting it was rejected because explicit user authorization to stop it is absent. The user has already been asked. Do not bypass that rejection or repeat finished analyses on heartbeat.

### Figure Interpretation for the Next Assistant
Task means the task performed during baseline/post-test; group means the training assignment. Both task / strength therefore contains strength measurements from all three training groups.
Location is the fitted signed center; closer to zero means less directional bias. MAE is mean absolute recorded error; lower means smaller overall error. Variance is modeled within-person trial variation; lower means greater consistency, not necessarily greater accuracy or isolated internal motor noise.
Original robust plot: small point=participant stage estimate; large point=arithmetic mean of paired participant estimates; crosshairs=marginal +/-SEM.
Focused estimator figures: group point=mean/median/20% trimmed mean of participant stage summaries; crosshairs=pointwise paired-bootstrap 95% intervals.
group_estimator_contrasts: (post-baseline group estimator A) minus (post-baseline group estimator B). Colors/shapes represent estimators here, not training groups. Nonlinear differences of stage estimators are not generally estimators of individual changes.
hierarchical_group_points: posterior median of population group location/expected within-person variance, with marginal 95% credible intervals.
hierarchical_group_effects: columns are the four endpoints; rows are location-change difference, variance-change difference and difference in log(post/pre variance ratios). Each panel compares Both-Strength, Both-Angle and Strength-Angle. Dots=posterior medians, bars=95% credible intervals, vertical zero=no difference in change. P(A-B<0) is a model-conditional directional probability, not a p-value. Negative signed-location change is not necessarily movement toward zero.

### Remaining Work
No outstanding computation or implementation in the latest delivered scope. Researcher review/merge, scientific primary-analysis choice, model-fit assessment and confirmed understanding are still pending. Do not mark them complete on the researcher's behalf. Any next model revision should explicitly target the predictive discrepancies and preserve comparisons with the delivered model.

### Recommended Next Step
Read results/group_inference/README_RESULTS.md and plots/group_inference/README.md, then review the exact change requested by the researcher. For figure-only work use saved CSVs/posterior draws. Run only checks affected by a change. Review PR #6 before merging/rebasing the stacked PR #8; merging still needs explicit researcher authorization.

### Important Context for Next Session
Verified 2026-11-21: canonical repository is now https://github.com/Motor-Learning-Lab/Billiards (old ayyyeeeee URLs redirect). The local branch is codex/group-estimators-english-docs at bd1ef8c82b2fdd3acba5c3acc5a16548acbd5be2 before this documentation edit. Main and Wiki worktrees were clean at entry. Wiki local head is 5b0cc11. PR #6 remains OPEN/unmerged, base main, head fd8901d689109fff2bcc5d661ff6c888b9e2adb0. PR #8 remains OPEN/unmerged, base codex/modularize-research-workflows, head bd1ef8c82b2fdd3acba5c3acc5a16548acbd5be2. Remote PR state was checked using the public API after the GitHub connector could not follow the numeric redirect. Issue #2 status itself was not re-fetched today.

Useful links:
- https://github.com/Motor-Learning-Lab/Billiards/pull/6
- https://github.com/Motor-Learning-Lab/Billiards/pull/8
- https://github.com/Motor-Learning-Lab/Billiards/wiki/Figure-Robust-Baseline-Transfer
- https://github.com/Motor-Learning-Lab/Billiards/wiki/Method-Group-Estimators-and-Hierarchical-Inference

From D:/experiment, plot-only commands (no MCMC):
```powershell
python -m plots.group_inference.focused_figures
python -m plots.group_inference.posterior_figures
```
Full regression, only when relevant:
```powershell
python -m unittest discover -s tests -t . -p "test_*.py"
```
A new full model run is expensive; use only for an actual data/model change:
```powershell
python -m plots.group_inference.run --bayesian --draws 1500 --tune 2000 --cores 1 --target-accept .995
```
Installed successful environment: Python under C:/ProgramData/anaconda3, PyMC 5.20.0, ArviZ 0.20.0, NUMBA. requirements_hierarchical.txt records dependencies. Do not rely on old process/session IDs; all formal endpoint results are already saved. Sources, failed-attempt CSVs and local full traces must remain intact.

### New figure milestone — across-subject training curves (2026-11-21)

The researcher requested a group view of the individual training mean and variance learning curves. The new module `plots/participant_learning/across_subjects.py` reads the current labeled training files for IDs 01–30. It reuses the participant figures' channel eligibility, censoring logic and Student-t spline. At each supported integer trial, the plotted estimands are the arithmetic mean of participant fitted means and the arithmetic mean of participant fitted within-person variances, separately by training group and component. Bands are between-participant interquartile ranges. Lines break at changes in membership.

Completed and verified at commit `23445a1` on `codex/across-subject-learning-curves`. See `results/across_subject_learning/` for the PNG, PDF, caption/method, 40 fit records, 5,590 participant-trial estimates and 560 group-trial summaries. Reproduce from the project root with `python -m plots.participant_learning.across_subjects`. Verified all source hashes, eligibility and support counts against labeled CSVs, both endpoint estimates against all 40 matching historical fits, and group means and quartiles against separate calculations. Twelve relevant robust-model, censoring and outlier tests passed; the rendered PDF was visually checked. All four series have ten contributors at trials 2–136. Partial support at the edges changes the group composition.

Review is pending on [draft PR 9](https://github.com/Motor-Learning-Lab/Billiards/pull/9), stacked on the branch for PR 8. The figure is descriptive. Researcher scientific acceptance and understanding remain pending. The previous handoff and journal edits were already uncommitted at entry and remain local. This milestone adds no new group hypothesis test or MCMC run.

### New figure milestone — bivariate Student-t scatterplot centers (2026-11-21)

The researcher requested new population points in the three robust baseline/post-test scatterplots and publication to GitHub and Wiki. [Draft PR 10](https://github.com/Motor-Learning-Lab/Billiards/pull/10) is stacked on PR 9. Code and results are in commit `cf46044`, branch `codex/bivariate-t-scatter-centers`. This supersedes the earlier arithmetic mean / SEM interpretation of the large markers in these three figures.

The existing participant table supplies the original small-point coordinates (SHA-256 `5de9e2ca517d86f04afb3684511876bdc902d6e7705bf843cdbb71bf38324ade`). The participant ID pairs baseline with immediate post-test. Each metric, task and training group gets an independent full-scatter bivariate Student-t maximum-likelihood fit with fixed df=5 in original units. The black-edged marker is the joint location. Insets reuse it. The figures display point estimates. Their companion descriptive statistics tables still contain arithmetic summaries and SEMs. No participant source, earlier estimator sensitivity or Bayesian inference changed.

Reproduce with `python plot_baseline_vs_transfer.py --metrics-csv results/baseline_vs_transfer_robust/subject_baseline_vs_transfer_metrics.csv`. The six figure files and `population_points.csv` are under `results/baseline_vs_transfer_robust/`. Relevant code is in `plots/baseline_transfer/robust_comparison.py` and `analysis/robust/bivariate_t.py`. All 36 fits used ten complete pairs. Independent likelihood maximization matched the locations within 2.04e-8. All 360 main-panel participant coordinates and all 36 main plus 12 inset population markers were checked. Fourteen related tests passed. Both PNG and PDF figures were visually inspected. Small samples limit interpretation and this two-stage fit conditions on each person's stage summaries. Researcher review and merge remain pending.

Wiki commit `d38c7cd` is published on the separate Wiki master branch. The [figure reading guide](https://github.com/Motor-Learning-Lab/Billiards/wiki/Figure-Robust-Baseline-Transfer) and the related group-inference page explain the new centers and reference draft PR 10.

### Corrected target — group-inference scatterplots (2026-11-21)

The researcher specified `results/group_inference/` and selected nine updated focused plots, the estimator overview, and three center-only plots. Implementation and verification are complete in [draft PR 11](https://github.com/Motor-Learning-Lab/Billiards/pull/11) at `6b3f13d`, stacked on the estimator in PR 10. Earlier plots remain intact. The group-inference figures use their own full-precision `participant_pairs.csv` (SHA-256 `2eae0fb82359da979ec8d619ca7c7759df0a0480357b56e16c75fd8f4f79364c`). Rebuild with `python -m plots.group_inference.bivariate_figures`.

Verified 181 source hashes, 240 stage summaries, 120 participant/endpoint pairs, 36 complete ten-person fits and 360 weights. Independent direct likelihood optimization reproduced each location within 2.14e-7 original units. Nine estimator tests passed. The plotting checks verified 13 figures, 180 main and 72 inset diamond positions and participant clouds. The earlier bootstrap crosshairs still refer to the estimators named in the figures. The three new center-only PDFs and PNGs have linear axes. Bayesian posterior and group contrast figures were outside this scope.

The [group-level Wiki tutorial](https://github.com/Motor-Learning-Lab/Billiards/wiki/Figure-Group-Inference-Bivariate-Centers) was published at Wiki commit `83c178e`; public HTTP 200 and the worked example were verified. The Wiki worktree is on `codex/group-inference-aggregate-guide` tracking origin/master. Its local master contains an unpublished participant-level draft; do not push it. The public tutorial uses only group-level examples and explains how to check the weights locally. Researcher review of PR 11, merge and scientific acceptance remain pending.

### Standalone hierarchical variance scatterplot (2026-11-21)

The researcher chose option A: a four-panel baseline/post-test variance scatterplot using existing hierarchical population parameters. Branch `codex/hierarchical-variance-scatter` contains the local implementation. New outputs are `results/group_inference/hierarchical_variance_scatter.{png,pdf,csv}`. Render from the saved inputs with `python -m plots.group_inference.posterior_figures --variance-only`. The Bayesian pipeline also generates the plot after a complete four-endpoint run. No MCMC was rerun. The 120 participant markers were verified against stage estimates. All 12 population points and 24 marginal interval segments matched quantiles from 6,000 draws per group and stage; all 181 source hashes matched. PDF visually inspected and three related tests passed.

The researcher explicitly authorized publication of the day's results and Wiki. Figure revision `d373ddf` is published in [draft PR 12](https://github.com/Motor-Learning-Lab/Billiards/pull/12), stacked on PR 11. Three related tests passed again before publication. Wiki revision `6200d8e` adds the [hierarchical variance guide](https://github.com/Motor-Learning-Lab/Billiards/wiki/Figure-Hierarchical-Variance-Scatter) and [across-subject learning curve guide](https://github.com/Motor-Learning-Lab/Billiards/wiki/Figure-Across-Subject-Learning-Curves). The Wiki home and all four figure guides returned HTTP 200 with the expected content. PRs 9, 10, 11 and 12 were verified open in draft. This publication includes the day's handoff and journal records. Researcher review, merge and scientific acceptance remain pending.
