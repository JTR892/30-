"""Final-stage contract tests; no model or real-data validation."""
import json
import unittest
from pathlib import Path

from weldstudy.protocol import issues


class ProtocolGateTests(unittest.TestCase):
    def completed_contract(self):
        # This fixture describes an administratively complete contract only.
        config = json.loads((Path(__file__).resolve().parents[1] / 'config/protocol.json').read_text())
        config.update(status='FROZEN', version='0.2', max_steps=10, batch_size=2,
                      input_size=32, optimizer='fixture', learning_rate=0.01,
                      temperature=0.1, weight_decay=0, augmentation_spec='fixture',
                      pretrained_weights_sha256='a' * 64, cluster_k=2,
                      group_audit_passed=True, mps_training_smoke_passed=True,
                      test_labels_locked=True, analysis_spec_frozen=True,
                      semantic_evidence_audited=True, analysis_spec_sha256='b' * 64,
                      semantic_analysis_scope='No location metadata; source diagnostics only')
        return config

    def test_unfrozen_analysis_rejects_otherwise_complete_final_contract(self):
        config = self.completed_contract()
        config['analysis_spec_frozen'] = False
        self.assertIn('Gate not passed: analysis_spec_frozen', issues(config))

    def test_missing_evidence_audit_rejects_final_contract(self):
        config = self.completed_contract()
        config['semantic_evidence_audited'] = False
        self.assertIn('Gate not passed: semantic_evidence_audited', issues(config))

    def test_unavailable_location_analysis_can_be_explicitly_scoped(self):
        self.assertEqual(issues(self.completed_contract()), [])

    def test_legacy_contract_cannot_bypass_new_analysis_gates(self):
        config = self.completed_contract()
        config['version'] = '0.1'
        self.assertTrue(any('Unsupported protocol version' in p for p in issues(config)))


if __name__ == '__main__':
    unittest.main()
