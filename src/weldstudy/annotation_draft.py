"""Link an unapproved taxonomy and human questions to a preserved audit package.

Selectors describe review scope only. They never produce diagnostic decisions,
label replacements, research exclusions, training subsets or a cluster count.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line]


def write_json(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def write_csv(path, records, fields):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        for record in records:
            writer.writerow({key:json.dumps(value,ensure_ascii=False) if isinstance(value,(list,dict)) else value
                             for key,value in record.items()})


def select_question(selector, row, labels, codes, name_relation, auxiliary):
    kind=selector['kind']
    if kind=='all':return True
    if kind=='population':return row['population_claim']==selector['value']
    if kind=='labels':return bool(labels & set(selector['values']))
    if kind=='multitype':return len(labels-auxiliary)>1
    if kind=='has_xml':return bool(row.get('xml_path'))
    if kind=='events':return bool(codes & set(selector['codes']))
    if kind=='name_relation':return name_relation==selector['value']
    raise ValueError('Unknown review-scope selector: '+kind)


def derive(rows, xml_records, tasks, events, coverage, names, taxonomy, questions, auxiliary):
    by_xml={x['xml_path']:x for x in xml_records}
    by_cov={c['image_id']:c for c in coverage}
    if len(by_cov)!=len(coverage) or set(by_cov)!={r['image_id'] for r in rows}:
        raise ValueError('Audit and task-package coverage differ')
    by_name={n['image_id']:n['relation'] for n in names};by_codes=defaultdict(set)
    for event in events:
        for ident in event['image_ids']:by_codes[ident].add(event['code'])
    aux=set(auxiliary);scope=[];links=defaultdict(list);task_links=defaultdict(set)
    labels_by_image={};objects=Counter()
    for r in rows:
        current=by_xml[r['xml_path']]['objects'] if r.get('xml_path') else []
        labels={o['name'] for o in current};labels_by_image[r['image_id']]=labels
        objects.update(o['name'] for o in current)
        selected=[q['id'] for q in questions if select_question(q['selector'],r,labels,
                     by_codes[r['image_id']],by_name.get(r['image_id']),aux)]
        base_task=by_cov[r['image_id']]['task_id']
        record={'image_id':r['image_id'],'image_path':r['image_path'],'xml_path':r.get('xml_path',''),
                'base_task_id':base_task,'question_ids':selected,'raw_xml_labels':sorted(labels),
                'review_status':'NOT_REVIEWED','observed_defects':'','proposed_label_changes':'',
                'reviewer':'','review_date':'','evidence_reference':'','adjudication':''}
        scope.append(record)
        for qid in selected:
            links[qid].append(record)
            if base_task:task_links[qid].add(base_task)
    question_records=[]
    for q in questions:
        selected=links[q['id']];ids={r['image_id'] for r in selected}
        groups={r['pixel_sha256'] for r in rows if r['image_id'] in ids}
        question_records.append(dict(q,affected_image_files=len(ids),affected_pixel_groups=len(groups),
             linked_base_tasks=len(task_links[q['id']]),status='OPEN',assignee='',answer='',
             confirmed_basis='',confirmation_date=''))
    statistics=[]
    for entry in taxonomy['entries']:
        label=entry['raw_label']
        if entry['observed_in']=='POPULATION_DIRECTORY_AND_RESEARCHER_STATEMENT':
            selected=[r for r in rows if r['population_claim']=='NORMAL_RESEARCHER_CONFIRMED']
            nobjects=None;unit='POPULATION_CLAIM_NOT_XML_LABEL'
        else:
            selected=[r for r in rows if label in labels_by_image[r['image_id']]]
            nobjects=objects[label];unit='XML_OBJECT_LABEL_PRESENCE'
        statistics.append({'label_id':entry['label_id'],'raw_label':label,'count_basis':unit,
             'object_instances':nobjects,'image_files':len(selected),
             'pixel_groups':len({r['pixel_sha256'] for r in selected}),
             'task_member_files':sum(bool(by_cov[r['image_id']]['task_id']) for r in selected),
             'expert_definition':None,'definition_status':entry['definition_status']})
    task_question_links=[{'question_id':qid,'task_id':tid} for qid,tids in sorted(task_links.items()) for tid in sorted(tids)]
    return {'scope':scope,'questions':question_records,'task_question_links':task_question_links,
            'label_statistics':statistics,'unmapped_xml_labels':sorted(set(objects)-{e['raw_label'] for e in taxonomy['entries']})}


def build(audit, package, taxonomy_path, questions_path, out):
    audit,package,taxonomy_path,questions_path,out=map(lambda p:Path(p).resolve(),
        (audit,package,taxonomy_path,questions_path,out))
    audit_summary=json.loads((audit/'summary.json').read_text());raw_root=Path(audit_summary['dataset_root']).resolve()
    if any(out==p or p in out.parents for p in [raw_root,audit,package]):
        raise ValueError('Use a separate output version outside raw data and prior evidence')
    if out.exists() and any(out.iterdir()):raise ValueError('Output must be new or empty')
    taxonomy=json.loads(taxonomy_path.read_text());qconfig=json.loads(questions_path.read_text())
    if taxonomy['status']!='DRAFT_NOT_APPROVED' or taxonomy['applied_standard'] is not None:
        raise ValueError('This draft builder does not approve standards or taxonomy')
    if any(e['expert_definition'] is not None for e in taxonomy['entries']):
        raise ValueError('Expert definitions must not be fabricated by the draft builder')
    qids=[q['id'] for q in qconfig['questions']]
    if len(qids)!=len(set(qids)):raise ValueError('Question IDs must be unique')
    rows=jsonl(audit/'images.jsonl');xs=jsonl(audit/'xml_records.jsonl');tasks=jsonl(package/'tasks.jsonl')
    events=jsonl(package/'events.jsonl');coverage=jsonl(package/'coverage.jsonl');names=jsonl(package/'names.jsonl')
    result=derive(rows,xs,tasks,events,coverage,names,taxonomy,qconfig['questions'],audit_summary['config']['auxiliary_labels'])
    out.mkdir(parents=True,exist_ok=True)
    for name in ['scope','questions','task_question_links','label_statistics']:
        with (out/(name+'.jsonl')).open('w',encoding='utf-8') as f:
            for record in result[name]:f.write(json.dumps(record,ensure_ascii=False,allow_nan=False)+'\n')
    write_csv(out/'人工确认问题.csv',result['questions'],['id','topic','question','affected_image_files',
        'affected_pixel_groups','linked_base_tasks','owner_role','evidence_requested','boundary',
        'status','assignee','answer','confirmed_basis','confirmation_date'])
    write_csv(out/'问题与原复核任务对应.csv',result['task_question_links'],['question_id','task_id'])
    scope_fields=['image_id','image_path','xml_path','base_task_id','question_ids','raw_xml_labels','review_status']
    write_csv(out/'全量逐图待确认范围.csv',result['scope'],scope_fields)
    members=[r for r in result['scope'] if r['base_task_id']]
    write_csv(out/'逐文件判读填报模板.csv',members,scope_fields+['observed_defects','proposed_label_changes',
        'reviewer','review_date','evidence_reference','adjudication'])
    write_csv(out/'类别观察统计.csv',result['label_statistics'],['label_id','raw_label','count_basis','object_instances',
        'image_files','pixel_groups','task_member_files','definition_status'])
    write_csv(out/'术语与角色确认表.csv',[dict(e,confirmed_definition='',confirmed_role='',approved_aliases='',
        reviewer='',review_date='',evidence_reference='') for e in taxonomy['entries']],
        ['label_id','raw_label','observed_in','proposed_role','concept_draft','source_ids','question_ids',
         'definition_status','confirmed_definition','confirmed_role','approved_aliases','reviewer','review_date','evidence_reference'])
    coord=[e for e in events if e['family']=='coordinates']
    write_csv(out/'坐标问题逐对象确认.csv',coord,['event_id','task_id','code','image_ids','evidence'])
    examples=['# 人工确认问题的机械索引示例','',
       '以下按image_id排序选取，供定位材料。未新增图像判读结论；不是随机抽样或代表性抽样。','']
    for q in result['questions']:
        sample=sorted([r for r in result['scope'] if q['id'] in r['question_ids']],key=lambda r:r['image_id'])[:3]
        examples.extend(['## '+q['id']+' '+q['topic'],'',q['question'],''])
        for r in sample:
            examples.append('- 原图：'+r['image_path']+'；XML：'+(r['xml_path'] or '无')+'；原任务：'+(r['base_task_id'] or '原剩余清单'))
        examples.append('')
    (out/'问题证据定位示例.md').write_text('\n'.join(examples),encoding='utf-8')
    inputs=[audit/'images.jsonl',audit/'xml_records.jsonl',audit/'summary.json',package/'tasks.jsonl',
            package/'events.jsonl',package/'coverage.jsonl',package/'names.jsonl',taxonomy_path,questions_path]
    summary={'version':'annotation-draft-0.1','status':'DRAFT_NOT_APPROVED',
        'generated_utc':datetime.now(timezone.utc).isoformat(),'source_image_files':len(rows),'source_xml_files':len(xs),
        'source_xml_objects':sum(len(x['objects']) for x in xs),'dictionary_entries':len(taxonomy['entries']),
        'questions':len(result['questions']),'base_review_tasks':len(tasks),'base_review_member_files':len(members),
        'scope_records':len(result['scope']),'question_task_links':len(result['task_question_links']),
        'all_base_tasks_linked':{r['task_id'] for r in result['task_question_links']}=={t['task_id'] for t in tasks},
        'unmapped_xml_labels':result['unmapped_xml_labels'],'expert_decisions_created':0,
        'source_files_modified':False,'applied_standard':None,'research_qualification':'HOLD',
        'label_statistics':result['label_statistics'],
        'question_scope_counts':[{k:q[k] for k in ['id','affected_image_files','affected_pixel_groups','linked_base_tasks']} for q in result['questions']],
        'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        'count_interpretation':'Presence in original XML or population claim; not expert truth or independent welds; question scopes overlap'}
    write_json(out/'summary.json',summary)
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audit',required=True);p.add_argument('--package',required=True)
    p.add_argument('--taxonomy',default='config/taxonomy.draft.json')
    p.add_argument('--questions',default='config/annotation_questions.draft.json');p.add_argument('--out',required=True)
    a=p.parse_args();print(json.dumps(build(a.audit,a.package,a.taxonomy,a.questions,a.out),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
