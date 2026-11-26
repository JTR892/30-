"""Counterexample checks for the optional, limited exact-overlap search."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image


class ContentOverlapTests(unittest.TestCase):
    def test_true_translated_crop_and_unrelated_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); raw = base / "raw"; raw.mkdir(); audit = base / "audit"; audit.mkdir()
            rng = np.random.default_rng(17)
            full = rng.integers(0, 65535, (180, 180), dtype=np.uint16)
            arrays = {"sample_0_0.tif": full, "sample_0_1.tif": full[10:170, 10:170],
                      "sample_1_0.tif": rng.integers(0, 65535, (160, 160), dtype=np.uint16)}
            rows = []
            for name, a in arrays.items():
                Image.fromarray(a).save(raw / name)
                rows.append({"image_id": name, "image_path": name,
                             "pixel_sha256": hashlib.sha256(a.tobytes()).hexdigest(),
                             "supplied_partition": "unallocated", "population_claim": "fixture", "defect_labels": []})
            (audit / "images.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
            command = [sys.executable, str(Path(__file__).resolve().parents[1]/"scripts/check_content_overlap.py"),
                       "--root", str(raw), "--audit", str(audit)]
            subprocess.run(command, check=True, capture_output=True)
            summary = json.loads((audit/"crop_overlap_summary.json").read_text())
            links = json.loads((audit/"exact_overlap_links.json").read_text())
            self.assertEqual(summary["exact_overlap_links"], 1)
            self.assertEqual(summary["nonidentical_shift_links"], 1)
            self.assertEqual(summary["components_including_singletons"], 2)
            self.assertEqual(links[0]["dx_b_origin_in_a"], 10)
            self.assertEqual(links[0]["dy_b_origin_in_a"], 10)
            self.assertFalse(summary["all_possible_pairs_searched"])


if __name__ == "__main__":
    unittest.main()
