"""Read-only audit for cropped weld radiographs with explicit binary label mapping."""
import argparse, csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

SUPPORTED={".png",".jpg",".jpeg",".tif",".tiff",".bmp"}
UNSUPPORTED={".dcm",".dicom",".raw"}
FIELDS=["image_id","image_path","width","height","mode","format","sha256","quality_status","binary_label","label_source","annotation_candidates","annotation_status"]

def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def load_label_map(path):
    if path is None: return {}
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data,dict) or not data or set(data.values())!={"defect","no_defect"}:
        raise ValueError("Label map must map actual folder names to exactly defect and no_defect")
    return data

def audit(root,out,label_map_path=None):
    root,out=Path(root).resolve(),Path(out).resolve()
    if not root.is_dir(): raise ValueError("Dataset root does not exist")
    if out==root or root in out.parents: raise ValueError("Audit output must be outside raw data")
    label_map=load_label_map(label_map_path)
    paths=sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink())
    images=[p for p in paths if p.suffix.lower() in SUPPORTED]
    if not images: raise ValueError("No supported images found")
    sidecars=defaultdict(list)
    for p in paths:
        if p.suffix.lower() in {".xml",".json",".txt"}: sidecars[(p.parent,p.stem)].append(p.relative_to(root).as_posix())
    rows=[]
    for p in images:
        rel=p.relative_to(root); top=rel.parts[0] if len(rel.parts)>1 else ""
        label=label_map.get(top,"")
        row=dict.fromkeys(FIELDS,"")
        row.update(image_id=hashlib.sha256(rel.as_posix().encode()).hexdigest(),image_path=rel.as_posix(),
                   quality_status="UNREADABLE",binary_label=label,label_source=top if label else "",annotation_status="UNREVIEWED")
        row["annotation_candidates"]=json.dumps(sidecars.get((p.parent,p.stem),[]),ensure_ascii=False)
        try:
            row["sha256"]=sha256_file(p)
            with Image.open(p) as im:
                row.update(width=im.width,height=im.height,mode=im.mode,format=im.format or "")
                im.load(); row["quality_status"]="READABLE" if getattr(im,"n_frames",1)==1 else "MULTIFRAME_REVIEW"
        except Exception as e: row["quality_status"]="UNREADABLE:"+type(e).__name__
        rows.append(row)
    hashes=defaultdict(list)
    for row in rows:
        if row["sha256"]: hashes[row["sha256"]].append(row)
    dup=[g for g in hashes.values() if len(g)>1]
    conflicts=[g for g in dup if len({x["binary_label"] for x in g})>1]
    out.mkdir(parents=True,exist_ok=True)
    with (out/"manifest.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    report={"dataset_root":str(root),"sample_unit":"cropped weld-region image","n_image_files":len(rows),
      "readable_image_files":sum(x["quality_status"]=="READABLE" for x in rows),
      "quality_counts":dict(Counter(x["quality_status"] for x in rows)),
      "label_map_supplied":bool(label_map),"label_counts":dict(Counter(x["binary_label"] for x in rows if x["binary_label"])),
      "unmapped_label_images":sum(not x["binary_label"] for x in rows),
      "duplicate_sha256_groups":len(dup),"duplicate_extra_files":sum(len(g)-1 for g in dup),
      "conflicting_duplicate_groups":len(conflicts),
      "dimensions":dict(Counter(f'{x["width"]}x{x["height"]}' for x in rows if x["width"])),
      "unsupported_image_files":[p.relative_to(root).as_posix() for p in paths if p.suffix.lower() in UNSUPPORTED],
      "original_film_trace":"NOT_REQUIRED_AND_NOT_PERFORMED",
      "source_independence":"NOT_ESTABLISHED_BY_IMAGE_LEVEL_AUDIT",
      "xml_status":"CANDIDATE_PATHS_ONLY; NOT_PARSED_OR_VALIDATED"}
    (out/"audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",required=True); p.add_argument("--out",required=True); p.add_argument("--label-map")
    a=p.parse_args()
    try: print(json.dumps(audit(a.root,a.out,a.label_map),ensure_ascii=False,indent=2))
    except (ValueError,OSError,json.JSONDecodeError) as e: p.exit(2,str(e)+"\n")
if __name__=="__main__": main()
