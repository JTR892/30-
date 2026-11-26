"""Synthetic counterexamples for the private, pre-partition XML auditor."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, TiffImagePlugin

from weldstudy.xml_audit import inspect_image, parse_xml, run_audit


class XMLAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.raw = self.base / "raw"
        self.raw.mkdir()
        self.config = {"population_roots": {"bad": "DEFECT_CLAIM", "good": "NORMAL_CLAIM"},
                       "directory_classes": {"pores": "气孔"}, "partition_names": ["train", "test"],
                       "auxiliary_labels": ["焊缝"], "known_defect_labels": ["气孔", "裂纹", "其它缺陷"],
                       "heterogeneous_labels": ["其它缺陷"]}
        self.config_path = self.base / "config.json"
        self.config_path.write_text(json.dumps(self.config))

    def image(self, rel="bad/train/pores/a.tif", metadata=None):
        p = self.raw / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        im = Image.fromarray(np.arange(120, dtype=np.uint16).reshape(10, 12))
        if metadata:
            im.save(p, tiffinfo=metadata)
        else:
            im.save(p)
        return p

    def xml(self, image, labels=("气孔",), width=12, height=10, box=(1, 2, 5, 8), filename=None):
        body = "".join(f"<object><name>{n}</name><bndbox><xmin>{box[0]}</xmin><ymin>{box[1]}</ymin><xmax>{box[2]}</xmax><ymax>{box[3]}</ymax></bndbox></object>" for n in labels)
        p = image.with_suffix(".xml")
        p.write_text(f"<annotation><filename>{filename or image.name}</filename><folder>气孔</folder><size><width>{width}</width><height>{height}</height><depth>1</depth></size>{body}</annotation>")
        return p

    def inspect(self, image):
        x = image.with_suffix(".xml")
        return inspect_image((self.raw, image, [x] if x.exists() else [], self.config))

    def test_auxiliary_weld_is_not_a_second_defect_type(self):
        p = self.image()
        self.xml(p, ("气孔", "焊缝"))
        r, objs = self.inspect(p)
        self.assertEqual(r["defect_labels"], ["气孔"])
        self.assertEqual(r["n_objects"], 2)
        self.assertTrue(r["candidate_status"].startswith("STRUCTURAL_SINGLE"))
        self.assertEqual(r["semantic_status"], "NOT_EXPERT_REVIEWED")

    def test_missing_xml_does_not_certify_normal(self):
        r, _ = self.inspect(self.image("good/a.tif"))
        self.assertEqual(r["defect_labels"], [])
        self.assertEqual(r["candidate_status"], "HOLD")
        self.assertEqual(r["xml_status"], "MISSING")

    def test_multidefect_not_forced_to_folder_label(self):
        p = self.image()
        self.xml(p, ("气孔", "裂纹"))
        r, _ = self.inspect(p)
        self.assertEqual(r["candidate_status"], "MULTITYPE_NOT_SINGLE_LABEL")
        self.assertEqual(r["label_consistency"], "DIRECTORY_PRESENT_MULTITYPE")

    def test_wrong_class_folder_is_flagged(self):
        p = self.image()
        self.xml(p, ("裂纹",))
        r, _ = self.inspect(p)
        self.assertIn("DIRECTORY_LABEL_ABSENT", r["issues"])
        self.assertEqual(r["candidate_status"], "HOLD")

    def test_source_size_and_box_not_automatically_rescaled_to_crop(self):
        p = self.image()
        self.xml(p, width=100, height=80, box=(40, 30, 50, 60))
        r, objs = self.inspect(p)
        self.assertIn("XML_IMAGE_SIZE_MISMATCH", r["issues"])
        self.assertEqual(r["boxes_invalid_actual"], 1)
        self.assertEqual(r["boxes_invalid_xml"], 0)
        self.assertEqual(objs[0]["box"], [40., 30., 50., 60.])

    def test_box_inverted_or_nonfinite_rejected(self):
        for box in [(6, 2, 1, 8), (1, 2, "nan", 8), (1, 2, "inf", 8)]:
            p = self.image()
            self.xml(p, box=box)
            r, _ = self.inspect(p)
            self.assertEqual(r["candidate_status"], "HOLD")
            self.assertIn("OBJECT_ERROR", r["issues"])

    def test_tif_tiff_extension_only_is_not_wrong_identity(self):
        p = self.image()
        self.xml(p, filename="a.tiff")
        r, _ = self.inspect(p)
        self.assertEqual(r["filename_match"], "TIFF_EXTENSION_ONLY")
        self.assertNotIn("XML_FILENAME_MISMATCH", r["issues"])

    def test_filename_stem_mismatch_blocks_candidate(self):
        p = self.image()
        self.xml(p, filename="other.tif")
        r, _ = self.inspect(p)
        self.assertIn("XML_FILENAME_MISMATCH", r["issues"])

    def test_dtd_and_utf16_dtd_rejected(self):
        p = self.base / "entity.xml"
        raw = '<!DOCTYPE annotation [<!ENTITY x "test">]><annotation>&x;</annotation>'
        for encoding in ["utf-8", "utf-16"]:
            p.write_bytes(raw.encode(encoding))
            r = parse_xml(p)
            self.assertEqual(r["parse_status"], "ERROR")

    def test_full_audit_pixel_duplicates_orphans_and_read_only(self):
        p = self.image()
        self.xml(p)
        tags = TiffImagePlugin.ImageFileDirectory_v2()
        tags[270] = "Different TIFF header, same original pixels"
        self.image("good/a2.tif", tags)
        (self.raw / "orphan.xml").write_text("<annotation/>")
        before = {str(p): p.read_bytes() for p in self.raw.rglob("*") if p.is_file()}
        result = run_audit(self.raw, self.base / "out", self.config_path, 2)
        self.assertEqual(result["byte_duplicate_summary"]["groups"], 0)
        self.assertEqual(result["pixel_duplicate_summary"]["cross_population_groups"], 1)
        self.assertEqual(result["orphan_xml_files"], ["orphan.xml"])
        self.assertEqual(result["input_stat_changes"], [])
        after = {str(p): p.read_bytes() for p in self.raw.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_output_cannot_touch_raw_or_overwrite_prior_audit(self):
        p = self.image()
        self.xml(p)
        with self.assertRaises(ValueError):
            run_audit(self.raw, self.raw / "out", self.config_path)
        out = self.base / "existing"
        out.mkdir()
        (out / "keep").write_text("prior")
        with self.assertRaises(ValueError):
            run_audit(self.raw, out, self.config_path)

    def test_independent_verifier_detects_changed_xml_and_returns_failure(self):
        p = self.image()
        xml = self.xml(p)
        out = self.base / "out"
        run_audit(self.raw, out, self.config_path, 1)
        # Mutation is confined to a disposable synthetic fixture.
        xml.write_text(xml.read_text().replace("气孔", "裂纹"))
        script = Path(__file__).resolve().parents[1] / "scripts/verify_xml_audit.py"
        result = subprocess.run([sys.executable, str(script), "--root", str(self.raw),
                                 "--audit", str(out)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        check = json.loads((out / "independent_verification.json").read_text())
        self.assertFalse(check["passed"])
        self.assertIn("xml_hash_changed", check["errors"][0][1])


if __name__ == "__main__":
    unittest.main()
