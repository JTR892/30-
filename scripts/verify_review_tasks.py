"""Independently recheck every source image/XML and the queue's assigned/rest sets.

Uses minidom rather than the inventory's ElementTree parser. All raw content is
read again. No imports from the task builder's rule functions are used.
"""
import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from xml.dom import minidom
import numpy as np
from PIL import Image


def load_jsonl(p):return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x]


def content_name_relation(a,b):
    b=PureWindowsPath(b or '').name
    if a==b:return 'EXACT'
    p,q=Path(a),Path(b)
    if b and p.stem==q.stem and p.suffix.lower() in ('.tif','.tiff') and q.suffix.lower() in ('.tif','.tiff'):
        return 'TIFF_EXTENSION_EQUIVALENT'
    return 'IDENTITY_REVIEW'


def node_text(node,key):
    nodes=node.getElementsByTagName(key)
    return ''.join(n.data for n in nodes[0].childNodes if n.nodeType==n.TEXT_NODE).strip() if nodes else ''


def verify(root,audit,package,workers=4):
    root,audit,package=[Path(p).resolve() for p in (root,audit,package)]
    if root==package or root in package.parents:raise ValueError('Output must be outside raw data')
    rows=load_jsonl(audit/'images.jsonl');cached_xml={x['xml_path']:x for x in load_jsonl(audit/'xml_records.jsonl')}
    tasks=load_jsonl(package/'tasks.jsonl');events=load_jsonl(package/'events.jsonl')
    coverage=load_jsonl(package/'coverage.jsonl');members=load_jsonl(package/'members.jsonl')
    names=load_jsonl(package/'names.jsonl');metadata=load_jsonl(package/'metadata.jsonl')
    cfg=json.loads((audit/'summary.json').read_text())['config'];aux=set(cfg['auxiliary_labels']);known=set(cfg['known_defect_labels'])
    errors=[];source_changed=[];actual=[]
    def worker(row):
        r=dict(row);bad=[];p=root/r['image_path'];st=p.stat();raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=r['file_sha256']:bad.append('RAW_IMAGE_CONTENT_CHANGED')
        if [st.st_size,st.st_mtime_ns]!=[r['file_bytes'],r['mtime_ns']]:bad.append('RAW_IMAGE_STAT_CHANGED')
        ph=hashlib.sha256()
        with Image.open(io.BytesIO(raw)) as im:
            if [im.width,im.height,im.mode,getattr(im,'n_frames',1)]!=[r['width'],r['height'],r['mode'],r['frames']]:bad.append('RAW_HEADER_CHANGED')
            for frame in range(getattr(im,'n_frames',1)):
                im.seek(frame);im.load();a=np.asarray(im)
                ph.update(json.dumps([frame,a.shape,a.dtype.str],separators=(',',':')).encode());ph.update(a.tobytes(order='C'))
        r['fresh_pixel_sha256']=ph.hexdigest()
        if r['fresh_pixel_sha256']!=r['pixel_sha256']:bad.append('PIXEL_DIGEST_DISAGREEMENT')
        x=None
        if r['xml_path']:
            raw=(root/r['xml_path']).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=r['xml_sha256']:bad.append('RAW_XML_CONTENT_CHANGED')
            probe=raw.replace(b'\x00',b'').upper()
            if b'<!DOCTYPE' in probe or b'<!ENTITY' in probe:raise ValueError('DTD/ENTITY not accepted')
            doc=minidom.parseString(raw);size=doc.getElementsByTagName('size')[0]
            x={'filename':node_text(doc,'filename'),'folder':node_text(doc,'folder'),'source_path':node_text(doc,'path'),
               'width':int(node_text(size,'width')),'height':int(node_text(size,'height')),'objects':[]}
            for i,o in enumerate(doc.getElementsByTagName('object')):
                try:b=[float(node_text(o,k)) for k in ['xmin','ymin','xmax','ymax']]
                except (ValueError,TypeError):b=None
                if b is not None and not all(math.isfinite(v) for v in b):b=None
                x['objects'].append({'object_index':i,'name':node_text(o,'name'),'box':b})
            doc.unlink()
            prior=cached_xml[r['xml_path']]
            if any(x[k]!=prior[k] for k in ['filename','folder','source_path','width','height']):bad.append('XML_HEADER_RECOMPUTATION_DISAGREEMENT')
            expected=[{k:o[k] for k in ['object_index','name','box']} for o in prior['objects']]
            if x['objects']!=expected:bad.append('XML_OBJECT_RECOMPUTATION_DISAGREEMENT')
        if p.stat().st_mtime_ns!=st.st_mtime_ns or p.stat().st_size!=st.st_size:bad.append('IMAGE_CHANGED_WHILE_RECHECKING')
        r['fresh_xml']=x;r['recheck_errors']=bad
        return r
    with ThreadPoolExecutor(max_workers=workers) as pool:
        with (package/'raw_rechecks.jsonl').open('w',encoding='utf-8') as f:
            for i,r in enumerate(pool.map(worker,rows),1):
                if r['recheck_errors']:errors.append([r['image_path'],r['recheck_errors']]);source_changed.append(r['image_path'])
                actual.append(r);f.write(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n')
                if i%3000==0 or i==len(rows):print(f'raw and residual recheck {i}/{len(rows)}',flush=True)
    # Recompute all four rule families from raw data, not cached issues or task labels.
    expected=defaultdict(set);metadata_expected=Counter();name_expected={};groups=defaultdict(list)
    for r in actual:groups[r['fresh_pixel_sha256']].append(r)
    def record(pixel,family,code,ident=None,object_index=None):
        expected[pixel].add((family,code,ident,object_index))
    for h,g in groups.items():
        ids=tuple(sorted(r['image_id'] for r in g))
        if len(g)>1:
            record(h,'duplicates','EXACT_PIXEL_DUPLICATES')
            if len({r['file_sha256'] for r in g})<len(g):record(h,'duplicates','EXACT_FILE_DUPLICATES')
            if len({r['supplied_partition'] for r in g})>1:record(h,'duplicates','DUPLICATE_CROSS_SUPPLIED_PARTITIONS')
            if len({tuple(sorted(set(o['name'] for o in r['fresh_xml']['objects'])-aux)) if r['fresh_xml'] else () for r in g})>1:
                record(h,'duplicates','DUPLICATE_LABEL_SET_DIFFERENCE')
            if len({r['directory_class'] for r in g})>1:record(h,'duplicates','DUPLICATE_DIRECTORY_CLAIM_DIFFERENCE')
            signatures=[]
            for r in g:
                signatures.append(None if r['fresh_xml'] is None else tuple(sorted((o['name'],tuple(o['box']) if o['box'] is not None else ()) for o in r['fresh_xml']['objects'])))
            if len(set(signatures))>1:record(h,'duplicates','DUPLICATE_OBJECT_ANNOTATION_DIFFERENCE')
        for r in g:
            x=r['fresh_xml'];ident=r['image_id']
            if x is None:continue
            labs=set(o['name'] for o in x['objects'])-aux
            if r['directory_class'] and r['directory_class'] not in labs:record(h,'class_conflicts','DIRECTORY_CLASS_ABSENT_FROM_XML',ident)
            rel=content_name_relation(Path(r['image_path']).name,x['filename']);name_expected[ident]=rel
            if rel=='IDENTITY_REVIEW':record(h,'filename_differences','XML_FILENAME_IDENTITY_REVIEW',ident)
            keys=[(o['name'],tuple(o['box'] or [])) for o in x['objects']]
            if len(set(keys))<len(keys):record(h,'duplicates','REPEATED_IDENTICAL_OBJECT_RECORD',ident)
            for o in x['objects']:
                b=o['box'];idx=o['object_index']
                if b is None:record(h,'coordinates','BOX_MALFORMED_OR_NONFINITE',ident,idx);continue
                x1,y1,x2,y2=b
                if x1>x2 or y1>y2:record(h,'coordinates','BOX_REVERSED',ident,idx)
                elif x1==x2 or y1==y2:record(h,'coordinates','BOX_ZERO_SPAN_CONVENTION',ident,idx)
                if any([x1<0,x2<0,y1<0,y2<0,x1>r['width'],x2>r['width'],y1>r['height'],y2>r['height']]):
                    record(h,'coordinates','BOX_OUTSIDE_CURRENT_IMAGE',ident,idx)
            if x['folder'] in known and x['folder'] not in labs:metadata_expected[(ident,'HISTORICAL_XML_FOLDER_LABEL_ABSENT')]+=1
            if x['folder'] in known and x['folder']!=r['directory_class']:metadata_expected[(ident,'CURRENT_DIRECTORY_VS_HISTORICAL_XML_FOLDER')]+=1
            sb=PureWindowsPath(x['source_path']).name
            if sb and sb!=x['filename']:metadata_expected[(ident,'SOURCE_PATH_BASENAME_DIFFERS_FROM_XML_FILENAME')]+=1
    tasks_by={t['task_id']:t for t in tasks};actual_events=defaultdict(set)
    if len(tasks_by)!=len(tasks) or len({t['pixel_sha256'] for t in tasks})!=len(tasks):
        errors.append(['DUPLICATED_TASK_ID_OR_CONTENT_GROUP'])
    if len({e['event_id'] for e in events})!=len(events):errors.append(['DUPLICATED_EVENT_ID'])
    for e in events:
        t=tasks_by[e['task_id']];ident=e['image_ids'][0] if len(e['image_ids'])==1 and e['code'] not in {
          'EXACT_PIXEL_DUPLICATES','EXACT_FILE_DUPLICATES','DUPLICATE_CROSS_SUPPLIED_PARTITIONS','DUPLICATE_LABEL_SET_DIFFERENCE','DUPLICATE_DIRECTORY_CLAIM_DIFFERENCE','DUPLICATE_OBJECT_ANNOTATION_DIFFERENCE'} else None
        if ident is None and set(e['image_ids'])!=set(t['image_ids']):
            errors.append(['GROUP_EVENT_MEMBER_DIFFERENCE',e['event_id']])
        actual_events[t['pixel_sha256']].add((e['family'],e['code'],ident,e['evidence'].get('object_index')))
    for h in expected.keys()|actual_events.keys():
        if expected[h]!=actual_events[h]:errors.append(['EVENT_SET_DIFFERENCE',h,repr(expected[h]-actual_events[h]),repr(actual_events[h]-expected[h])])
    if len(events)!=sum(len(ev) for ev in expected.values()):errors.append(['EVENT_MULTIPLICITY_DIFFERENCE'])
    expected_hashes={h for h,es in expected.items() if es};actual_hashes={t['pixel_sha256'] for t in tasks}
    if expected_hashes!=actual_hashes:errors.append(['TASK_GROUP_SET_DIFFERENCE'])
    all_ids={r['image_id'] for r in actual};task_ids={r['image_id'] for r in actual if r['fresh_pixel_sha256'] in expected_hashes}
    remainder=all_ids-task_ids;cov={r['image_id']:r for r in coverage}
    if len(cov)!=len(coverage) or set(cov)!=all_ids:errors.append(['COVERAGE_ID_BIJECTION_FAILURE'])
    actual_task_ids={r['image_id'] for r in coverage if r['task_id']}
    if actual_task_ids!=task_ids:errors.append(['WRONG_MAIN_OR_REMAINING_ASSIGNMENT'])
    if len(members)!=len(task_ids) or {r['image_id'] for r in members}!=task_ids:errors.append(['MEMBERSHIP_NOT_ONE_ROW_PER_SOURCE_FILE'])
    source_by_id={r['image_id']:r for r in actual}
    for c in coverage:
        source=source_by_id[c['image_id']];h=source['fresh_pixel_sha256']
        expected_task='RT-'+h[:24] if h in expected_hashes else ''
        if c['task_id']!=expected_task or c['content_group']!=h or c['image_path']!=source['image_path']:
            errors.append(['COVERAGE_TASK_LINK_DIFFERENCE',c['image_id']])
        if c['bucket']!=('MAIN_REVIEW_TASK' if expected_task else 'NO_FOUR_FAMILY_TASK'):
            errors.append(['COVERAGE_BUCKET_DIFFERENCE',c['image_id']])
    for m in members:
        source=source_by_id[m['image_id']]
        if m['task_id']!='RT-'+source['fresh_pixel_sha256'][:24]:
            errors.append(['MEMBER_TASK_LINK_DIFFERENCE',m['image_id']])
        for key in ['image_path','xml_path','file_sha256','pixel_sha256','xml_sha256','defect_labels','directory_class']:
            if m.get(key)!=source.get(key):errors.append(['MEMBER_SOURCE_FIELD_DIFFERENCE',m['image_id'],key])
        original_objects=cached_xml[source['xml_path']]['objects'] if source['xml_path'] else []
        if m['xml_objects']!=original_objects:errors.append(['MEMBER_XML_VARIANT_LOST',m['image_id']])
    for t in tasks:
        expected_ids={r['image_id'] for r in groups[t['pixel_sha256']]}
        if set(t['image_ids'])!=expected_ids or t['member_count']!=len(expected_ids):errors.append(['CONTENT_GROUP_MEMBER_LOST',t['task_id']])
    if len(names)!=len(name_expected) or {r['image_id']:r['relation'] for r in names}!=name_expected:errors.append(['NAME_REGISTER_DISAGREEMENT'])
    if Counter((r['image_id'],r['code']) for r in metadata)!=metadata_expected:errors.append(['HISTORICAL_REFERENCE_REGISTER_DISAGREEMENT'])
    # Validate cumulative and residual memberships independently for each screening round.
    processed=set();round_checks=[]
    for rr,family in enumerate(['duplicates','class_conflicts','filename_differences','coordinates'],1):
        processed.add(family);assigned={h for h,ev in expected.items() if any(e[0] in processed for e in ev)}
        nfiles=sum(len(groups[h]) for h in assigned)
        round_checks.append({'round':rr,'family':family,'expected_cumulative_tasks':len(assigned),
                             'expected_cumulative_files':nfiles,'expected_remaining_files':len(rows)-nfiles})
    saved=json.loads((package/'rounds.json').read_text())
    if len(saved)!=len(round_checks):errors.append(['ROUND_COUNT_DIFFERENCE'])
    for a,b in zip(round_checks,saved):
        if [a['expected_cumulative_tasks'],a['expected_cumulative_files'],a['expected_remaining_files']]!=[b['cumulative_tasks'],b['cumulative_image_files'],b['remaining_image_files']]:errors.append(['ROUND_RESIDUAL_ACCOUNTING_DIFFERENCE',a['round']])
    source_paths={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.suffix.lower() in {'.tif','.tiff','.png','.jpg','.jpeg','.bmp'}}
    if source_paths!={r['image_path'] for r in rows}:errors.append(['NEW_OR_MISSING_SOURCE_IMAGES'])
    xml_paths={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p.suffix.lower()=='.xml'}
    if xml_paths!=set(cached_xml):errors.append(['NEW_OR_MISSING_SOURCE_XML'])
    # CSV files are reviewer-facing copies of these exact records, not a second
    # selection. Check their contents as well as their row counts.
    csv_sources={
        '复核任务总表.csv':tasks,'任务与原始文件对应.csv':members,
        '问题证据明细.csv':events,'全量图片覆盖账本.csv':coverage,
        '未纳入本任务包的图片.csv':[c for c in coverage if not c['task_id']],
        '名称比较全表.csv':names,'历史元数据参考.csv':metadata,'逐轮筛选账本.csv':saved}
    for filename,records in csv_sources.items():
        with (package/filename).open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f);fields=reader.fieldnames;exported=list(reader)
        expected_csv=[]
        for record in records:
            line={}
            for key in fields:
                value=record.get(key)
                line[key]=json.dumps(value,ensure_ascii=False) if isinstance(value,(dict,list)) else '' if value is None else str(value)
            expected_csv.append(line)
        if exported!=expected_csv:errors.append(['CSV_RECORD_DIFFERENCE',filename])
    package_summary=json.loads((package/'summary.json').read_text())
    counts={'source_image_files':len(rows),'source_xml_files':len(cached_xml),
            'source_pixel_groups':len(groups),'deduplicated_tasks':len(expected_hashes),
            'task_member_files':len(task_ids),'remaining_image_files':len(remainder),'event_count':len(events)}
    if any(package_summary[k]!=value for k,value in counts.items()):errors.append(['PACKAGE_SUMMARY_COUNT_DIFFERENCE'])
    for filename,sha in package_summary['input_artifact_sha256'].items():
        if hashlib.sha256((audit/filename).read_bytes()).hexdigest()!=sha:errors.append(['PRIOR_AUDIT_ARTIFACT_CHANGED',filename])
    result={'verification':'raw bytes, decoded pixels, minidom XML, independent membership rules and CSV records',
            'verified_utc':datetime.now(timezone.utc).isoformat(),
            'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'image_files_rechecked':len(actual),'xml_files_rechecked':sum(r['fresh_xml'] is not None for r in actual),
            'main_queue_files_expected':len(task_ids),'remaining_files_rechecked':len(remainder),
            'expected_deduplicated_tasks':len(expected_hashes),'missed_issue_files':len(task_ids-actual_task_ids),
            'unjustified_queue_files':len(actual_task_ids-task_ids),'raw_content_or_stat_change_files':source_changed,
            'round_checks':round_checks,'errors':errors,'passed':not errors,
            'interpretation':'No classification mistakes found under the four explicit machine-review rules; not a semantic label-accuracy claim'}
    (package/'independent_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--audit',required=True);p.add_argument('--package',required=True);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    result=verify(a.root,a.audit,a.package,a.workers);print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['passed'] else 2)
