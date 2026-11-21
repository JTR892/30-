"""Synthetic fixtures only; these tests are not real industrial-data validation."""
import csv
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from weldstudy.audit import audit
from weldstudy.split import make_splits, read_csv
from weldstudy.protocol import issues

class DataContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name);self.raw=self.base/'raw';self.raw.mkdir()
    def image(self,name,color): Image.new('L',(12,10),color).save(self.raw/name)
    def mapping(self,rows,change=None):
        target=self.base/'groups.csv'
        with target.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['image_id','group_id']);w.writeheader()
            for i,r in enumerate(rows): w.writerow({'image_id':r['image_id'],'group_id':(change(r,i) if change else f'g{i}')})
        return target
    def test_inventory_does_not_infer_normal(self):
        self.image('a.png',3);(self.raw/'broken.png').write_bytes(b'bad');(self.raw/'study.dcm').write_bytes(b'dummy')
        report=audit(self.raw,self.base/'audit');rows=read_csv(self.base/'audit/manifest.csv')
        self.assertEqual(report['n_image_files'],2);self.assertEqual(len(report['unsupported_image_files']),1)
        self.assertTrue(all(r['defect_classes']=='' and r['annotation_status']=='UNREVIEWED' for r in rows))
        self.assertTrue(any(r['quality_status'].startswith('UNREADABLE') for r in rows))
    def test_empty_dataset_fails(self):
        with self.assertRaises(ValueError): audit(self.raw,self.base/'audit')
    def test_partition_disjoint_nested_deterministic(self):
        for i in range(30): self.image(f'{i}.png',i)
        audit(self.raw,self.base/'audit');manifest=self.base/'audit/manifest.csv';rows=read_csv(manifest);mapping=self.mapping(rows)
        a=make_splits(manifest,mapping,self.base/'s1');b=make_splits(manifest,mapping,self.base/'s2')
        self.assertEqual(a,b)
        load=lambda n:{r['group_id'] for r in read_csv(self.base/f's1/{n}.csv')}
        self.assertTrue(load('train_10')<=load('train_50')<=load('train_100'))
        self.assertFalse(load('train_100')&load('test'));self.assertFalse(load('calibration')&load('test'));self.assertFalse(load('train_100')&load('calibration'))
        self.assertNotIn('defect_classes',read_csv(self.base/'s1/train_100.csv')[0])
        make_splits(manifest,mapping,self.base/'s3',seed=29)
        self.assertEqual(read_csv(self.base/'s1/test.csv'),read_csv(self.base/'s3/test.csv'))
        self.assertEqual(read_csv(self.base/'s1/calibration.csv'),read_csv(self.base/'s3/calibration.csv'))
    def test_duplicate_content_across_groups_fails(self):
        for i in range(12): self.image(f'{i}.png',i)
        self.image('dup.png',0);audit(self.raw,self.base/'audit');manifest=self.base/'audit/manifest.csv';rows=read_csv(manifest)
        with self.assertRaisesRegex(ValueError,'duplicate content'): make_splits(manifest,self.mapping(rows),self.base/'split')
    def test_missing_group_fails(self):
        self.image('a.png',1);audit(self.raw,self.base/'audit');manifest=self.base/'audit/manifest.csv'
        with self.assertRaises(ValueError): make_splits(manifest,self.mapping([]),self.base/'split')
    def test_unfrozen_protocol_fails(self): self.assertTrue(issues({'status':'DRAFT'}))

if __name__=='__main__':unittest.main()
