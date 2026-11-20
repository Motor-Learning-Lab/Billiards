# Learning curves across subjects

The figure covers training trials 1–140 for participants 01–30. Each participant trained in one of three groups (10 people each). The Both group contributed one strength and one angle series. Each single-component group contributed its trained component.

**a–b. Mean signed error.** Each line averages the fitted individual means at the indicated training trial. Zero denotes no average directional bias. Positive and negative biases can cancel across participants.

**c–d. Within-person variance.** Each participant's Student-t model estimates trial variance as squared scale times 5/3. The group line averages these variances with equal weight. Lower values indicate more consistent performance within a participant.

**e–f. Contributing participants.** Counts refer to individual fits covering each trial. Individual predictions span the first through last eligible shot and may interpolate across interior gaps. Lines in a–d break when the set of contributors changes. All groups have ten contributors per channel throughout trials 2–136. Participants 07, 09 and 19 recorded 136, 138 and 139 shots respectively.

Shading shows the pointwise 25th and 75th percentiles across participant fits. Vertical bars show the same range for isolated points. These are descriptive summaries of participant heterogeneity. The figure provides no test of group differences.

## Reproduction

Run `python -m plots.participant_learning.across_subjects` from the repository root. This reads the labeled training CSV for each participant from `data/participants/{ID}/outlier_results/labeled_csv/` and checks its condition against `data/group_assignments.json`. The training rule and penalized Student-t location/scale spline follow the individual learning figures. Each channel uses finite signed values with its own outlier flag cleared. Documented censoring uses the project's signed-bound likelihood. The fitted mean and variance use separate spline bases of dimensions 5 and 3, with penalty 1 and 5 degrees of freedom.

The PNG and PDF show the same figure. `group_curves.csv` lists means, quartiles, counts and contributing IDs by group, channel and trial. `participant_curves.csv` contains the predictions used in those averages. `fit_audit.csv` identifies input paths relative to the participant root, SHA-256 hashes, counts and supported trial ranges.
