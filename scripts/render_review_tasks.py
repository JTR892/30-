"""Render a PRIVATE offline review index and fixed-window thumbnails.

Each content-identical task has one unannotated preview. All original XML object
variants remain selectable as overlays; original image/XML links stay local.
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',required=True);p.add_argument('--workers',type=int,default=4);args=p.parse_args()
out=Path(args.package).resolve();summary=json.loads((out/'summary.json').read_text());root=Path(summary['raw_root']).resolve()
if out==root or root in out.parents:raise SystemExit('Output cannot be raw data')
tasks=[json.loads(l) for l in (out/'tasks.jsonl').read_text().splitlines()]
members=[json.loads(l) for l in (out/'members.jsonl').read_text().splitlines()]
bytask={}
for r in members:bytask.setdefault(r['task_id'],[]).append(r)
preview=out/'previews';preview.mkdir(exist_ok=True)

def render(task):
 with Image.open(root/task['representative_path']) as im:a=np.asarray(im)
 low,high=np.percentile(a,[1,99]);b=np.uint8(np.clip((a.astype(np.float32)-low)/max(high-low,1),0,1)*255)
 view=ImageOps.contain(Image.fromarray(b),(640,640),Image.Resampling.LANCZOS)
 target=preview/(task['task_id']+'.jpg');view.save(target,quality=90)
 return {'task_id':task['task_id'],'display_low':float(low),'display_high':float(high),'source_width':int(a.shape[1]),'source_height':int(a.shape[0]),'preview_width':view.width,'preview_height':view.height}
settings=list(ThreadPoolExecutor(max_workers=args.workers).map(render,tasks))
(out/'preview_windows.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2)+'\n')
data=[]
for t in tasks:
 row=dict(t);row['preview']='previews/'+t['task_id']+'.jpg';row['members']=[]
 for m in bytask[t['task_id']]:
  row['members'].append({k:m[k] for k in ['image_id','image_path','xml_path','width','height','directory_class','defect_labels','xml_filename','xml_folder','xml_source_path','xml_objects','own_event_codes']})
  row['members'][-1]['image_url']=(root/m['image_path']).as_uri()
  row['members'][-1]['xml_url']=(root/m['xml_path']).as_uri() if m['xml_path'] else ''
 data.append(row)
labels={
 'EXACT_PIXEL_DUPLICATES':'相同像素内容','EXACT_FILE_DUPLICATES':'文件字节重复','DUPLICATE_CROSS_SUPPLIED_PARTITIONS':'重复跨现成分区',
 'DUPLICATE_LABEL_SET_DIFFERENCE':'同像素缺陷类别集合不同','DUPLICATE_DIRECTORY_CLAIM_DIFFERENCE':'同像素目录类别不同',
 'DUPLICATE_OBJECT_ANNOTATION_DIFFERENCE':'同像素XML对象/坐标组合不同','DIRECTORY_CLASS_ABSENT_FROM_XML':'当前目录类别未见于XML缺陷集合',
 'XML_FILENAME_IDENTITY_REVIEW':'XML filename与实际文件名待核','BOX_REVERSED':'坐标端点逆序','BOX_ZERO_SPAN_CONVENTION':'坐标零跨度，端点约定待核',
 'BOX_OUTSIDE_CURRENT_IMAGE':'坐标超出当前图像包络','BOX_MALFORMED_OR_NONFINITE':'坐标格式/数值待核','REPEATED_IDENTICAL_OBJECT_RECORD':'XML对象重复登记'}
payload=json.dumps({'summary':summary,'tasks':data,'labels':labels},ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>去重复核任务包</title><style>
body{margin:0;color:#182533;background:#f3f6fa;font:15px/1.6 system-ui,-apple-system,sans-serif}header,main{max-width:1450px;margin:auto;padding:20px}header{background:#10293a;color:white;max-width:none}header>div{max-width:1450px;margin:auto}h1{font-size:26px;margin:0 0 8px}.stats{display:flex;gap:24px;flex-wrap:wrap;font-size:17px}.notice{background:#fff4d8;padding:12px;border-left:4px solid #b98113}.filters{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}input,select,button{font:inherit;padding:7px 10px;border:1px solid #bcc8d1;border-radius:4px}input{min-width:300px}button{cursor:pointer;background:white}table{width:100%;border-collapse:collapse;background:white}td,th{padding:9px;border-bottom:1px solid #dae1e8;text-align:left}th{position:sticky;top:0;background:#e7eef4}tr:hover{background:#edf5fb}a{color:#125b90}.badge{display:inline-block;border:1px solid #b8c8d3;border-radius:3px;padding:1px 5px;margin:2px;font-size:12px}.paging{display:flex;gap:12px;align-items:center;margin:12px 0}dialog{width:min(1260px,94vw);max-height:90vh;border:1px solid #9faeb8;border-radius:8px;padding:22px}dialog::backdrop{background:#0009}.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.image{max-width:100%;max-height:560px;background:#111}pre{white-space:pre-wrap;word-break:break-all;font-size:12px;background:#f4f6f9;padding:10px}.small{font-size:13px;color:#536472}.member{padding:12px;border:1px solid #ced8e0;margin:8px 0}.csv{display:flex;gap:16px;flex-wrap:wrap;margin:14px 0}@media(max-width:800px){.detail-grid{grid-template-columns:1fr}input{min-width:180px}td,th{padding:5px}}
</style></head><body><header><div><h1>去重复核任务包 · 2026-11-27</h1><div class="stats" id="stats"></div></div></header><main><div class="notice">当前仅整理复核任务：原始文件、原始标签和坐标均保留。未纳入四类任务的图片不等于语义正确或科研资格通过。预览采用1–99百分位显示窗口；细小缺陷请打开原始16位图。零跨度框可能涉及包含端点约定，未自动修复。</div><div class="csv"><a href="复核任务总表.csv">任务总表CSV</a><a href="任务与原始文件对应.csv">原始文件对应</a><a href="全量图片覆盖账本.csv">全部图片覆盖</a><a href="未纳入本任务包的图片.csv">未纳入图片</a><a href="历史元数据参考.csv">历史元数据参考</a><a href="independent_validation.json">独立复核结果</a><a href="交付说明.md">交付说明</a></div><div class="filters"><input id="q" placeholder="搜索任务、类别、文件名或问题"><select id="priority"><option value="">全部复核顺序</option><option value="1">顺序1：类别/逆序等</option><option value="2">顺序2：命名/标注/端点等</option><option value="3">顺序3：其余重复</option></select><select id="family"><option value="">全部任务类型</option><option value="duplicates">重复及标注差异</option><option value="class_conflicts">目录/XML类别</option><option value="filename_differences">XML filename名称</option><option value="coordinates">坐标</option></select></div><div class="paging"><button id="prev">上一页</button><span id="page"></span><button id="next">下一页</button></div><table><thead><tr><th>任务</th><th>顺序</th><th>文件数</th><th>复核依据</th><th>状态</th></tr></thead><tbody id="rows"></tbody></table><p class="small">复核人员、结论、证据依据和日期留空，待实际复核后在CSV填写。此页面只读浏览，不提交或修改标签。</p></main><dialog id="detail"><button id="close">关闭</button><h2 id="detail-title"></h2><div class="detail-grid"><section><select id="variant"></select><div id="image-area"></div><p class="small">红框为当前选中的原XML缺陷候选，绿框为焊缝辅助区域；所有原XML变体保留。对零跨度/逆序框仅提供坐标记录，不绘制成正常矩形。</p></section><section id="member-list"></section></div></dialog><script id="payload" type="application/json">__DATA__</script><script>
const D=JSON.parse(document.getElementById('payload').textContent),S=D.summary,T=D.tasks;let page=0,filtered=T;const size=40,$=id=>document.getElementById(id);$('stats').textContent=`${S.deduplicated_tasks.toLocaleString()} 个去重任务 · ${S.task_member_files.toLocaleString()} 个原图文件 · 全量覆盖 ${S.source_image_files.toLocaleString()} 张`;
function node(tag,text,cls){let e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e}
function redraw(){const q=$('q').value.toLowerCase(),p=$('priority').value,f=$('family').value;filtered=T.filter(t=>(!p||String(t.priority)===p)&&(!f||t.families.includes(f))&&(!q||JSON.stringify(t).toLowerCase().includes(q)));const last=Math.max(0,Math.ceil(filtered.length/size)-1);page=Math.min(page,last);$('rows').replaceChildren();for(const t of filtered.slice(page*size,(page+1)*size)){let tr=node('tr'),td=node('td'),b=node('button',t.task_id);b.onclick=()=>show(t);td.append(b);tr.append(td,node('td',t.priority),node('td',t.member_count));let reasons=node('td');for(const c of t.issue_codes)reasons.append(node('span',D.labels[c]||c,'badge'));tr.append(reasons,node('td','待复核'));$('rows').append(tr)}$('page').textContent=`第 ${page+1}/${last+1} 页 · ${filtered.length} 个任务`;$('prev').disabled=page===0;$('next').disabled=page===last}
function overlay(t,m){let ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',`0 0 ${m.width} ${m.height}`);svg.setAttribute('class','image');svg.style.width='100%';let im=document.createElementNS(ns,'image');im.setAttribute('href',t.preview);im.setAttribute('width',m.width);im.setAttribute('height',m.height);im.setAttribute('preserveAspectRatio','none');svg.append(im);for(const o of m.xml_objects){const b=o.box;if(!b||b[2]<=b[0]||b[3]<=b[1])continue;let r=document.createElementNS(ns,'rect');r.setAttribute('x',b[0]);r.setAttribute('y',b[1]);r.setAttribute('width',b[2]-b[0]);r.setAttribute('height',b[3]-b[1]);r.setAttribute('fill','none');r.setAttribute('stroke',o.name==='焊缝'?'lime':'red');r.setAttribute('stroke-width',Math.max(m.width,m.height)/350);svg.append(r)}$('image-area').replaceChildren(svg)}
function show(t){$('detail-title').textContent=t.task_id+' · '+t.member_count+'个原始文件';$('variant').replaceChildren();$('member-list').replaceChildren();t.members.forEach((m,i)=>{let option=node('option',(i+1)+': '+m.image_path);option.value=i;$('variant').append(option);let box=node('div',undefined,'member');box.append(node('strong',m.image_path),node('p','目录：'+(m.directory_class||'无具名缺陷目录')+'；XML缺陷：'+(m.defect_labels.join('、')||'无/未知')));for(const [label,url] of [['打开原图',m.image_url],['打开XML',m.xml_url]]){if(url){let a=node('a',label);a.href=url;a.target='_blank';a.rel='noopener';box.append(a,document.createTextNode('　'))}}box.append(node('pre',JSON.stringify({xml_filename:m.xml_filename,xml_folder:m.xml_folder,xml_source_path:m.xml_source_path,objects:m.xml_objects,own_event_codes:m.own_event_codes},null,2)));$('member-list').append(box)});$('variant').onchange=()=>overlay(t,t.members[Number($('variant').value)]);overlay(t,t.members[0]);$('detail').showModal()}
$('q').oninput=()=>{page=0;redraw()};$('priority').onchange=$('family').onchange=()=>{page=0;redraw()};$('prev').onclick=()=>{page--;redraw()};$('next').onclick=()=>{page++;redraw()};$('close').onclick=()=>$('detail').close();redraw();
</script></body></html>'''
(out/'复核入口.html').write_text(html.replace('__DATA__',payload),encoding='utf-8')
print('private review index rendered:',len(tasks),'tasks,',len(members),'source members')
