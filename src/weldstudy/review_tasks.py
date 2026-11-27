"""Build a private, content-deduplicated review queue; never clean or relabel raw data.

Four actionable families: exact duplicates (including annotation differences),
actual-directory/XML class disagreements, XML filename identity differences, and
coordinate questions. Historical XML folder/path claims are a separate register.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

VERSION = 'review-tasks-1.0'
FAMILIES = ['duplicates', 'class_conflicts', 'filename_differences', 'coordinates']


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def write_jsonl(path, rows):
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, allow_nan=False)+'\n')


def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict,list)) else v
                        for k,v in row.items()})


def filename_relation(actual, recorded):
    recorded = PureWindowsPath(recorded or '').name
    if actual == recorded:
        return 'EXACT'
    a,b = Path(actual),Path(recorded)
    if recorded and a.stem == b.stem and a.suffix.lower() in {'.tif','.tiff'} and b.suffix.lower() in {'.tif','.tiff'}:
        return 'TIFF_EXTENSION_EQUIVALENT'
    return 'IDENTITY_REVIEW'


def box_questions(box, width, height):
    if box is None or len(box)!=4 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in box):
        return ['BOX_MALFORMED_OR_NONFINITE']
    x1,y1,x2,y2 = box; result=[]
    if x2<x1 or y2<y1: result.append('BOX_REVERSED')
    elif x2==x1 or y2==y1: result.append('BOX_ZERO_SPAN_CONVENTION')
    if min(x1,x2)<0 or min(y1,y2)<0 or max(x1,x2)>width or max(y1,y2)>height:
        result.append('BOX_OUTSIDE_CURRENT_IMAGE')
    return result


def annotation_signature(objects):
    # Sorting removes XML object-order differences, while retaining multiplicity.
    return sorted([{'name':o['name'], 'box':o.get('box')} for o in objects], key=lambda x:json.dumps(x,sort_keys=True))


def derive(rows, xml_records, config):
    by_xml={x['xml_path']:x for x in xml_records}; groups=defaultdict(list)
    for r in rows:
        if not r.get('pixel_sha256'):
            raise ValueError('A reviewed decoded-pixel hash is required for every file')
        groups[r['pixel_sha256']].append(r)
    events=[];tasks=[];members=[];metadata=[];names=[];coverage=[]
    known=set(config['known_defect_labels']); auxiliary=set(config['auxiliary_labels'])
    for pixel_hash, group in sorted(groups.items()):
        group=sorted(group,key=lambda r:r['image_id']); task_id='RT-'+pixel_hash[:24]
        local=[]; own=defaultdict(set)
        def add(family,code,selected,evidence):
            ids=sorted(r['image_id'] for r in selected)
            event={'task_id':task_id,'family':family,'code':code,'image_ids':ids,'evidence':evidence}
            event['event_id']='EV-'+digest(event)[:24];local.append(event)
            for ident in ids:own[ident].add(code)
        if len(group)>1:
            add('duplicates','EXACT_PIXEL_DUPLICATES',group,{'member_count':len(group),'pixel_sha256':pixel_hash})
            byte_counts=Counter(r['file_sha256'] for r in group)
            if max(byte_counts.values())>1:
                add('duplicates','EXACT_FILE_DUPLICATES',group,{'byte_hash_counts':dict(byte_counts)})
            partitions=sorted({r['supplied_partition'] for r in group})
            if len(partitions)>1:add('duplicates','DUPLICATE_CROSS_SUPPLIED_PARTITIONS',group,{'partitions':partitions})
            label_sets=sorted({tuple(r['defect_labels']) for r in group})
            if len(label_sets)>1:add('duplicates','DUPLICATE_LABEL_SET_DIFFERENCE',group,{'label_sets':label_sets})
            dirs=sorted({r['directory_class'] for r in group})
            if len(dirs)>1:add('duplicates','DUPLICATE_DIRECTORY_CLAIM_DIFFERENCE',group,{'directory_claims':dirs})
            sigs=[annotation_signature(by_xml[r['xml_path']]['objects']) if r['xml_path'] else None for r in group]
            if len({digest(s) for s in sigs})>1:
                add('duplicates','DUPLICATE_OBJECT_ANNOTATION_DIFFERENCE',group,
                    {'annotation_signatures':dict(zip((r['image_id'] for r in group),(digest(s) for s in sigs)))})
        for r in group:
            if r['xml_path']:
                x=by_xml[r['xml_path']]; labels=sorted({o['name'] for o in x['objects']} - auxiliary)
                if r['directory_class'] and r['directory_class'] not in labels:
                    add('class_conflicts','DIRECTORY_CLASS_ABSENT_FROM_XML',[r],
                        {'directory_class':r['directory_class'],'xml_defect_labels':labels})
                relation=filename_relation(Path(r['image_path']).name,x['filename'])
                names.append({'image_id':r['image_id'],'image_path':r['image_path'],'content_group':pixel_hash,
                              'recorded_filename':x['filename'],'relation':relation,'task_id_candidate':task_id})
                if relation=='IDENTITY_REVIEW':
                    add('filename_differences','XML_FILENAME_IDENTITY_REVIEW',[r],
                        {'actual_filename':Path(r['image_path']).name,'xml_filename':x['filename']})
                for o in x['objects']:
                    for code in box_questions(o.get('box'),r['width'],r['height']):
                        add('coordinates',code,[r],{'object_index':o['object_index'],'name':o['name'],
                                                    'box':o.get('box'),'width':r['width'],'height':r['height']})
                # Header folders and old source paths can record earlier exports. They
                # are not promoted to current defect ground truth or pairing failures.
                if x['folder'] in known and x['folder'] not in labels:
                    metadata.append({'image_id':r['image_id'],'image_path':r['image_path'],'code':'HISTORICAL_XML_FOLDER_LABEL_ABSENT',
                                     'evidence':{'xml_folder':x['folder'],'xml_defect_labels':labels},'action':'PROVENANCE_REFERENCE_NOT_AUTO_LABEL_ERROR'})
                if x['folder'] in known and x['folder']!=r['directory_class']:
                    metadata.append({'image_id':r['image_id'],'image_path':r['image_path'],'code':'CURRENT_DIRECTORY_VS_HISTORICAL_XML_FOLDER',
                                     'evidence':{'directory_class':r['directory_class'],'xml_folder':x['folder']},'action':'PROVENANCE_REFERENCE_NOT_AUTO_LABEL_ERROR'})
                source_base=PureWindowsPath(x['source_path']).name
                if source_base and source_base!=x['filename']:
                    metadata.append({'image_id':r['image_id'],'image_path':r['image_path'],'code':'SOURCE_PATH_BASENAME_DIFFERS_FROM_XML_FILENAME',
                                     'evidence':{'xml_filename':x['filename'],'source_basename':source_base,
                                                 'relation':filename_relation(x['filename'],source_base)},
                                     'action':'HISTORICAL_PATH_REFERENCE_NOT_AUTO_PAIRING_ERROR'})
                keys=[digest({'name':o['name'],'box':o.get('box')}) for o in x['objects']]
                if len(keys)!=len(set(keys)):
                    add('duplicates','REPEATED_IDENTICAL_OBJECT_RECORD',[r],{'extra_objects':len(keys)-len(set(keys))})
        if local:
            codes=sorted({e['code'] for e in local}); families=sorted({e['family'] for e in local})
            priority=1 if any(c in codes for c in ['BOX_REVERSED','DIRECTORY_CLASS_ABSENT_FROM_XML','DUPLICATE_LABEL_SET_DIFFERENCE','DUPLICATE_DIRECTORY_CLAIM_DIFFERENCE']) else 2 if any(c in codes for c in ['XML_FILENAME_IDENTITY_REVIEW','BOX_ZERO_SPAN_CONVENTION','DUPLICATE_CROSS_SUPPLIED_PARTITIONS','DUPLICATE_OBJECT_ANNOTATION_DIFFERENCE']) else 3
            tasks.append({'task_id':task_id,'priority':priority,'pixel_sha256':pixel_hash,'member_count':len(group),
                          'families':families,'issue_codes':codes,'representative_image_id':group[0]['image_id'],
                          'representative_path':group[0]['image_path'],'image_ids':[r['image_id'] for r in group],
                          'supplied_partitions':sorted({r['supplied_partition'] for r in group}),
                          'review_status':'PENDING_REVIEW','assignee':'','decision':'','evidence_reference':'','review_date':''})
            events.extend(local)
            for r in group:
                members.append(dict(r,task_id=task_id,own_event_codes=sorted(own[r['image_id']]),
                                    xml_objects=by_xml[r['xml_path']]['objects'] if r['xml_path'] else []))
        for r in group:
            coverage.append({'image_id':r['image_id'],'image_path':r['image_path'],'content_group':pixel_hash,
                             'task_id':task_id if local else '', 'bucket':'MAIN_REVIEW_TASK' if local else 'NO_FOUR_FAMILY_TASK',
                             'own_event_codes':sorted(own[r['image_id']]),
                             'semantic_status':'NOT_EXPERT_CERTIFIED','research_eligibility':'NOT_DECIDED_BY_TASK_PACK',
                             'other_scope_notes':([
                                 name for name,condition in [
                                     ('NORMAL_LABEL_RESEARCHER_STATEMENT_NO_XML',not r['xml_path']),
                                     ('MULTITYPE',r['n_defect_types']>1),
                                     ('AUXILIARY_ONLY',bool(r['xml_path']) and not r['defect_labels']),
                                     ('HETEROGENEOUS_LABEL','其它缺陷' in r['defect_labels'])] if condition])})
    tasks.sort(key=lambda t:(t['priority'],t['task_id']))
    task_ids={t['task_id'] for t in tasks}
    for n in names:
        candidate=n.pop('task_id_candidate')
        n['task_id']=candidate if candidate in task_ids else ''
    rounds=[];selected=set();by_task={t['task_id']:set(t['families']) for t in tasks}
    for i,family in enumerate(FAMILIES,1):
        found={e['task_id'] for e in events if e['family']==family};new=found-selected;selected |= found
        selected_images={m['image_id'] for m in members if m['task_id'] in selected}
        remaining=[r for r in coverage if r['task_id'] not in selected]
        processed=set(FAMILIES[:i])
        missed={e['task_id'] for e in events if e['family'] in processed and e['task_id'] not in selected}
        rounds.append({'round':i,'family':family,'new_content_tasks':len(new),'cumulative_tasks':len(selected),
                       'cumulative_image_files':len(selected_images),'remaining_image_files':len(remaining),
                       'remaining_known_events_in_processed_families':len(missed),
                       'later_family_tasks_not_yet_assigned':sum(bool(fs-set(FAMILIES[:i])) and tid not in selected for tid,fs in by_task.items())})
    return {'tasks':tasks,'events':events,'members':members,'coverage':coverage,'names':names,'metadata':metadata,'rounds':rounds}


def build(audit_dir, raw_root, out):
    audit_dir,raw_root,out=map(lambda p:Path(p).resolve(),(audit_dir,raw_root,out))
    if out==raw_root or raw_root in out.parents:raise ValueError('Output cannot be inside the raw directory')
    if out==audit_dir or audit_dir in out.parents:raise ValueError('Use a separate output version; preserve prior audit artifacts')
    if out.exists() and any(out.iterdir()):raise ValueError('Output must be new or empty')
    rows=jsonl(audit_dir/'images.jsonl'); xs=jsonl(audit_dir/'xml_records.jsonl')
    summary=json.loads((audit_dir/'summary.json').read_text());config=summary['config']
    if Path(summary['dataset_root']).resolve()!=raw_root:raise ValueError('Raw root does not match the recorded audit')
    if len({r['image_id'] for r in rows})!=len(rows) or len({r['image_path'] for r in rows})!=len(rows):
        raise ValueError('Input inventory IDs/paths must be unique')
    result=derive(rows,xs,config)
    if len({t['task_id'] for t in result['tasks']})!=len(result['tasks']):raise ValueError('Task ID collision')
    out.mkdir(parents=True,exist_ok=True)
    for key in ['tasks','events','members','coverage','names','metadata']:
        write_jsonl(out/(key+'.jsonl'),result[key])
    task_fields=['task_id','priority','member_count','families','issue_codes','representative_path','supplied_partitions','review_status','assignee','decision','evidence_reference','review_date']
    write_csv(out/'复核任务总表.csv',result['tasks'],task_fields)
    write_csv(out/'任务与原始文件对应.csv',result['members'],['task_id','image_id','image_path','xml_path','file_sha256','pixel_sha256','xml_sha256','directory_class','defect_labels','xml_filename','xml_folder','xml_source_path','own_event_codes'])
    write_csv(out/'问题证据明细.csv',result['events'],['event_id','task_id','family','code','image_ids','evidence'])
    cov_fields=['image_id','image_path','content_group','task_id','bucket','own_event_codes','other_scope_notes','semantic_status','research_eligibility']
    write_csv(out/'全量图片覆盖账本.csv',result['coverage'],cov_fields)
    write_csv(out/'未纳入本任务包的图片.csv',[r for r in result['coverage'] if not r['task_id']],cov_fields)
    write_csv(out/'名称比较全表.csv',result['names'],['image_id','image_path','recorded_filename','relation','task_id'])
    write_csv(out/'历史元数据参考.csv',result['metadata'],['image_id','image_path','code','evidence','action'])
    write_csv(out/'逐轮筛选账本.csv',result['rounds'],list(result['rounds'][0]))
    write_json(out/'rounds.json',result['rounds'])
    events=result['events'];tasks=result['tasks']
    report={'version':VERSION,'generated_utc':datetime.now(timezone.utc).isoformat(),'audit_directory':str(audit_dir),
            'raw_root':str(raw_root),'builder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'input_artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [audit_dir/'images.jsonl',audit_dir/'xml_records.jsonl',audit_dir/'summary.json']},
            'source_image_files':len(rows),'source_xml_files':len(xs),'source_pixel_groups':len({r['pixel_sha256'] for r in rows}),
            'deduplicated_tasks':len(tasks),'task_member_files':len(result['members']),
            'remaining_image_files':sum(not r['task_id'] for r in result['coverage']),
            'event_count':len(events),'event_code_counts':dict(Counter(e['code'] for e in events)),
            'priority_task_counts':dict(Counter(t['priority'] for t in tasks)),
            'name_relation_counts':dict(Counter(r['relation'] for r in result['names'])),
            'historical_metadata_counts':dict(Counter(r['code'] for r in result['metadata'])),
            'rounds':result['rounds'],'input_pixels_or_xml_modified':False,
            'review_decisions_made':0,'research_samples_excluded':0,
            'deduplication_unit':'Identical decoded pixels including dimensions/dtype/frames; not source/weld identity',
            'completion_status':'BUILT_AWAITING_INDEPENDENT_VALIDATION',
            'scope':'Four review families; no task assignment is a label correction or research qualification decision'}
    write_json(out/'summary.json',report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audit',required=True);p.add_argument('--root',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();print(json.dumps(build(a.audit,a.root,a.out),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
