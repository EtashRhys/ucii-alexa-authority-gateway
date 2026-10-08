import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'gateway'))
from canonical_action import CanonicalAction
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.orm import sessionmaker
from pq_auth.authorization.exact_action import ExactActionApproval
from pq_auth.database import Base
if "identities" not in Base.metadata.tables:
    Table("identities",Base.metadata,Column("id",String,primary_key=True))

# Substitute only external controller verification; use the real approval
# persistence and constraints with a temporary SQLite database.
controller = types.ModuleType('pq_auth.identity.controller_authority')
controller.ControllerAuthorityService = types.SimpleNamespace(verify=lambda *a, **kw: True)
with patch.dict(sys.modules, {'pq_auth.identity.controller_authority':controller}):
    import exact_approval

class ExactProtectedTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.root=Path(self.folder.name)
        self.human,self.agent,self.proposal=map(lambda _:str(uuid4()),range(3))
        self.env=patch.dict(os.environ,UCII_ALEXA_HUMAN_ID=self.human)
        self.env.start()
        self.now=datetime.now(timezone.utc)
        self.engine=create_engine('sqlite:///'+str(self.root/'test.sqlite3'))
        metadata=MetaData()
        Table('identities',metadata,Column('id',String,primary_key=True))
        ExactActionApproval.__table__.to_metadata(metadata)
        metadata.create_all(self.engine)
        self.factory=sessionmaker(bind=self.engine)
        self.action=CanonicalAction.from_proposal({'operation':'infrastructure.deploy','resource':'test-app','environment':'staging','artifact_digest':'sha256:'+'a'*64},subject_identity_id=self.agent)
        self.request={'version':'ucii-alexa-exact-approval-v1','operation':'approve_exact_action','proposal_id':self.proposal,'human_token':'test-human', 'action_json':self.action.canonical_message(),'action_digest':self.action.digest(),'proposal_expires_at':(self.now+timedelta(minutes=15)).isoformat()}
        self.daemon=types.SimpleNamespace(identity_id=self.agent,_session_factory=self.factory,_credential=types.SimpleNamespace(controller_authority='test-only'),verify_human=lambda token: None if token=='test-human' else (_ for _ in ()).throw(ValueError()))
        self.permit={'schema_version':exact_approval.SCHEMA,'authorization_id':str(uuid4()),'product_id':'ucii-alexa','proposal_id':self.proposal,'human_identity_id':self.human,'subject_identity_id':self.agent,'action_digest':self.action.digest(),'authorized_at':(self.now-timedelta(seconds=1)).isoformat(),'expires_at':(self.now+timedelta(minutes=3)).isoformat(),'proposal_expires_at':self.request['proposal_expires_at'],'max_uses':1}
        self.write_permit()
        original_fstat=os.fstat
        def fixture_root_owner(fd):
            values=list(original_fstat(fd));values[4]=0
            return os.stat_result(values)
        self.stat_fixture=patch.object(exact_approval.os,'fstat',side_effect=fixture_root_owner)
        self.stat_fixture.start()
    def tearDown(self):
        self.engine.dispose();self.stat_fixture.stop();self.env.stop();self.folder.cleanup()
    def write_permit(self):
        path=self.root/(self.proposal+'.exact-approval.json')
        path.write_text(json.dumps(self.permit));path.chmod(0o600)
    def call(self):
        return exact_approval.handle(self.daemon,self.request,permit_directory=self.root,now=self.now)
    def test_exact_issue_and_duplicate_reconcile_same_record(self):
        first=self.call();second=self.call()
        self.assertEqual(first,second)
        self.assertFalse(first['approval']['execution_allowed'])
        with self.factory() as db:self.assertEqual(db.query(ExactActionApproval).count(),1)
    def test_wrong_human_session_controller_or_permit_denied(self):
        self.request['human_token']='bad'
        with self.assertRaises(ValueError):self.call()
        self.request['human_token']='test-human'
        with patch.object(exact_approval.ControllerAuthorityService,'verify',return_value=False):
            with self.assertRaises(ValueError):self.call()
        self.permit['human_identity_id']=str(uuid4());self.write_permit()
        with self.assertRaises(ValueError):self.call()
    def test_changed_exact_action_denied(self):
        changed=CanonicalAction.from_proposal({'operation':'infrastructure.deploy','resource':'other-app','environment':'staging','artifact_digest':'sha256:'+'a'*64},subject_identity_id=self.agent)
        self.request.update(action_json=changed.canonical_message(),action_digest=changed.digest())
        with self.assertRaises(ValueError):self.call()
    def test_expired_or_writable_permit_denied(self):
        self.permit['expires_at']=(self.now-timedelta(seconds=1)).isoformat();self.write_permit()
        with self.assertRaises(ValueError):self.call()
        self.permit['expires_at']=(self.now+timedelta(minutes=1)).isoformat();self.write_permit()
        (self.root/(self.proposal+'.exact-approval.json')).chmod(0o622)
        with self.assertRaises(ValueError):self.call()
    def test_status_is_owner_bound_and_does_not_issue(self):
        request={k:self.request[k] for k in ('version','proposal_id','human_token')}
        request['operation']='exact_approval_status'
        self.assertIsNone(exact_approval.handle(self.daemon,request,permit_directory=self.root)['approval'])
        self.call()
        self.assertEqual(exact_approval.handle(self.daemon,request,permit_directory=self.root)['approval']['state'],'ACTIVE')

if __name__=='__main__':unittest.main()
