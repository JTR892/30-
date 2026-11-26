"""Fail-closed administrative v0.5 gate; flags do not independently prove evidence."""
import argparse
import json
from pathlib import Path

PARAMS = ["max_steps", "batch_size", "input_size", "optimizer", "learning_rate",
          "temperature", "weight_decay", "augmentation_spec", "pretrained_weights_sha256",
          "analysis_spec_sha256", "split_manifest_sha256", "taxonomy_sha256",
          "group_mapping_sha256", "dataset_audit_sha256", "checkpoint_rule", "primary_contrast"]
GATES = ["dataset_audit_passed", "taxonomy_review_passed", "source_groups_verified",
         "duplicate_review_passed", "usage_permission_confirmed", "pilot_protocol_frozen",
         "real_image_pilot_passed", "training_implementation_validated",
         "test_labels_locked", "analysis_spec_frozen"]


def issues(c):
    out = []
    if not str(c.get("version", "")).startswith("0.5"):
        out.append("Unsupported protocol version: active research requires v0.5; v0.4 is historical")
    if c.get("status") != "FROZEN":
        out.append("Protocol has not been frozen")
    for k in PARAMS:
        if c.get(k) is None or c.get(k) == "":
            out.append(f"Unspecified parameter: {k}")
    for k in GATES:
        if c.get(k) is not True:
            out.append(f"Gate not passed: {k}")
    k = c.get("cluster_k")
    if isinstance(k, bool) or not isinstance(k, int) or k < 2:
        out.append("Specify a valid cluster_k after taxonomy/calibration review; do not inherit K=2")
    if c.get("cluster_k_policy") not in {"known_k_disclosed", "unlabeled_calibration_frozen_rule"}:
        out.append("Specify and disclose cluster_k_policy")
    if c.get("source_film_mapping_required") is not True:
        out.append("Verified source-connected groups are required by the research agreement")
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    a = p.parse_args()
    result = issues(json.loads(Path(a.config).read_text()))
    print(json.dumps({"ready_for_training": not result, "issues": result,
                      "scope": "Administrative contract check; evidence artifacts require review; no trainer is executed"},
                     ensure_ascii=False, indent=2))
    raise SystemExit(2 if result else 0)
