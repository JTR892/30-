"""Read-only, pre-partition image/XML audit. This does not certify defect semantics.

Outputs are private inventory artifacts, not manifests accepted by the legacy splitter.
Coordinates are checked under a declared provisional 0..width/height envelope;
the producer's inclusive/exclusive and zero/one-based convention remains unverified.
"""
import argparse
import csv
import hashlib
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageOps

from .audit import SUPPORTED, sha256_file

SCHEMA_VERSION = "xml-audit-1.0"


def dump_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                             for k, v in row.items()})


def signature(path):
    s = path.stat()
    return [s.st_size, s.st_mtime_ns]


def int_field(value):
    # Reject silently truncated floating-point sizes.
    return int(value) if value is not None and str(int(value)) == value.strip() else None


def parse_xml(path):
    result = {"xml_path": str(path), "xml_sha256": "", "parse_status": "ERROR",
              "filename": "", "folder": "", "source_path": "", "width": None,
              "height": None, "depth": None, "objects": [], "issues": []}
    try:
        before = signature(path)
        raw = path.read_bytes()
        result["xml_sha256"] = hashlib.sha256(raw).hexdigest()
        # ElementTree never fetches external entities. Also reject DTD/entity declarations
        # explicitly (including UTF-16 encodings) to avoid expanding internal entities.
        probe = raw.replace(b"\x00", b"").upper()
        if b"<!DOCTYPE" in probe or b"<!ENTITY" in probe:
            raise ValueError("DTD_OR_ENTITY_DECLARATION")
        root = ET.fromstring(raw)
        if root.tag != "annotation":
            raise ValueError("UNEXPECTED_XML_ROOT")
        for key in ("filename", "folder"):
            result[key] = (root.findtext(key) or "").strip()
        result["source_path"] = (root.findtext("path") or "").strip()
        for key in ("width", "height", "depth"):
            try:
                result[key] = int_field(root.findtext("size/" + key))
            except ValueError:
                pass
        if not all(result[k] and result[k] > 0 for k in ("width", "height", "depth")):
            result["issues"].append("INVALID_XML_SIZE")
        for i, obj in enumerate(root.findall("object")):
            item = {"object_index": i, "name": (obj.findtext("name") or "").strip(),
                    "box": None, "issues": []}
            if not item["name"]:
                item["issues"].append("EMPTY_OBJECT_NAME")
            try:
                box = [float(obj.findtext("bndbox/" + k)) for k in ("xmin", "ymin", "xmax", "ymax")]
                if not all(math.isfinite(v) for v in box):
                    raise ValueError("NONFINITE")
                item["box"] = box
                if box[2] <= box[0] or box[3] <= box[1]:
                    item["issues"].append("NONPOSITIVE_BOX")
            except (ValueError, TypeError):
                item["issues"].append("MALFORMED_BOX")
            result["objects"].append(item)
        if signature(path) != before:
            result["issues"].append("FILE_CHANGED_DURING_READ")
        result["parse_status"] = "PARSED"
    except (OSError, ValueError, ET.ParseError) as e:
        result["issues"].append(type(e).__name__ + ":" + str(e))
    return result


def envelope_valid(box, width, height):
    return bool(box and width and height and 0 <= box[0] < box[2] <= width
                and 0 <= box[1] < box[3] <= height)


