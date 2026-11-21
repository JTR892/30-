"""Read-only image inventory; never infer defect labels from absent annotations."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from PIL import Image

SUPPORTED = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
UNSUPPORTED = {".dcm", ".dicom", ".raw"}
FIELDS = ["image_id", "image_path", "width", "height", "mode", "format", "sha256", "quality_status", "annotation_candidates", "annotation_status", "defect_classes", "defect_count", "group_id"]

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def audit(root, out):
    root, out = Path(root).resolve(), Path(out).resolve()
    if not root.is_dir():
        raise ValueError("Dataset root does not exist or is not a directory")
    if out == root or root in out.parents:
        raise ValueError("Audit output must be outside raw dataset root")
    paths = sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink())
    images = [p for p in paths if p.suffix.lower() in SUPPORTED]
    if not images:
        raise ValueError("No supported images found; refusing an empty successful audit")
    sidecars = {}
    for p in paths:
        if p.suffix.lower() in {".json", ".xml", ".txt"}:
            sidecars.setdefault((p.parent, p.stem), []).append(str(p.relative_to(root)))
    rows = []
    for p in images:
        rel = p.relative_to(root).as_posix()
        row = dict.fromkeys(FIELDS, "")
        row.update(image_id=hashlib.sha256(rel.encode()).hexdigest(), image_path=rel,
                   annotation_status="UNREVIEWED", quality_status="UNREADABLE")
        # Only same-directory sidecars are candidates; this is not a schema parser.
        candidates = sidecars.get((p.parent, p.stem), [])
        row["annotation_candidates"] = json.dumps(candidates, ensure_ascii=False)
        try:
            row["sha256"] = sha256_file(p)
            with Image.open(p) as im:
                row.update(width=im.width, height=im.height, mode=im.mode, format=im.format)
                im.load()
                row["quality_status"] = "READABLE" if getattr(im, "n_frames", 1) == 1 else "MULTIFRAME_REVIEW"
        except Exception as e:
            row["quality_status"] = "UNREADABLE:" + type(e).__name__
        rows.append(row)
    hashes = Counter(r["sha256"] for r in rows if r["sha256"])
    report = {
        "dataset_root": str(root), "n_image_files": len(rows),
        "quality_counts": dict(Counter(r["quality_status"] for r in rows)),
        "duplicate_hash_groups": sum(n > 1 for n in hashes.values()),
        "duplicate_extra_files": sum(n - 1 for n in hashes.values()),
        "dimensions": dict(Counter(f'{r["width"]}x{r["height"]}' for r in rows)),
        "unsupported_image_files": [str(p.relative_to(root)) for p in paths if p.suffix.lower() in UNSUPPORTED],
        "all_extension_counts": dict(Counter(p.suffix.lower() for p in paths)),
        "label_statistics": "NOT_COMPUTED: annotation schema and taxonomy not supplied",
        "group_audit": "PENDING", "normal_images": "UNKNOWN"
    }
    out.mkdir(parents=True, exist_ok=True)
    with (out / "manifest.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    (out / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report

def main():
    p = argparse.ArgumentParser(); p.add_argument("--root", required=True); p.add_argument("--out", required=True)
    a = p.parse_args()
    try:
        print(json.dumps(audit(a.root, a.out), ensure_ascii=False, indent=2))
    except ValueError as e:
        p.exit(2, str(e) + "\n")

if __name__ == "__main__": main()

