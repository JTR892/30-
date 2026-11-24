"""Final-stage v0.3 protocol gate."""
import argparse,json
from pathlib import Path
PARAMS=["max_steps","batch_size","input_size","optimizer","learning_rate","temperature","weight_decay","augmentation_spec","pretrained_weights_sha256","analysis_spec_sha256","split_manifest_sha256","checkpoint_rule"]
GATES=["dataset_audit_passed","binary_label_map_verified","exact_duplicate_audit_passed","usage_permission_confirmed","mps_training_smoke_passed","test_labels_locked","analysis_spec_frozen"]
def issues(c):
    out=[]
    if not str(c.get("version","")).startswith("0.3"): out.append("Unsupported protocol version: requires v0.3")
    if c.get("status")!="FROZEN": out.append("Protocol has not been frozen")
    for k in PARAMS:
        if c.get(k) is None or c.get(k)=="": out.append(f"Unspecified parameter: {k}")
    for k in GATES:
        if c.get(k) is not True: out.append(f"Gate not passed: {k}")
    if c.get("cluster_k")!=2: out.append("Primary experiment must use known K=2")
    if c.get("source_film_mapping_required") is not False: out.append("Source-film mapping must not be reintroduced as a v0.3 gate")
    return out
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--config",required=True);a=p.parse_args()
    result=issues(json.loads(Path(a.config).read_text()))
    print(json.dumps({"ready_for_training":not result,"issues":result},ensure_ascii=False,indent=2))
    raise SystemExit(2 if result else 0)
