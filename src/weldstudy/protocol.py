import argparse
import json
from pathlib import Path

def issues(c):
    problems=[]
    if not str(c.get("version", "")).startswith("0.2"):
        problems.append("Unsupported protocol version: final training requires the three-layer v0.2 contract")
    if c.get("status") != "FROZEN": problems.append("Protocol has not been frozen")
    for k in ["max_steps","batch_size","input_size","optimizer","learning_rate","temperature","weight_decay","augmentation_spec","pretrained_weights_sha256","cluster_k","primary_contrast","checkpoint_rule","analysis_spec_sha256","semantic_analysis_scope"]:
        if c.get(k) is None or c.get(k) == "": problems.append(f"Unspecified parameter: {k}")
    for k in ["group_audit_passed","mps_training_smoke_passed","test_labels_locked","analysis_spec_frozen","semantic_evidence_audited"]:
        if c.get(k) is not True: problems.append(f"Gate not passed: {k}")
    return problems

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--config",required=True);a=p.parse_args();result=issues(json.loads(Path(a.config).read_text()))
    print(json.dumps({"ready_for_training":not result,"issues":result},ensure_ascii=False,indent=2));raise SystemExit(2 if result else 0)

