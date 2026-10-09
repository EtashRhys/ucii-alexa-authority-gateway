import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gateway'))
from conversation_tool import run, EXPECTED

class ConversationToolTests(unittest.TestCase):
    def test_allowed_and_blocked_are_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);root.chmod(0o700)
            artifact=root/'artifact';artifact.write_bytes(EXPECTED);artifact.chmod(0o444)
            # Local test owner is root in this runtime, matching production custody.
            for allowed in (True,False):
                request={'version':'ucii-alexa-conversation-tool-v1','request_id':str(uuid4())}
                result=run(request,agent=str(uuid4()),verify=lambda action:allowed,
                    artifact=artifact,receipts=root)
                self.assertEqual(result['status'],'completed' if allowed else 'blocked')
                self.assertEqual(result['artifact_matches'],True if allowed else None)
                self.assertEqual(json.loads((root/('tool-'+request['request_id']+'.json')).read_text()),result)
    def test_blocked_never_reads_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory).chmod(0o700)
            result=run({'version':'ucii-alexa-conversation-tool-v1','request_id':str(uuid4())},
                agent=str(uuid4()),verify=lambda action:False,artifact='/missing',receipts=directory)
            self.assertEqual(result['status'],'blocked')
    def test_changed_permission_and_extra_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);root.chmod(0o700);artifact=root/'artifact'
            artifact.write_bytes(EXPECTED);artifact.chmod(0o444)
            outcomes=iter([True,False]);request={'version':'ucii-alexa-conversation-tool-v1','request_id':str(uuid4())}
            result=run(request,agent=str(uuid4()),verify=lambda action:next(outcomes),artifact=artifact,receipts=root)
            self.assertEqual(result['status'],'blocked');self.assertIsNone(result['artifact_matches'])
            with self.assertRaises(ValueError):
                run({**request,'resource':'production'},agent=str(uuid4()),verify=lambda action:True,artifact=artifact,receipts=root)
