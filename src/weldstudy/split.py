"""Deterministic group partitions and nested subsets; no label-guided sampling."""
import argparse
import csv
import json
import random
from pathlib import Path

def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def make_splits(manifest, group_file, out, seed=17, partition_seed=20261122):
    rows, mapped = read_csv(manifest), read_csv(group_file)
    groups = {}
    for r in mapped:
        if not r.get("image_id") or not r.get("group_id"):
            raise ValueError("Group mapping has missing image_id/group_id")
        if r["image_id"] in groups:
            raise ValueError("Duplicate image_id in group mapping")
        groups[r["image_id"]] = r["group_id"]
    if not rows or len({r["image_id"] for r in rows}) != len(rows):
        raise ValueError("Empty manifest or duplicate image_id")
    for r in rows:
        if r["quality_status"] != "READABLE":
            raise ValueError("Resolve/exclude unreadable and multiframe images in a documented audited manifest first")
        if not r.get("sha256") or r["image_id"] not in groups:
            raise ValueError("Every image requires a content hash and verified group mapping")
    hash_groups = {}
    for r in rows:
        group = groups[r["image_id"]]
        if r["sha256"] in hash_groups and hash_groups[r["sha256"]] != group:
            raise ValueError("Exact duplicate content spans groups: merge connected provenance components before splitting")
        hash_groups[r["sha256"]] = group
    # Drop exact duplicates deterministically; record them. Near duplicates remain a human audit requirement.
    unique, seen, removed = [], set(), []
    for r in sorted(rows, key=lambda r: r["image_id"]):
        if r["sha256"] in seen: removed.append(r["image_id"])
        else: unique.append(r); seen.add(r["sha256"])
    keys = sorted({groups[r["image_id"]] for r in unique})
    if len(keys) < 10:
        raise ValueError("At least 10 independent groups required for this 80/10/10 scaffold; redesign if fewer")
    random.Random(partition_seed).shuffle(keys)
    ntest = max(1, round(len(keys) * .1)); ncal = ntest
    test, cal, train = keys[:ntest], keys[ntest:ntest+ncal], keys[ntest+ncal:]
    random.Random(seed).shuffle(train)
    sets = {"test": set(test), "calibration": set(cal), "train_100": set(train),
            "train_50": set(train[:max(1, round(len(train)*.5))]),
            "train_10": set(train[:max(1, round(len(train)*.1))])}
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, selected in sets.items():
        selected_rows = [{"image_id": r["image_id"], "image_path": r["image_path"], "sha256": r["sha256"], "group_id": groups[r["image_id"]]} for r in unique if groups[r["image_id"]] in selected]
        with (out / f"{name}.csv").open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=["image_id", "image_path", "sha256", "group_id"]); w.writeheader(); w.writerows(selected_rows)
        counts[name] = {"groups": len(selected), "images": len(selected_rows)}
    report = {"subset_seed": seed, "partition_seed": partition_seed, "ratio_unit": "independent groups, not exact image counts", "counts": counts,
              "removed_exact_duplicate_image_ids": removed,
              "limitations": "Only supplied provenance and exact file hashes checked; near-duplicates and group semantics need review"}
    (out / "split_report.json").write_text(json.dumps(report, indent=2))
    return report

def main():
    p=argparse.ArgumentParser(); p.add_argument("--manifest",required=True); p.add_argument("--groups",required=True); p.add_argument("--out",required=True); p.add_argument("--seed",type=int,default=17)
    a=p.parse_args()
    try: print(json.dumps(make_splits(a.manifest,a.groups,a.out,a.seed),indent=2))
    except (ValueError, KeyError, FileNotFoundError) as e: p.exit(2,str(e)+"\n")

if __name__ == "__main__": main()

