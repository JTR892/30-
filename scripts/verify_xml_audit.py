from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from xml.dom import minidom
import hashlib,json,sys
from PIL import Image
import argparse
p=argparse.ArgumentParser(description='Independent rehash, PIL headers and minidom XML verification; private output only')
p.add_argument('--root',required=True);p.add_argument('--audit',required=True);args=p.parse_args()
root=Path(args.root).resolve();out=Path(args.audit).resolve()
if out==root or root in out.parents: raise SystemExit("Audit output must remain outside the raw data directory")
rows=[json.loads(l) for l in (out/'images.jsonl').read_text().splitlines()]
summary=json.loads((out/'summary.json').read_text()); errors=[];actual=Counter(); label_counts=Counter(); boxes=0

def text_at(node,tag):
 xs=node.getElementsByTagName(tag)
 return ''.join(c.data for c in xs[0].childNodes if c.nodeType==c.TEXT_NODE).strip() if xs else ''
def check(row):
 p=root/row['image_path'];err=[];h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 if h.hexdigest()!=row['file_sha256']:err.append('image_hash_changed')
 with Image.open(p) as im:
  if (im.width,im.height,im.mode)!=(row['width'],row['height'],row['mode']):err.append('header_disagreement')
 labels=[];nobj=0;bad=0
 if row['xml_path']:
  raw=(root/row['xml_path']).read_bytes()
  if hashlib.sha256(raw).hexdigest()!=row['xml_sha256']:err.append('xml_hash_changed')
  probe=raw.replace(b'\x00',b'').upper()
  if b'<!DOCTYPE' in probe or b'<!ENTITY' in probe: raise ValueError('DTD/ENTITY rejected')
  doc=minidom.parseString(raw);objs=doc.getElementsByTagName('object');nobj=len(objs)
  labels=[text_at(o,'name') for o in objs]
  size=doc.getElementsByTagName('size')[0]
  if (int(text_at(size,'width')),int(text_at(size,'height')))!=(row['width'],row['height']):err.append('independent_xml_size_mismatch')
  unique=sorted(set(labels)-{'焊缝'})
  if unique!=row['defect_labels']:err.append('label_set_disagreement')
  for o in objs:
   try:
    x1,y1,x2,y2=[float(text_at(o,k)) for k in ['xmin','ymin','xmax','ymax']]
    valid=0<=x1<x2<=row['width'] and 0<=y1<y2<=row['height']
   except Exception:valid=False
   bad+=not valid
  if bad!=row['boxes_invalid_actual']:err.append('box_disagreement')
  doc.unlink()
 return row['image_path'],err,labels,nobj
with ThreadPoolExecutor(max_workers=4) as ex:
 for i,(path,err,labels,nobj) in enumerate(ex.map(check,rows),1):
  if err:errors.append([path,err])
  label_counts.update(labels);boxes+=nobj
  if i%5000==0:print('independent verified',i,flush=True)
image_paths={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.suffix.lower() in ['.tif','.tiff','.png','.jpg','.jpeg','.bmp']}
if image_paths!={r['image_path'] for r in rows}:errors.append(['COVERAGE','image list disagreement'])
if boxes!=summary['counts']['objects']:errors.append(['COUNTS','object count disagreement'])
for c in summary['class_statistics']:
 if label_counts[c['label']]!=c['object_instances']:errors.append([c['label'],'class count disagreement'])
result={'verification':'INDEPENDENT_BYTE_REHASH_PIL_HEADERS_MINIDOM_XML','image_files_checked':len(rows),'xml_files_checked':sum(bool(r['xml_path']) for r in rows),'objects_recounted':boxes,'object_label_counts':dict(label_counts),'errors':errors,'passed':not errors}
(out/'independent_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))

if errors: raise SystemExit(2)
