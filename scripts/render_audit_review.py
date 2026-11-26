from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
import argparse
p=argparse.ArgumentParser(description='Render a preselected PRIVATE audit gallery; never publish industrial images')
p.add_argument('--root',required=True);p.add_argument('--audit',required=True);p.add_argument('--font',required=True);args=p.parse_args()
root=Path(args.root).resolve();out=Path(args.audit).resolve()
if out==root or root in out.parents: raise SystemExit("Audit output must remain outside the raw data directory")
v=out/'visual'
rows=json.loads((v/'selection.json').read_text());objects={}
import csv
for r in csv.DictReader((out/'objects.csv').open(encoding='utf-8-sig')):
 objects.setdefault(r['image_path'],[]).append({'name':r['name'],'box':json.loads(r['box']),'valid':r['valid_actual_envelope']=='True'})
font_path=args.font
font=ImageFont.truetype(font_path,20);small=ImageFont.truetype(font_path,16)
for batch in range((len(rows)+5)//6):
 sheet=Image.new('RGB',(1800,1780),'#eeeeee');d=ImageDraw.Draw(sheet)
 d.text((20,8),f'预分区影像抽查 {batch+1} | 原始16位像素的1–99百分位显示，非诊断结论；红框为XML候选；绿框为焊缝',font=font,fill='black')
 for idx,r in enumerate(rows[batch*6:(batch+1)*6],batch*6):
  x=(idx%2)*900;y=50+((idx%6)//2)*570
  with Image.open(root/r['image_path']) as im:a=np.asarray(im)
  lo,hi=np.percentile(a,[1,99]);gray=Image.fromarray(np.uint8(np.clip((a.astype(float)-lo)/max(hi-lo,1),0,1)*255)).convert('RGB')
  overlay=gray.copy();od=ImageDraw.Draw(overlay)
  valid=[o for o in objects.get(r['image_path'],[]) if o['valid']]
  for o in valid:
   b=o['box'];od.rectangle(b,outline='lime' if o['name']=='焊缝' else 'red',width=max(2,min(gray.size)//200))
  fitted=ImageOps.contain(overlay,(430,390));sheet.paste(fitted,(x+10+(430-fitted.width)//2,y+95+(390-fitted.height)//2))
  defects=[o for o in valid if o['name']!='焊缝']
  if defects:
   o=max(defects,key=lambda o:(o['box'][2]-o['box'][0])*(o['box'][3]-o['box'][1]));b=o['box'];pad=max(20,int(max(b[2]-b[0],b[3]-b[1])*.5))
   crop=(max(0,int(b[0])-pad),max(0,int(b[1])-pad),min(gray.width,int(b[2])+pad),min(gray.height,int(b[3])+pad))
  else:crop=(gray.width//4,gray.height//4,gray.width*3//4,gray.height*3//4)
  zoom=ImageOps.contain(gray.crop(crop),(430,390));sheet.paste(zoom,(x+455+(430-zoom.width)//2,y+95+(390-zoom.height)//2))
  sample=f'A{idx+1:02d}';r['sample_id']=sample;r['display_window']=[float(lo),float(hi)];r['zoom_crop_xyxy']=list(crop)
  # Local IDs map to private paths in selection.json, never uploaded.
  d.text((x+10,y),f'{sample} {r["width"]}×{r["height"]} | {r["selection_reason"]}',font=font,fill='black')
  d.text((x+10,y+28),'目录: '+(r['directory_class'] or 'good(用户称合格)')+' | XML: '+','.join(r['defect_labels']),font=font,fill='black')
  d.text((x+10,y+57),'左:有效XML框叠加  右:最大缺陷候选框周边(不叠框)',font=small,fill='black')
  iss=', '.join(r['issues']) or '结构无异常；语义待专家复核'
  for j in range(0,min(len(iss),150),66):d.text((x+10,y+492+j//66*22),iss[j:j+66],font=small,fill='black')
 sheet.save(v/f'contact_{batch+1:02d}.jpg',quality=93)
(v/'selection.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print('rendered',len(rows),'slots')
