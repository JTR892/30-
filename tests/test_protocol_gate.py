"""Synthetic contract checks, never proof that data or training are qualified."""
import json
import unittest
from pathlib import Path
from weldstudy.protocol import issues, PARAMS, GATES


class ProtocolGateTests(unittest.TestCase):
    def fixture(self):
        c = dict.fromkeys(PARAMS, "synthetic-administrative-fixture")
        c.update(dict.fromkeys(GATES, True))
        c.update(version="0.5", status="FROZEN", cluster_k=5,
                 cluster_k_policy="known_k_disclosed", source_film_mapping_required=True)
        return c

    def test_complete_synthetic_contract_is_administratively_accepted(self):
        self.assertEqual(issues(self.fixture()), [])

    def test_actual_draft_remains_closed(self):
        c = json.loads((Path(__file__).resolve().parents[1]/"config/protocol.json").read_text())
        self.assertIn("Protocol has not been frozen", issues(c))
        self.assertIn("Gate not passed: dataset_audit_passed", issues(c))

    def test_old_binary_contract_cannot_authorize_new_research(self):
        c = self.fixture()
        c.update(version="0.4", cluster_k=2, source_film_mapping_required=False)
        result = issues(c)
        self.assertTrue(any("historical" in r for r in result))
        self.assertTrue(any("source-connected" in r for r in result))

    def test_small_or_untyped_cluster_count_rejected(self):
        for value in [None, True, 1, 2.5, "5"]:
            c = self.fixture(); c["cluster_k"] = value
            self.assertTrue(any("valid cluster_k" in r for r in issues(c)))

    def test_missing_evidence_flag_blocks_contract(self):
        c = self.fixture(); c["taxonomy_review_passed"] = False
        self.assertIn("Gate not passed: taxonomy_review_passed", issues(c))

    def test_xml_audit_does_not_authorize_a_real_image_pilot(self):
        c = self.fixture(); c["real_image_pilot_passed"] = False
        self.assertIn("Gate not passed: real_image_pilot_passed", issues(c))


if __name__ == "__main__":
    unittest.main()
