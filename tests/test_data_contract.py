"""Synthetic tests for binary image-level audit/splitting only."""
import csv,json,tempfile,unittest
from pathlib import Path
from PIL import Image
from weldstudy.audit import audit
from weldstudy.split import make_splits,read_csv

class DataContractTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
  self.raw=self.base/"raw";(self.raw/"defect").mkdir(parents=True);(self.raw/"normal").mkdir()
  self.map=self.base/"map.json";self.map.write_text(json.dumps({"defect":"defect","normal":"no_defect"}))
 def image(self,folder,name,value): Image.new("L",(12,10),value).save(self.raw/folder/name)
 def test_explicit_mapping_and_inventory(self):
  self.image("defect","a.png",2);r=audit(self.raw,self.base/"audit")
  self.assertEqual(r["unmapped_label_images"],1)
  r=audit(self.raw,self.base/"audit2",self.map);self.assertEqual(r["label_counts"],{"defect":1})
 def test_stratified_nested_split_and_label_separation(self):
  for i in range(20): self.image("defect",f"d{i}.png",i+1);self.image("normal",f"n{i}.png",i+101)
  audit(self.raw,self.base/"audit",self.map);m=self.base/"audit/manifest.csv"
  a=make_splits(m,self.base/"s1");b=make_splits(m,self.base/"s2");self.assertEqual(a,b)
  load=lambda n:{x["image_id"] for x in read_csv(self.base/"s1"/f"{n}.csv")}
  self.assertTrue(load("train_10")<=load("train_50")<=load("train_100"))
  self.assertFalse(load("train_100")&load("calibration"));self.assertFalse(load("train_100")&load("test"))
  self.assertNotIn("binary_label",read_csv(self.base/"s1/train_100.csv")[0])
  self.assertNotIn("binary_label",read_csv(self.base/"s1/test.csv")[0])
  self.assertEqual(len(read_csv(self.base/"s1/test_labels.locked.csv")),len(load("test")))
 def test_conflicting_duplicate_labels_fail(self):
  self.image("defect","same.png",7);self.image("normal","same.png",7);audit(self.raw,self.base/"audit",self.map)
  with self.assertRaisesRegex(ValueError,"conflicting binary labels"):make_splits(self.base/"audit/manifest.csv",self.base/"s")
 def test_unreadable_or_unmapped_is_not_silently_accepted(self):
  self.image("defect","a.png",7);audit(self.raw,self.base/"audit")
  with self.assertRaisesRegex(ValueError,"explicit defect/no_defect"):make_splits(self.base/"audit/manifest.csv",self.base/"s")

if __name__=="__main__":unittest.main()
