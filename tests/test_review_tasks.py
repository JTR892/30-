"""Synthetic review-queue tests; no real defect semantic certification."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
from weldstudy.xml_audit import run_audit
from weldstudy.review_tasks import build, box_questions, filename_relation, jsonl


class ReviewTaskTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.raw=self.base/'raw';self.raw.mkdir()
        self.config={'population_roots':{'bad':'DEFECT_CLAIM','good':'NORMAL_RESEARCHER_CONFIRMED'},
                     'directory_classes':{'pores':'气孔','cracks':'裂纹'},'partition_names':['train','test'],
                     'known_defect_labels':['气孔','裂纹'],'auxiliary_labels':['焊缝'],'heterogeneous_labels':[]}
        self.conf=self.base/'conf.json';self.conf.write_text(json.dumps(self.config))
        self.audit=self.base/'audit';self.package=self.base/'package'

    def add(self,path,seed=1,label='气孔',box=(1,2,5,8),filename=None,folder=None,source=None,xml=True):
        p=self.raw/path;p.parent.mkdir(parents=True,exist_ok=True)
        a=np.random.default_rng(seed).integers(0,65535,(10,12),dtype=np.uint16);Image.fromarray(a).save(p)
        if xml:
            text=f'<annotation><filename>{filename or p.name}</filename><folder>{folder or label}</folder><path>{source or p.name}</path><size><width>12</width><height>10</height><depth>1</depth></size><object><name>{label}</name><bndbox><xmin>{box[0]}</xmin><ymin>{box[1]}</ymin><xmax>{box[2]}</xmax><ymax>{box[3]}</ymax></bndbox></object></annotation>'
            p.with_suffix('.xml').write_text(text)
        return p

    def fixture(self):
        self.add('bad/train/pores/a.tif',1)
        self.add('bad/test/cracks/dup.tif',1,label='裂纹',box=(2,2,5,8))
        self.add('bad/train/pores/b.tif',2,filename='b.tiff')
        self.add('bad/train/pores/c.tif',3,label='裂纹')
        self.add('bad/train/pores/d.tif',4,filename='older.tif')
        self.add('bad/train/pores/e.tif',5,box=(2,2,2,8))
        self.add('bad/train/pores/f.tif',6,box=(5,2,2,8))
        self.add('good/g.tif',7,xml=False)
        self.add('bad/train/pores/h.tif',8,folder='裂纹',source='old_source.tif')
        run_audit(self.raw,self.audit,self.conf,2)
        return build(self.audit,self.raw,self.package)

    def test_dedup_preserves_members_annotations_and_rest_coverage(self):
        s=self.fixture();rows=jsonl(self.package/'coverage.jsonl');tasks=jsonl(self.package/'tasks.jsonl')
        self.assertEqual(s['source_image_files'],9);self.assertEqual(s['deduplicated_tasks'],5)
        self.assertEqual(s['task_member_files'],6);self.assertEqual(s['remaining_image_files'],3)
        dup=next(t for t in tasks if t['member_count']==2)
        self.assertIn('DUPLICATE_LABEL_SET_DIFFERENCE',dup['issue_codes'])
        self.assertIn('DUPLICATE_OBJECT_ANNOTATION_DIFFERENCE',dup['issue_codes'])
        self.assertEqual(len([m for m in jsonl(self.package/'members.jsonl') if m['task_id']==dup['task_id']]),2)
        self.assertTrue(all(r['research_eligibility']=='NOT_DECIDED_BY_TASK_PACK' for r in rows))
        rest={Path(r['image_path']).name for r in rows if not r['task_id']}
        self.assertEqual(rest,{'b.tif','g.tif','h.tif'})
        self.assertEqual(s['review_decisions_made'],0)

    def test_independent_verification_and_injected_omission(self):
        self.fixture();script=Path(__file__).resolve().parents[1]/'scripts/verify_review_tasks.py'
        cmd=[sys.executable,str(script),'--root',str(self.raw),'--audit',str(self.audit),'--package',str(self.package)]
        r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        cov=jsonl(self.package/'coverage.jsonl');next(r for r in cov if r['task_id'])['task_id']=''
        (self.package/'coverage.jsonl').write_text('\n'.join(json.dumps(r) for r in cov))
        r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,2)
        v=json.loads((self.package/'independent_validation.json').read_text())
        self.assertFalse(v['passed']);self.assertGreater(v['missed_issue_files'],0)

    def test_verifier_detects_wrong_task_link_lost_xml_and_csv_changes(self):
        self.fixture();members=jsonl(self.package/'members.jsonl')
        members[0]['task_id']=members[-1]['task_id'];members[0]['xml_objects']=[]
        (self.package/'members.jsonl').write_text('\n'.join(json.dumps(r) for r in members))
        path=self.package/'复核任务总表.csv'
        path.write_text(path.read_text(encoding='utf-8-sig').replace('PENDING_REVIEW','CERTIFIED'),encoding='utf-8-sig')
        script=Path(__file__).resolve().parents[1]/'scripts/verify_review_tasks.py'
        r=subprocess.run([sys.executable,str(script),'--root',str(self.raw),'--audit',str(self.audit),
                          '--package',str(self.package)],capture_output=True,text=True)
        self.assertEqual(r.returncode,2,r.stdout+r.stderr)
        codes={e[0] for e in json.loads((self.package/'independent_validation.json').read_text())['errors']}
        self.assertTrue({'MEMBER_TASK_LINK_DIFFERENCE','MEMBER_XML_VARIANT_LOST','CSV_RECORD_DIFFERENCE'}<=codes)

    def test_no_source_changes_and_no_output_overwrite(self):
        self.add('bad/train/pores/a.tif');run_audit(self.raw,self.audit,self.conf,1)
        before={str(p):p.read_bytes() for p in self.raw.rglob('*') if p.is_file()}
        build(self.audit,self.raw,self.package)
        after={str(p):p.read_bytes() for p in self.raw.rglob('*') if p.is_file()};self.assertEqual(before,after)
        with self.assertRaises(ValueError):build(self.audit,self.raw,self.package)
        with self.assertRaises(ValueError):build(self.audit,self.raw,self.raw/'output')

    def test_duplicate_normal_files_without_xml_are_preserved_and_verified(self):
        self.add('good/a.tif',seed=9,xml=False);self.add('good/b.tif',seed=9,xml=False)
        run_audit(self.raw,self.audit,self.conf,1);summary=build(self.audit,self.raw,self.package)
        self.assertEqual(summary['deduplicated_tasks'],1);self.assertEqual(summary['task_member_files'],2)
        self.assertTrue(all(not m['xml_path'] and not m['xml_objects'] for m in jsonl(self.package/'members.jsonl')))
        script=Path(__file__).resolve().parents[1]/'scripts/verify_review_tasks.py'
        r=subprocess.run([sys.executable,str(script),'--root',str(self.raw),'--audit',str(self.audit),
                          '--package',str(self.package)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertEqual(json.loads((self.package/'independent_validation.json').read_text())['xml_files_rechecked'],0)

    def test_coordinate_uncertainty_not_mislabeled_as_reversal(self):
        self.assertEqual(box_questions([2,2,2,8],12,10),['BOX_ZERO_SPAN_CONVENTION'])
        self.assertEqual(box_questions([5,2,2,8],12,10),['BOX_REVERSED'])
        self.assertEqual(box_questions([0,0,12,10],12,10),[])
        self.assertEqual(filename_relation('a.tif','a.tiff'),'TIFF_EXTENSION_EQUIVALENT')


if __name__=='__main__':unittest.main()
