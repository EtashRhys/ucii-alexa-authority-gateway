import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from datetime import datetime
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gateway'))
import activity
import executor_service

class ActivityTests(unittest.TestCase):
    def test_saved_receipts_and_permission_history(self):
        row=types.SimpleNamespace(id='authority',allowed_operations=['sandbox.artifact.verify'],granted_at=datetime(2026,10,9,12),revoked_at=datetime(2026,10,9,13))
        query=types.SimpleNamespace(filter=lambda *args:types.SimpleNamespace(all=lambda:[row]))
        db=types.SimpleNamespace(query=lambda *args:query)
        with tempfile.TemporaryDirectory() as root:
            receipt={'request_id':'receipt','subject_identity_id':'agent','operation':'sandbox.artifact.verify','status':'completed','artifact_matches':True,'checked_at':'2026-10-09T14:00:00+00:00','deployed':False}
            Path(root,'tool-one.json').write_text(json.dumps(receipt))
            Path(root,'tool-other.json').write_text(json.dumps({**receipt,'subject_identity_id':'other'}))
            Path(root,'tool-invalid.json').write_text('{')
            result=activity.read(db,agent='agent',receipts=root)
            self.assertEqual([r['result'] for r in result],['matched','blocked','allowed'])
            self.assertEqual(activity.read(db,agent='agent',receipts=root),result)
    def test_invalid_human_prevents_activity_access(self):
        with patch.object(executor_service,'verify_human',side_effect=PermissionError),patch('builtins.open') as opened:
            with self.assertRaises(PermissionError):
                executor_service.handle({'version':'ucii-alexa-activity-v1','human_token':'bad'},lambda:self.fail('Database opened'))
            opened.assert_not_called()
