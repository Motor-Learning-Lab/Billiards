# Participant 03: final CSV

The main file is 03.csv; csv/ contains 7 independent segment results.
Within each segment, retain actual valid shots in chronological order: at most the first 10 baseline, 140 training, and 30 test shots. Do not select by score or fabricate missing shots.
strength_value is measured in O-to-B lengths and angle_value in degrees; both retains the two components independently.
Components without reliable evidence remain blank; status, needs_review, and tracking_observation_review retain the reasons for review.
Hand-removal/end-of-video estimates without a confirmed natural stop are not strength scores; the primary component remains blank. Old estimates are retained only in strength_unconfirmed_estimate and must not be treated as measured stopping points.
audit/uncapped contains full results before trial-count truncation, for provenance only; use the main file or csv/ for formal analysis.
Original videos, sessions, recording logs, MOLT4_results1, and the 08/09 deliveries were not changed. Complete original observations remain in the working directory specified by processing_info.

The SHA manifest is delivery_manifest.json; the manifest's own SHA is stored in deployment.json in this run's working directory.
