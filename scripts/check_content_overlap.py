from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor
import re,json,csv
import numpy as np
from PIL import Image
import argparse
p=argparse.ArgumentParser(description='Limited filename-candidate exact-overlap search; no crop-provenance certification')
p.add_argument('--root',required=True);p.add_argument('--audit',required=True);args=p.parse_args()
root=Path(args.root).resolve();out=Path(args.audit).resolve()
if out==root or root in out.parents: raise SystemExit("Audit output must remain outside the raw data directory")
rows=[json.loads(l) for l in (out/'images.jsonl').read_text().splitlines()]
groups=defaultdict(list)
for r in rows:
 stem=Path(r['image_path']).stem.casefold();base=re.sub(r'_(?:[01]_[01]|2_0)$','',stem)
 groups[base].append(r)
items=[(k,rs) for k,rs in sorted(groups.items()) if len(rs)>1]
print('candidate name families',len(items),'files',sum(len(x) for _,x in items),flush=True)

def compare(a,b):
 ha,wa=a.shape;hb,wb=b.shape
 # Exact translation candidates from three interior anchor values; each match is
 # verified against EVERY stored pixel of the overlap, never against thumbnails.
 offsets=set()
 for fy,fx in [(.5,.5),(.33,.33),(.67,.67)]:
  ay,ax=int((ha-1)*fy),int((wa-1)*fx);v=a[ay,ax]
  if v==0 or v==65535:continue
  ys,xs=np.where(b==v)
  if len(ys)>200:continue
  offsets.update((ay-int(y),ax-int(x)) for y,x in zip(ys,xs))
 # Include identity even for constant images, while refusing low-information overlaps.
 offsets.add((0,0))
 for dy,dx in sorted(offsets,key=lambda o:abs(o[0])+abs(o[1])):
  y0,x0=max(0,dy),max(0,dx);y1,x1=min(ha,hb+dy),min(wa,wb+dx)
  if y1<=y0 or x1<=x0:continue
  area=(y1-y0)*(x1-x0)
  if area/min(a.size,b.size)<.5:continue
  aa=a[y0:y1,x0:x1];bb=b[y0-dy:y1-dy,x0-dx:x1-dx]
  if aa.size<4096 or np.unique(aa[::8,::8]).size<32:continue
  if np.array_equal(aa,bb):
   return {'dy_b_origin_in_a':dy,'dx_b_origin_in_a':dx,'overlap_pixels':area,'fraction_a':area/a.size,'fraction_b':area/b.size,'exact_containment':area==min(a.size,b.size)}
 return None

def process(item):
 key,rs=item; arrays={};links=[]
 for r in rs:
  with Image.open(root/r['image_path']) as im:arrays[r['image_path']]=np.asarray(im).copy()
 for ra,rb in combinations(rs,2):
  a,b=arrays[ra['image_path']],arrays[rb['image_path']]
  if a.ndim!=2 or b.ndim!=2:continue
  match=compare(a,b)
  if match:
   links.append(dict(match,a=ra['image_path'],b=rb['image_path'],name_family=key,partition_a=ra['supplied_partition'],partition_b=rb['supplied_partition'],population_a=ra['population_claim'],population_b=rb['population_claim']))
 return key,len(rs),links
links=[];families=0
with ThreadPoolExecutor(max_workers=4) as pool:
 for i,(key,n,ls) in enumerate(pool.map(process,items),1):
  links.extend(ls);families+=bool(ls)
  if i%500==0:print('family comparisons',i,'exact overlap links',len(links),flush=True)
parents={r['image_path']:r['image_path'] for r in rows}
def find(x):
 while parents[x]!=x:
  parents[x]=parents[parents[x]];x=parents[x]
 return x
for link in links:
 a,b=find(link['a']),find(link['b'])
 if a!=b:parents[b]=a
# Also connect full pixel-equal files found outside filename families.
byhash={}
for r in rows:
 h=r['pixel_sha256'];p=r['image_path']
 if h in byhash:
  a,b=find(p),find(byhash[h]);parents[b]=a
 else:byhash[h]=p
comp=defaultdict(list)
for r in rows:comp[find(r['image_path'])].append(r)
components=[]
for i,rs in enumerate(sorted(comp.values(),key=lambda rs:rs[0]['image_path'])):
 if len(rs)>1:components.append({'component':f'exact-content-{i:05d}','n':len(rs),'paths':[r['image_path'] for r in rs],'partitions':sorted({r['supplied_partition'] for r in rs}),'population_claims':sorted({r['population_claim'] for r in rs}),'xml_label_sets':sorted({json.dumps(r['defect_labels'],ensure_ascii=False) for r in rs})})
report={'method':'filename-candidate pairs only; >=50% smaller-image exact uint16 overlap; 4096 pixels minimum and >=32 sampled levels; plus full-pixel duplicates',
 'all_possible_pairs_searched':False,'name_candidate_families':len(items),'name_candidate_files':sum(len(rs) for _,rs in items),'families_with_verified_links':families,'exact_overlap_links':len(links),'linked_image_files':len({p for l in links for p in [l['a'],l['b']]}),'nonidentical_shift_links':sum(bool(l['dx_b_origin_in_a'] or l['dy_b_origin_in_a']) for l in links),
 'components_including_singletons':len(comp),'nontrivial_components':len(components),'component_size_counts':dict(Counter(len(rs) for rs in comp.values())),
 'cross_partition_components':sum(len(c['partitions'])>1 for c in components),'cross_population_components':sum(len(c['population_claims'])>1 for c in components),
 'interpretation':'Exact overlapping stored content establishes shared image content, not independent weld IDs, original full-film dimensions, crop author or date. Candidate filename families without matches remain unverified.'}
(out/'exact_overlap_links.json').write_text(json.dumps(links,ensure_ascii=False,indent=2)+'\n')
(out/'content_components.json').write_text(json.dumps(components,ensure_ascii=False,indent=2)+'\n')
(out/'crop_overlap_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
with (out/'content_group_candidates.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['image_id','image_path','content_component','provenance_status']);w.writeheader()
 for i,rs in enumerate(sorted(comp.values(),key=lambda rs:rs[0]['image_path'])):
  for r in rs:w.writerow({'image_id':r['image_id'],'image_path':r['image_path'],'content_component':f'exact-content-{i:05d}','provenance_status':'CONTENT_CONNECTED_NOT_VERIFIED_WELD_ID'})
print(json.dumps(report,ensure_ascii=False,indent=2))
