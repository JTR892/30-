"""Image-level stratified split; labels are isolated from model-facing manifests."""
import argparse,csv,json,random,os
from collections import Counter,defaultdict
from pathlib import Path
LABELS=("defect","no_defect")
IMAGE_FIELDS=["image_id","image_path","sha256"]
def read_csv(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def write_csv(path,fields,rows):
    with Path(path).open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
def make_splits(manifest,out,seed=17,partition_seed=20261122):
    rows=read_csv(manifest)
    if not rows or len({r.get("image_id") for r in rows})!=len(rows): raise ValueError("Empty manifest or duplicate image IDs")
    for r in rows:
        if r.get("quality_status")!="READABLE": raise ValueError("Resolve unreadable/multiframe images before split")
        if r.get("binary_label") not in LABELS: raise ValueError("Every image needs explicit defect/no_defect label mapping")
        if not r.get("sha256"): raise ValueError("Every image needs SHA256")
    hashes=defaultdict(list)
    for r in rows: hashes[r["sha256"]].append(r)
    unique=[]; removed=[]
    for digest,group in hashes.items():
        if len({r["binary_label"] for r in group})>1: raise ValueError("Exact duplicate content has conflicting binary labels; review before split")
        group=sorted(group,key=lambda r:r["image_id"]); unique.append(group[0]); removed.extend(x["image_id"] for x in group[1:])
    pools={label:[] for label in LABELS}
    for r in unique: pools[r["binary_label"]].append(r)
    train,cal,test=[],[],[]
    for i,label in enumerate(LABELS):
        group=list(pools[label])
        if len(group)<10: raise ValueError(f"Too few unique readable images in class {label}")
        random.Random(partition_seed+i).shuffle(group)
        nt=max(1,round(.1*len(group))); nc=max(1,round(.1*len(group)))
        test.extend(group[:nt]); cal.extend(group[nt:nt+nc]); train.extend(group[nt+nc:])
    random.Random(seed).shuffle(train)
    sets={"train_10":train[:max(1,round(.1*len(train)))],"train_50":train[:max(1,round(.5*len(train)))],"train_100":train,"calibration":cal,"test":test}
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    for name,selected in sets.items():
        write_csv(out/f"{name}.csv",IMAGE_FIELDS,[{k:r[k] for k in IMAGE_FIELDS} for r in sorted(selected,key=lambda x:x["image_id"])])
    locked_path=out/"test_labels.locked.csv"
    write_csv(locked_path,["image_id","binary_label"],[{"image_id":r["image_id"],"binary_label":r["binary_label"]} for r in sorted(test,key=lambda x:x["image_id"])])
    try: os.chmod(locked_path,0o600)
    except OSError: pass
    counts={n:{"images":len(v),"classes":dict(Counter(r["binary_label"] for r in v))} for n,v in sets.items()}
    report={"partition_seed":partition_seed,"training_subset_seed":seed,"split_unit":"image","partition_strategy":"label-stratified 80/10/10; disclose stratification","training_subset_strategy":"nested random sampling within train; label-blind","counts":counts,"unique_images_after_exact_deduplication":len(unique),"removed_exact_duplicate_count":len(removed),"removed_exact_duplicate_image_ids":sorted(removed),"test_labels_file":"test_labels.locked.csv","test_label_file_mode":"owner read/write where POSIX permissions are supported; this is an operational safeguard, not encryption","model_manifests_include_labels":False,"original_film_or_weld_grouping":"NOT_PERFORMED","limitations":["Image-level split does not establish original-film/weld independence.","SHA256 does not detect all near-duplicates or crops from shared sources.","Labels are used for partition stratification, not representation training or K-means."]}
    (out/"split_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument("--manifest",required=True);p.add_argument("--out",required=True);p.add_argument("--seed",type=int,default=17);p.add_argument("--partition-seed",type=int,default=20261122);a=p.parse_args()
    p.exit(2,"Legacy v0.4 image-only split CLI is disabled for active v0.5 research; resolve source groups and taxonomy first\n")
if __name__=="__main__":main()
