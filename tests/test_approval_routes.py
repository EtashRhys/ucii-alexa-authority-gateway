import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from uuid import uuid4
from unittest.mock import patch
from starlette.responses import JSONResponse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gateway'))
from approval_routes import install
from canonical_action import CanonicalAction
from proposals import ProposalStore

class Routes:
    def custom_route(self,path,methods):
        def register(fn):self.route=fn;return fn
        return register
class Request:
    method='POST'
    query_params={}
    def __init__(self,body):self.body_data=body
    async def body(self):return json.dumps(self.body_data).encode()
class ApprovalRoutesTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.path=Path(self.folder.name)/'draft.sqlite3'
        self.human,self.agent=str(uuid4()),str(uuid4())
        self.environment=patch.dict(os.environ,UCII_ALEXA_PROPOSALS_PATH=str(self.path),UCII_ALEXA_AGENT_ID=self.agent);self.environment.start()
        self.store=ProposalStore(self.path)
        self.action=CanonicalAction.from_proposal({'operation':'compute.inspect','resource':'test-app','environment':'staging'},subject_identity_id=self.agent)
        self.p=self.store.create(self.action,human_identity_id=self.human,idempotency_key=str(uuid4()))
        self.body={'proposal_id':self.p['proposal_id'],'action_digest':self.p['action_digest'],'confirmation':'APPROVE_EXACT_ACTION_ONCE'}
    def tearDown(self):self.environment.stop();self.folder.cleanup()
    def run_route(self,exchange,authenticated=True):
        mcp=Routes()
        async def session(request,op):
            if not authenticated:raise PermissionError()
            return op('test-only',self.human)
        install(mcp,session,exchange,lambda data,status=200:JSONResponse(data,status_code=status))
        return asyncio.run(mcp.route(Request(self.body)))
    def test_no_session_or_changed_digest_sends_no_ipc(self):
        def never(intent):self.fail('IPC must not be called')
        self.assertEqual(self.run_route(never,False).status_code,401)
        self.body['action_digest']='sha256:'+'a'*64
        self.assertEqual(self.run_route(never).status_code,409)
    def test_cancelled_draft_cannot_be_approved(self):
        self.store.get(self.p['proposal_id'],human_identity_id=self.human,cancel=True)
        self.assertEqual(self.run_route(lambda _:self.fail('IPC must not be called')).status_code,409)
    def test_claim_prevents_cancellation_and_uncertain_resubmission(self):
        def uncertain(intent):
            with self.assertRaises(FileExistsError):self.store.get(self.p['proposal_id'],human_identity_id=self.human,cancel=True)
            return {'status':'uncertain'}
        self.assertEqual(self.run_route(uncertain).status_code,503)
        self.assertEqual(self.run_route(lambda _:self.fail('No duplicate request')).status_code,409)
        self.assertEqual(self.store.get(self.p['proposal_id'],human_identity_id=self.human)['state'],'APPROVAL_PENDING')
if __name__=='__main__':unittest.main()
