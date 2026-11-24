"""Synthetic v0.4 final-gate tests."""
import json,unittest
from pathlib import Path
from weldstudy.protocol import issues
class ProtocolGateTests(unittest.TestCase):
 def fixture(self):
  c=json.loads((Path(__file__).resolve().parents[1]/"config/protocol.json").read_text())
  c.update(version="0.4",status="FROZEN",max_steps=10,batch_size=2,input_size=32,optimizer="x",learning_rate=.01,temperature=.1,weight_decay=0,augmentation_spec="x",pretrained_weights_sha256="a"*64,analysis_spec_sha256="b"*64,split_manifest_sha256="c"*64,checkpoint_rule="last",cluster_k=2,source_film_mapping_required=False)
  for k in ["dataset_audit_passed","binary_label_map_verified","exact_duplicate_audit_passed","usage_permission_confirmed","mps_training_smoke_passed","test_labels_locked","analysis_spec_frozen"]:c[k]=True
  return c
 def test_draft_rejected(self):self.assertTrue(issues({"version":"0.4-draft","status":"DRAFT"}))
 def test_complete_fixture_passes(self):self.assertEqual(issues(self.fixture()),[])
 def test_missing_gate_rejected(self):
  c=self.fixture();c["binary_label_map_verified"]=False
  self.assertIn("Gate not passed: binary_label_map_verified",issues(c))
 def test_wrong_k_rejected(self):
  c=self.fixture();c["cluster_k"]=3
  self.assertIn("Primary experiment must use known K=2",issues(c))
 def test_missing_source_mapping_policy_rejected(self):
  c=self.fixture();c.pop("source_film_mapping_required")
  self.assertIn("Source-film mapping must not be reintroduced as a v0.4 gate",issues(c))
if __name__=="__main__":unittest.main()
