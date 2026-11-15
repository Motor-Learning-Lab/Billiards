import json
import tempfile
import unittest
from pathlib import Path
from plots.group_inference.posterior_figures import draw_posteriors


class PosteriorSourceTests(unittest.TestCase):
    def test_mixed_source_snapshots_are_rejected_before_plotting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source_hashes.json").write_text(json.dumps({"input.csv": "new"}))
            endpoint = root / "bayes" / "both_strength"
            endpoint.mkdir(parents=True)
            (endpoint / "posterior_manifest.json").write_text(
                json.dumps({"source_snapshot_sha256": "old"}))
            with self.assertRaisesRegex(ValueError, "different source snapshots"):
                draw_posteriors(root)
