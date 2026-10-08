"""Canonical action binding tests; no authority is granted or executed."""
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gateway"))
from canonical_action import CanonicalAction

SUBJECT = "00000000-0000-4000-8000-000000000001"
ARTIFACT = "sha256:" + "a" * 64


class CanonicalActionTests(unittest.TestCase):
    def action(self):
        return CanonicalAction(SUBJECT, "infrastructure.deploy", "test-app", "staging", ARTIFACT)

    def test_order_independent_proposal_and_server_bound_subject(self):
        proposal = {"artifact_digest": ARTIFACT, "environment": "staging", "resource": "test-app", "operation": "infrastructure.deploy"}
        action = CanonicalAction.from_proposal(proposal, subject_identity_id=SUBJECT)
        self.assertEqual(action.canonical_message(), self.action().canonical_message())
        self.assertEqual(action.digest(), self.action().digest())

    def test_each_execution_field_changes_binding(self):
        action = self.action()
        variants = {
            "subject_identity_id": "00000000-0000-4000-8000-000000000002",
            "operation": "infrastructure.inspect", "resource": "other-app",
            "environment": "production", "artifact_digest": "sha256:" + "b" * 64,
        }
        for field, value in variants.items():
            with self.subTest(field=field):
                self.assertNotEqual(action.digest(), replace(action, **{field: value}).digest())

    def test_missing_or_mutable_deployment_artifact_rejected(self):
        for value in (None, "latest", "main", "sha256:" + "A" * 64):
            with self.subTest(value=value), self.assertRaises(ValueError):
                replace(self.action(), artifact_digest=value)

    def test_ambiguous_scope_rejected(self):
        for resource in ("", "*", "test-*", " test-app", "test-app\n", "a" * 513):
            with self.subTest(resource=resource), self.assertRaises(ValueError):
                replace(self.action(), resource=resource)
        for environment in ("not applicable", "any", "STAGING"):
            with self.subTest(environment=environment), self.assertRaises(ValueError):
                replace(self.action(), environment=environment)

    def test_browser_subject_and_extra_fields_rejected(self):
        proposal = {"operation": "infrastructure.inspect", "resource": "test-app", "environment": "staging"}
        for key in ("subject_identity_id", "approved", "signature"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                CanonicalAction.from_proposal({**proposal, key: SUBJECT}, subject_identity_id=SUBJECT)

    def test_action_is_immutable(self):
        action = self.action()
        with self.assertRaises(FrozenInstanceError):
            action.resource = "other-app"


if __name__ == "__main__":
    unittest.main()
