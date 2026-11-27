"""Synthetic checks for review-scope linking; no defect adjudication."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from weldstudy.annotation_draft import build, derive


class AnnotationDraftTests(unittest.TestCase):
    def fixture(self):
        rows=[
            {'image_id':'a','image_path':'a.tif','xml_path':'a.xml','pixel_sha256':'p1','population_claim':'DEFECT_DIRECTORY_CLAIM'},
            {'image_id':'b','image_path':'b.tif','xml_path':'b.xml','pixel_sha256':'p1','population_claim':'DEFECT_DIRECTORY_CLAIM'},
            {'image_id':'c','image_path':'c.tif','xml_path':'','pixel_sha256':'p2','population_claim':'NORMAL_RESEARCHER_CONFIRMED'},
            {'image_id':'d','image_path':'d.tif','xml_path':'','pixel_sha256':'p3','population_claim':'UNKNOWN'}]
        xs=[{'xml_path':'a.xml','objects':[{'name':'气孔'},{'name':'气孔'},{'name':'焊缝'}]},
            {'xml_path':'b.xml','objects':[{'name':'气孔'},{'name':'裂纹'}]}]
        tasks=[{'task_id':'T1'}]
        events=[{'code':'DUPLICATE_LABEL_SET_DIFFERENCE','image_ids':['a','b'],'family':'duplicates'}]
        cov=[{'image_id':r['image_id'],'task_id':'T1' if r['image_id'] in ['a','b'] else ''} for r in rows]
        names=[{'image_id':'a','relation':'TIFF_EXTENSION_EQUIVALENT'},{'image_id':'b','relation':'EXACT'}]
        taxonomy={'status':'DRAFT_NOT_APPROVED','applied_standard':None,'entries':[
            {'label_id':name,'raw_label':name,'observed_in':'XML','definition_status':'PENDING',
             'expert_definition':None} for name in ['气孔','裂纹','焊缝']] + [
            {'label_id':'good','raw_label':'good','observed_in':'POPULATION_DIRECTORY_AND_RESEARCHER_STATEMENT',
             'definition_status':'RESEARCHER_STATEMENT','expert_definition':None}]}
        questions=[{'id':ident,'topic':ident,'question':'Synthetic review question','selector':selector} for ident,selector in [
            ('all',{'kind':'all'}),('good',{'kind':'population','value':'NORMAL_RESEARCHER_CONFIRMED'}),
            ('multi',{'kind':'multitype'}),('duplicates',{'kind':'events','codes':['DUPLICATE_LABEL_SET_DIFFERENCE']}),
            ('suffix',{'kind':'name_relation','value':'TIFF_EXTENSION_EQUIVALENT'})]]
        return rows,xs,tasks,events,cov,names,taxonomy,questions

    def test_missing_xml_is_not_a_normal_label_and_multibox_is_not_multitype(self):
        values=self.fixture();result=derive(*values,['焊缝']);scope={r['image_id']:r for r in result['scope']}
        self.assertIn('good',scope['c']['question_ids']);self.assertNotIn('good',scope['d']['question_ids'])
        self.assertNotIn('multi',scope['a']['question_ids']);self.assertIn('multi',scope['b']['question_ids'])
        self.assertEqual(scope['d']['raw_xml_labels'],[])
        self.assertTrue(all(r['review_status']=='NOT_REVIEWED' and not r['observed_defects'] for r in scope.values()))

    def test_duplicate_question_links_once_per_task_and_retains_both_variants(self):
        result=derive(*self.fixture(),['焊缝'])
        linked=[r for r in result['task_question_links'] if r['question_id']=='duplicates']
        self.assertEqual(linked,[{'question_id':'duplicates','task_id':'T1'}])
        q=next(q for q in result['questions'] if q['id']=='duplicates')
        self.assertEqual((q['affected_image_files'],q['affected_pixel_groups'],q['linked_base_tasks']),(2,1,1))
        stats={r['raw_label']:r for r in result['label_statistics']}
        self.assertEqual((stats['气孔']['object_instances'],stats['气孔']['image_files']),(3,2))
        self.assertIsNone(stats['good']['object_instances'])
        self.assertTrue(all(not q['answer'] and q['status']=='OPEN' for q in result['questions']))

    def test_new_label_is_reported_without_silent_alias_merge(self):
        values=list(self.fixture());values[1][0]['objects'].append({'name':'其它写法'})
        result=derive(*values,['焊缝'])
        self.assertEqual(result['unmapped_xml_labels'],['其它写法'])
        self.assertIn('其它写法',result['scope'][0]['raw_xml_labels'])

    def test_build_preserves_prior_files_and_refuses_raw_or_prior_outputs(self):
        rows,xs,tasks,events,cov,names,taxonomy,questions=self.fixture()
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);raw=base/'raw';audit=base/'audit';package=base/'package'
            for folder in [raw,audit,package]:folder.mkdir()
            (raw/'source.bin').write_bytes(b'unchanged synthetic source')
            for folder,filename,records in [(audit,'images.jsonl',rows),(audit,'xml_records.jsonl',xs),
                    (package,'tasks.jsonl',tasks),(package,'events.jsonl',events),
                    (package,'coverage.jsonl',cov),(package,'names.jsonl',names)]:
                (folder/filename).write_text('\n'.join(json.dumps(r) for r in records))
            (audit/'summary.json').write_text(json.dumps({'dataset_root':str(raw),'config':{'auxiliary_labels':['焊缝']}}))
            tax=base/'taxonomy.json';tax.write_text(json.dumps(taxonomy))
            qs=base/'questions.json';qs.write_text(json.dumps({'questions':questions}))
            before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for folder in [raw,audit,package] for p in folder.rglob('*') if p.is_file()}
            out=base/'draft';summary=build(audit,package,tax,qs,out)
            self.assertTrue(summary['all_base_tasks_linked']);self.assertEqual(summary['expert_decisions_created'],0)
            self.assertTrue(all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in before.items()))
            for target in [out,raw/'draft',audit/'draft',package/'draft']:
                with self.assertRaises(ValueError):build(audit,package,tax,qs,target)


if __name__=='__main__':unittest.main()
