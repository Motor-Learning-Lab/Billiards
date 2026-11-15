# 01 test angle: retain 21 shots; no recovery recommended

The current audit contains **21 attempts, all 21 scored**. No audit rows were excluded for movement below 8 cm, reversed direction, or unresolved status. The filename's 30 must not be interpreted as 30 shots having occurred, with the difference treated as 9 missed shots.

An independent scan of all 13,289 original raw frames found 21 groups of actual free-ball observations approaching the upper cushion, reaching an extremum, and returning. Their extremum times match the existing 21 endpoints exactly, one for one. The video spans 221.466 seconds, with 1,368 frames missing in raw; 21 missing intervals last at least 0.3 seconds. Targeted source-video checks place these intervals in hand pickup, transport back to O, and ball positioning after return. No evidence supporting an additional shot was found.

| Focus interval | Source-video observation | Treatment |
| --- | --- | --- |
| 9–12 seconds | Slow return of the first shot; hand pickup around 10.833–11.167 seconds, followed by transport to O | Do not count twice |
| 29–34 seconds | Third-shot return; hand pickup and replacement at O at 31.333–32.833 seconds; next shot around 36.683 seconds | Do not add a shot |
| 88.033–89.750, 99.933–101.233 seconds | Original frames before, during, and after the gaps show pickup and transport to O | No basis for recovery |
| 107.216–124.866 seconds | Upper-cushion contact at 108.283 seconds; still returning at 111/114 seconds; pickup back to O at 117.783–119.233 seconds, waiting at 121 seconds; next departure at 124.866 seconds | One complete shot cycle |
| Long gaps within 131.866–184.483 seconds | Sampled frames before, during, and after each gap show hand transport and replacement at O | Not free shots |
| 185–221.466 seconds | No raw gaps; source frames agree with the final four cushion contacts and returns in the current table | Retain current table |

An independent reviewer also examined a one-frame-per-second overview of 0–80 seconds, 6 fps contact sheets of two suspicious intervals, and actual approach/contact/return frames for the first eight upper-cushion contacts, agreeing with the primary review. The primary review examined frames before, during, and after all long gaps after 80 seconds, plus the long pause and ending: 48 actual source frames. This targeted check is not full-video frame-by-frame manual ground truth. Its conclusion is “no evidence of missed shots requiring recovery was found”; counts are not inferred from filenames.

Final recommendation: **Retain the existing 21 angle results. Do not change raw data, scoring rules, or counts, and do not pad to 30.**

Evidence entry points:

- `review_conclusion.json`: frozen conclusion, scope limitations, and input SHA. SHA256 `cf3c0cbce8a2f9b1b396adbf3d3c826bd6a37ffc2f9bb42d116f8f88de979c9c`.
- `source_review_evidence.json`: 21 contact groups, 21 long gaps, and locations/SHA of 48 actual source frames.
- `summary_missing_intervals_80plus_*.jpg` / `summary_pause_tail_*.jpg`: visually inspected source-frame contact sheets; no inferred points are drawn.
- `summary_source_frames/`: unmodified original full-frame PNGs.
- `independent_manual_review.json` / `independent_manual_bank_witness.jpg`: independent 0–80-second review.

Source-video SHA256: `ee2215a0a646c2e83eca503d5a888efaa77c1e0ec0fe549248f435a7b0bf4ee6`. Input hashes for the video, current raw, cal, report, and attempt CSV were identical before and after; only this review directory was written.