def inspect_image(args):
    root, path, xmls, config = args
    rel = path.relative_to(root).as_posix()
    parts = Path(rel).parts
    row = {"image_id": hashlib.sha256(rel.encode()).hexdigest(), "image_path": rel,
           "population_claim": config.get("population_roots", {}).get(parts[0], "UNKNOWN"),
           "supplied_partition": next((p for p in parts[:-1] if p in config.get("partition_names", [])), "UNSPECIFIED"),
           "directory_class": config.get("directory_classes", {}).get(path.parent.name, ""),
           "file_sha256": "", "pixel_sha256": "", "width": None, "height": None,
           "mode": "", "format": "", "dtype": "", "frames": 0, "bits_per_sample": [],
           "samples_per_pixel": None, "pixel_min": None, "pixel_max": None,
           "file_bytes": None, "mtime_ns": None, "tiff_metadata": {}, "dhash": "",
           "quality_status": "UNREADABLE", "xml_status": "MISSING", "xml_path": "",
           "xml_width": None, "xml_height": None, "xml_depth": None,
           "xml_filename": "", "xml_folder": "", "xml_source_path": "",
           "dimension_match": None, "filename_match": "UNKNOWN", "object_labels": [],
           "defect_labels": [], "n_objects": 0, "n_defect_types": 0,
           "boxes_invalid_actual": 0, "boxes_invalid_xml": 0,
           "label_consistency": "UNKNOWN", "candidate_status": "HOLD",
           "semantic_status": "NOT_EXPERT_REVIEWED", "issues": []}
    try:
        before = signature(path)
        row["file_bytes"], row["mtime_ns"] = before
        row["file_sha256"] = sha256_file(path)
        with Image.open(path) as im:
            row.update(width=im.width, height=im.height, mode=im.mode, format=im.format,
                       frames=getattr(im, "n_frames", 1))
            tags = getattr(im, "tag_v2", {})
            bits = tags.get(258, [])
            row["bits_per_sample"] = list(bits) if isinstance(bits, tuple) else [bits] if bits else []
            row["samples_per_pixel"] = tags.get(277, len(im.getbands()))
            row["tiff_metadata"] = {str(k): str(tags[k]) for k in (270, 271, 272, 274, 282, 283, 296, 305, 306, 339) if k in tags}
            # Decode every frame, rather than only opening its header.
            h = hashlib.sha256()
            for frame in range(row["frames"]):
                im.seek(frame)
                im.load()
                a = np.asarray(im)
                h.update(json.dumps([frame, a.shape, a.dtype.str], separators=(",", ":")).encode())
                h.update(a.tobytes(order="C"))
                if frame == 0:
                    row.update(dtype=str(a.dtype), pixel_min=float(a.min()), pixel_max=float(a.max()))
                    if a.ndim == 2:
                        small = Image.fromarray(a.astype(np.float32)).resize((9, 8), Image.Resampling.BILINEAR)
                        small = np.asarray(small)
                        row["dhash"] = f'{int.from_bytes(np.packbits(small[:, 1:] > small[:, :-1]).tobytes(), "big"):016x}'
            row["pixel_sha256"] = h.hexdigest()
        if row["frames"] != 1:
            row["issues"].append("MULTIFRAME")
        if row["pixel_min"] == row["pixel_max"]:
            row["issues"].append("CONSTANT_IMAGE")
        row["quality_status"] = "READABLE"
        if signature(path) != before:
            row["issues"].append("FILE_CHANGED_DURING_READ")
    except Exception as e:
        row["issues"].append("IMAGE_ERROR:" + type(e).__name__ + ":" + str(e))

    objects = []
    if len(xmls) > 1:
        row["xml_status"] = "AMBIGUOUS"
        row["issues"].append("MULTIPLE_SAME_STEM_XML")
    elif xmls:
        x = parse_xml(xmls[0])
        row.update(xml_status=x["parse_status"], xml_path=xmls[0].relative_to(root).as_posix(),
                   xml_sha256=x["xml_sha256"], xml_width=x["width"], xml_height=x["height"],
                   xml_depth=x["depth"], xml_filename=x["filename"], xml_folder=x["folder"],
                   xml_source_path=x["source_path"])
        row["issues"].extend(x["issues"])
        if x["parse_status"] == "PARSED":
            row["dimension_match"] = row["width"] == x["width"] and row["height"] == x["height"]
            if not row["dimension_match"]:
                row["issues"].append("XML_IMAGE_SIZE_MISMATCH")
            xml_base = PureWindowsPath(x["filename"]).name
            if xml_base == path.name:
                row["filename_match"] = "EXACT"
            elif Path(xml_base).stem == path.stem and Path(xml_base).suffix.lower() in {".tif", ".tiff"} and path.suffix.lower() in {".tif", ".tiff"}:
                row["filename_match"] = "TIFF_EXTENSION_ONLY"
            else:
                row["filename_match"] = "MISMATCH"
                row["issues"].append("XML_FILENAME_MISMATCH")
            if row["samples_per_pixel"] and x["depth"] != row["samples_per_pixel"]:
                row["issues"].append("XML_DEPTH_MISMATCH")
            row["object_labels"] = sorted({o["name"] for o in x["objects"] if o["name"]})
            auxiliary = set(config.get("auxiliary_labels", []))
            row["defect_labels"] = sorted(set(row["object_labels"]) - auxiliary)
            row["n_objects"] = len(x["objects"])
            row["n_defect_types"] = len(row["defect_labels"])
            if not x["objects"]:
                row["issues"].append("NO_XML_OBJECTS")
            known = set(config.get("known_defect_labels", []))
            if set(row["defect_labels"]) - known:
                row["issues"].append("UNMAPPED_XML_LABEL")
            for obj in x["objects"]:
                item = dict(obj, image_id=row["image_id"], image_path=rel, xml_path=row["xml_path"])
                item["valid_actual_envelope"] = envelope_valid(obj["box"], row["width"], row["height"])
                item["valid_xml_envelope"] = envelope_valid(obj["box"], x["width"], x["height"])
                if not item["valid_actual_envelope"]:
                    row["boxes_invalid_actual"] += 1
                if not item["valid_xml_envelope"]:
                    row["boxes_invalid_xml"] += 1
                if obj["issues"]:
                    row["issues"].append("OBJECT_ERROR")
                objects.append(item)
            if row["boxes_invalid_actual"]:
                row["issues"].append("BOX_OUTSIDE_OR_INVALID_ACTUAL")
            if row["boxes_invalid_xml"]:
                row["issues"].append("BOX_OUTSIDE_OR_INVALID_XML")
            expected = row["directory_class"]
            if expected:
                if expected not in row["defect_labels"]:
                    row["label_consistency"] = "DIRECTORY_LABEL_ABSENT"
                    row["issues"].append("DIRECTORY_LABEL_ABSENT")
                elif row["n_defect_types"] > 1:
                    row["label_consistency"] = "DIRECTORY_PRESENT_MULTITYPE"
                else:
                    row["label_consistency"] = "DIRECTORY_EXACT_SINGLE_TYPE"
    # No XML never establishes normality; even a matching XML is not a semantic review.
    if not xmls:
        row["issues"].append("NO_XML_SEMANTIC_UNVERIFIED")
    structural = row["quality_status"] == "READABLE" and row["frames"] == 1 and not row["issues"]
    if structural and row["n_defect_types"] == 1:
        if row["defect_labels"][0] in config.get("heterogeneous_labels", []):
            row["candidate_status"] = "HETEROGENEOUS_LABEL_REVIEW"
        else:
            row["candidate_status"] = "STRUCTURAL_SINGLE_TYPE_CANDIDATE_NOT_CERTIFIED"
    elif structural and row["n_defect_types"] > 1:
        row["candidate_status"] = "MULTITYPE_NOT_SINGLE_LABEL"
    row["issues"] = sorted(set(row["issues"]))
    return row, objects


