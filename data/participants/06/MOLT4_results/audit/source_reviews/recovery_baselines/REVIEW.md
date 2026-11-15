# Local review of two baseline-strength segments: retain blank scores

Conclusion: shot 8 for both 01 and 03 involves actual hand intervention. The available source footage cannot recover reliable free axis-crossing speed or a natural stopping point. **Do not integrate any candidate raw package; retain the original primary-analysis diagnostics and all scalar values unchanged.**

- 01: examined 89–100 seconds. At 96.800 seconds the ball was still moving, approximately 26.06 cm perpendicular to the Y axis; the hand approached/contacted it at 96.9 seconds, gripped it around 97.0 seconds, and transported it back to O after 97.3 seconds. Frozen f6 used only normal-light detection (the dark-light gate was disabled) and recovered no usable missing points beyond the original cache. Retain the original `assumed_stationary_hand` unresolved status.
- 03: examined 87–97 seconds. The hand contacted the ball around 93.2 seconds, after which motion was hand-influenced; the safe free observation at 93.100 seconds was approximately 100.10 cm perpendicular to the Y axis. Frozen dark-light contours can recover 11 actual red-ball points at 92.700–92.884 seconds before pickup, but still establish neither free axis crossing nor a confirmable natural stop. Retain the original `unexpected_longitudinal_cushion_before_crossing` unresolved status.

The original point at 94.050 seconds for 03 lies on the distant upper cushion; the source frame shows it is not the actual ball. f6 instead selects the actual hand/ball contact area at that time, with hand_fraction=0.455. This contour establishes non-free hand contact, not a reliable ball center. A trial replacement of this point causes the existing assumed-stop branch to output an assumed pickup-stop score of approximately 0.473879. This is not reliable natural-stop or free-axis-crossing evidence found by this review, and was explicitly rejected and not adopted. This trial is stored separately as `REJECTED_nonfree_hand_hypothesis.npz` and must not be integrated or described as successful recovery.

## Frozen evidence

- `manual_review_manifest.json`: final manual conclusions for both cases and checksums of inputs/sources/candidate packages.
- `manual_review.json` in each segment directory: original scores, non-adopted candidate recomputation, source-frame list, and pointwise color-pixel/hand evidence.
- `original_source_frames/`: unmarked source PNGs; decoded source PTS corresponds frame by frame to the original cache.
- `remeasure_contactsheet_*.jpg`: local source-video contact sheets every 0.1 seconds. Purple circles indicate original points; yellow circles indicate current f6 measurements in the same frames.
- `local_measurements.npz` / `frame_remeasurements.json`: frame-by-frame causal measurements in the original window, methods, current contour area, actual HSV red-pixel support, and original/new rows.
- `*_NOT_ADOPTED_review_candidate.npz`: all four complete data/fps/quad/median arrays. 01 is an unchanged zero-patch reference; 03 adds only 11 actual missing points before pickup, preserving all originally observed coordinates, all PTS, and other rows. Both cases remain unresolved; every field of other attempts and all numeric scores are exactly unchanged.

Local detection uses frozen counter `f6dddc5877b318f2607c5f23fb01650ac93d6a93cdcd139dd364c96e6e989043` and live_detection `6ae8428ba2eb48198be42506ab3d831868476702d83843a493002de9c887ba4e`. Same-frame contour-support functions come from the frozen participant07 extraction script. All code, cfg, and source hashes are recorded. Original video/cache/cal/report/code hashes match before and after processing. No writes were made to primary analysis; no rules were changed, points smoothed, hand contacts fabricated, or new free speeds inferred.

Manifest SHA256: `b671cecb3f30e8c746255f1c51f9dffc1b9a29bad06395b838b23f2a0bd31c94`.
