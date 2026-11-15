# Assumed-stop semantics and targeted source-frame checks

`strength_assumed_stop=1` does not, by itself, violate the historical protocol: old handoffs/guides and tests explicitly retain assumed stops at the last hand-held or EOF observation. v3 strength fully inherits this behavior. However, this is not natural-stop detection, and the current `method=observed_stop` is misleading.

Local source-video frames and actual trajectories were reviewed for all 7 specified shots. 01_02 strength shots 2/4 and shots 4/5/6/8/10 within the first 10 of 03_01 both do not establish a natural stop before pickup. Scoring points for 01#4 and 03#4/#5/#8 had already moved with the hand. In the first category the ball was picked up while slowly rolling; in the second, occlusion caused a gap, and a reacquired red-ball position after transport triggered the hand threshold.

| Source/shot | Net displacement of actual free-ball points over the final approximately 0.30 seconds (cm) | Review conclusion |
|---|---:|---|
| 01_02_baseline_strength_010shots / 2 | 1.650 | Still moving before contact; stop unconfirmed |
| 01_02_baseline_strength_010shots / 4 | 1.156 | Scoring point already transported |
| 03_01_baseline_both_010shots / 4 | 2.299 | Scoring point already transported |
| 03_01_baseline_both_010shots / 5 | 2.890 | Scoring point already transported |
| 03_01_baseline_both_010shots / 6 | 2.043 | Still moving before contact; stop unconfirmed |
| 03_01_baseline_both_010shots / 8 | 1.292 | Scoring point already transported |
| 03_01_baseline_both_010shots / 10 | 1.905 | Still moving before contact; stop unconfirmed |

If primary scoring in this run requires a genuine natural stop, these values should remain only as explicitly labeled intervention-endpoint estimates in the audit; primary strength should be blank with status=unresolved. Retain valid target-cushion shots/angle, selecting the first N in actual chronological order without deleting a shot and substituting a later one. Values supported by a completed natural stop before pickup or reliable free axis-crossing speed should remain; later hand contact must not clear them indiscriminately. When no axis crossing occurred, do not apply a model without authorization to impute a natural stopping point.

If the historical assumed-stop scoring protocol is continued, identify these as estimates and mark them for review; do not tell the user that they are measured natural stops. Historical documents cannot substitute for the current user's choice.

The current 46 primary CSVs contain 89 assumed+scored rows; 74 remain after 10/140/30 truncation (73 hand contact, 1 EOF), involving 17 sources. Only the above 7 shots have been visually verified. Do not assert that all remaining 67 retained rows involve motion, or claim complete natural-stop compliance after clearing only these 7.

This directory stores 7 source-frame contact sheets, 7 frame-by-frame actual-trajectory CSVs, and assumed_stop_evidence.json with SHA values. No writes were made to original videos, core code, caches, scores, analysis, or recovery_baselines.