def duplicate_groups(rows, key):
    by_hash = defaultdict(list)
    for row in rows:
        if row[key]:
            by_hash[row[key]].append(row)
    result = []
    for digest, group in sorted(by_hash.items()):
        if len(group) < 2:
            continue
        result.append({"hash": digest, "n": len(group), "paths": [r["image_path"] for r in group],
                       "partitions": sorted({r["supplied_partition"] for r in group}),
                       "population_claims": sorted({r["population_claim"] for r in group}),
                       "xml_label_sets": sorted({json.dumps(r["defect_labels"], ensure_ascii=False) for r in group}),
                       "directory_classes": sorted({r["directory_class"] for r in group}),
                       "cross_partition": len({r["supplied_partition"] for r in group}) > 1,
                       "cross_population": len({r["population_claim"] for r in group}) > 1,
                       "label_set_conflict": len({tuple(r["defect_labels"]) for r in group}) > 1})
    return result


def run_audit(root, out, config_path, workers=4):
    root, out = Path(root).resolve(), Path(out).resolve()
    if not root.is_dir() or out == root or root in out.parents:
        raise ValueError("Input must exist; output must be outside the raw directory")
    if out.exists() and any(out.iterdir()):
        raise ValueError("Output is nonempty; use a new versioned directory")
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    started = datetime.now(timezone.utc).isoformat()
    all_paths = sorted(root.rglob("*"))
    symlinks = [p.relative_to(root).as_posix() for p in all_paths if p.is_symlink()]
    paths = [p for p in all_paths if p.is_file() and not p.is_symlink()]
    images = [p for p in paths if p.suffix.lower() in SUPPORTED]
    if not images:
        raise ValueError("No images")
    xml_paths = [p for p in paths if p.suffix.lower() == ".xml"]
    index = defaultdict(list)
    for p in xml_paths:
        index[(p.parent, p.stem.casefold())].append(p)
    initial = {p.relative_to(root).as_posix(): signature(p) for p in paths}
    rows, objects = [], []
    work = ((root, p, index[(p.parent, p.stem.casefold())], config) for p in images)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i, (row, objs) in enumerate(pool.map(inspect_image, work), 1):
            rows.append(row)
            objects.extend(objs)
            if i % 1000 == 0 or i == len(images):
                print(f"decoded {i}/{len(images)}", file=sys.stderr, flush=True)
    paired = {row["xml_path"] for row in rows if row["xml_path"]}
    xml_records = []
    for p in xml_paths:
        x = parse_xml(p)
        x["xml_path"] = p.relative_to(root).as_posix()
        x["paired_by_same_directory_stem"] = x["xml_path"] in paired
        xml_records.append(x)
    byte_dups, pixel_dups = duplicate_groups(rows, "file_sha256"), duplicate_groups(rows, "pixel_sha256")
    blocked = {p for g in pixel_dups if g["cross_population"] or g["label_set_conflict"] for p in g["paths"]}
    for row in rows:
        if row["image_path"] in blocked:
            row["issues"].append("DUPLICATE_LABEL_OR_POPULATION_CONFLICT")
            row["candidate_status"] = "HOLD"
    sizes = Counter((r["width"], r["height"]) for r in rows if r["quality_status"] == "READABLE")
    class_stats = []
    for label in sorted({o["name"] for o in objects}):
        relevant = [r for r in rows if label in r["object_labels"]]
        single = [r for r in relevant if r["defect_labels"] == [label]]
        cand = [r for r in single if r["candidate_status"].startswith("STRUCTURAL_SINGLE")]
        class_stats.append({"label": label, "role": "AUXILIARY_BY_AUDIT_CONFIG" if label in config.get("auxiliary_labels", []) else "DEFECT_LABEL_CANDIDATE",
                            "object_instances": sum(o["name"] == label for o in objects),
                            "image_files": len(relevant), "single_type_files": len(single),
                            "structural_candidate_files": len(cand),
                            "structural_candidate_unique_pixels": len({r["pixel_sha256"] for r in cand})})
    final = {p.relative_to(root).as_posix(): signature(p) for p in root.rglob("*") if p.is_file() and not p.is_symlink()}
    changed = sorted(k for k in initial.keys() | final.keys() if initial.get(k) != final.get(k))
    report = {
        "schema_version": SCHEMA_VERSION, "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_root": str(root), "config_sha256": sha256_file(Path(config_path)),
        "auditor_source_sha256": sha256_file(Path(__file__)), "config": config,
        "counts": {"image_files": len(rows), "xml_files": len(xml_paths), "objects": len(objects),
                   "unique_file_hashes": len({r["file_sha256"] for r in rows if r["file_sha256"]}),
                   "unique_pixel_hashes": len({r["pixel_sha256"] for r in rows if r["pixel_sha256"]})},
        "quality_counts": dict(Counter(r["quality_status"] for r in rows)),
        "population_counts": dict(Counter(r["population_claim"] for r in rows)),
        "supplied_partition_counts": dict(Counter(r["supplied_partition"] for r in rows)),
        "xml_status_counts": dict(Counter(r["xml_status"] for r in rows)),
        "xml_parse_counts": dict(Counter(x["parse_status"] for x in xml_records)),
        "orphan_xml_files": [x["xml_path"] for x in xml_records if not x["paired_by_same_directory_stem"]],
        "label_consistency_counts": dict(Counter(r["label_consistency"] for r in rows)),
        "candidate_counts": dict(Counter(r["candidate_status"] for r in rows)),
        "issue_image_counts": dict(Counter(issue for r in rows for issue in r["issues"])),
        "dimensions": {f"{w}x{h}": n for (w, h), n in sorted(sizes.items())},
        "dimension_patterns": len(sizes), "class_statistics": class_stats,
        "byte_duplicate_summary": {"groups": len(byte_dups), "extra_files": sum(g["n"]-1 for g in byte_dups),
                                   "cross_partition_groups": sum(g["cross_partition"] for g in byte_dups),
                                   "cross_population_groups": sum(g["cross_population"] for g in byte_dups)},
        "pixel_duplicate_summary": {"groups": len(pixel_dups), "extra_files": sum(g["n"]-1 for g in pixel_dups),
                                    "cross_partition_groups": sum(g["cross_partition"] for g in pixel_dups),
                                    "cross_population_groups": sum(g["cross_population"] for g in pixel_dups),
                                    "label_set_conflict_groups": sum(g["label_set_conflict"] for g in pixel_dups)},
        "extension_counts": dict(Counter(p.suffix.lower() for p in paths)), "skipped_symlinks": symlinks,
        "input_stat_changes": changed, "source_independence": "UNVERIFIED_NO_GROUP_MAPPING",
        "semantic_certification": "NONE: machine structure audit, not NDT expert certification",
        "crop_status": "UNVERIFIED: dimensions/filenames/XML discrepancies alone do not establish crop lineage",
        "test_access": "PREPARTITION_AUDIT: supplied folder names are not a frozen final evaluation partition",
        "limitations": ["No full near-duplicate or common-source exclusion", "Directory claims and XML are not ground truth",
                        "No normality inferred from missing XML", "No pixel-to-physical-size or exposure inference",
                        "No training or splitting performed; coordinates not repaired or rescaled"]}
    out.mkdir(parents=True, exist_ok=True)
    with (out / "images.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    with (out / "xml_records.jsonl").open("w", encoding="utf-8") as f:
        for row in xml_records:
            f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    write_csv(out / "images.csv", rows, sorted({k for r in rows for k in r}))
    write_csv(out / "objects.csv", objects, ["image_id", "image_path", "xml_path", "object_index", "name", "box", "valid_actual_envelope", "valid_xml_envelope", "issues"])
    write_csv(out / "dimensions.csv", [{"width": w, "height": h, "image_files": n} for (w,h),n in sorted(sizes.items())], ["width", "height", "image_files"])
    write_csv(out / "class_statistics.csv", class_stats, list(class_stats[0]) if class_stats else ["label"])
    write_csv(out / "review_queue.csv", rows, ["image_id", "image_path", "population_claim", "directory_class", "defect_labels", "issues", "candidate_status", "semantic_status"])
    dump_json(out / "byte_duplicates.json", byte_dups)
    dump_json(out / "pixel_duplicates.json", pixel_dups)
    dump_json(out / "input_snapshot.json", initial)
    dump_json(out / "summary.json", report)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--workers", type=int, default=4)
    a = p.parse_args()
    result = run_audit(a.root, a.out, a.config, a.workers)
    print(json.dumps({k: v for k, v in result.items() if k not in {"dimensions", "config"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
