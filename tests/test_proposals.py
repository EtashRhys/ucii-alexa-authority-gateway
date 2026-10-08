"""Stored drafts never constitute authority or executor receipts."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gateway'))
from canonical_action import CanonicalAction
from proposals import ProposalStore


class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / 'proposals.sqlite3'
        self.store = ProposalStore(self.path)
        self.action = CanonicalAction(str(uuid4()), 'infrastructure.deploy', 'test-app', 'staging', 'sha256:' + 'a' * 64)
        self.owner = str(uuid4())
        self.key = str(uuid4())

    def tearDown(self):
        self.directory.cleanup()

    def create(self, action=None, now=100):
        return self.store.create(action or self.action, human_identity_id=self.owner, idempotency_key=self.key, now=now)

    def test_persistent_exact_snapshot_with_no_authority(self):
        result = self.create()
        loaded = ProposalStore(self.path).get(result['proposal_id'], human_identity_id=self.owner, now=101)
        self.assertEqual(result, loaded)
        self.assertEqual(loaded['action_digest'], self.action.digest())
        self.assertFalse(loaded['execution_allowed'])
        self.assertEqual(loaded['approval'], 'NOT_ESTABLISHED')
        self.assertNotIn('token', loaded)

    def test_idempotency_preserves_original_expiry(self):
        first = self.create()
        self.assertEqual(first, self.create(now=200))

    def test_same_key_changed_action_conflicts(self):
        first = self.create()
        with self.assertRaises(FileExistsError):
            self.create(replace(self.action, resource='other-app'))
        self.assertEqual(first['action']['resource'], 'test-app')

    def test_other_human_cannot_retrieve_or_cancel(self):
        result = self.create()
        for cancel in (False, True):
            with self.assertRaises(LookupError):
                self.store.get(result['proposal_id'], human_identity_id=str(uuid4()), cancel=cancel, now=101)

    def test_cancel_and_retry_cannot_restore_proposal(self):
        result = self.create()
        cancelled = self.store.get(result['proposal_id'], human_identity_id=self.owner, cancel=True, now=101)
        self.assertEqual(cancelled['state'], 'CANCELLED')
        self.assertEqual(self.create(now=102)['state'], 'CANCELLED')

    def test_expiry_never_renews_on_retry(self):
        self.create()
        self.assertEqual(self.create(now=1000)['state'], 'EXPIRED')

    def test_parallel_retries_create_one_snapshot(self):
        self.create()  # initialize schema before concurrent transactions
        with ThreadPoolExecutor(max_workers=4) as executor:
            records = list(executor.map(lambda _: self.create(now=150), range(8)))
        self.assertEqual(len({r['proposal_id'] for r in records}), 1)


if __name__ == '__main__':
    unittest.main()
