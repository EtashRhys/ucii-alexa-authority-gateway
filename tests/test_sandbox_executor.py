import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gateway'))
from sqlalchemy import create_engine, MetaData, Table, Column, String
from sqlalchemy.orm import sessionmaker
from pq_auth.database import Base
from pq_auth.authorization.exact_action import ExactActionApproval, ExactActionApprovalService
if 'identities' not in Base.metadata.tables:
    Table('identities',Base.metadata,Column('id',String,primary_key=True))
from canonical_action import CanonicalAction
from sandbox_executor import execute, SandboxDenied, SandboxUncertain

class SandboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.receipts=self.root/'receipts';self.receipts.mkdir(mode=0o700)
        self.artifact=self.root/'artifact.json';self.artifact.write_text('{"sandbox":"UCII"}\n')
        self.human,self.agent=str(uuid4()),str(uuid4());self.now=datetime.utcnow()
        self.engine=create_engine('sqlite:///'+str(self.root/'db'))
        metadata=MetaData();Table('identities',metadata,Column('id',String,primary_key=True))
        ExactActionApproval.__table__.to_metadata(metadata);metadata.create_all(self.engine)
        self.db=sessionmaker(bind=self.engine)()
        self.action=CanonicalAction.from_proposal({'operation':'sandbox.artifact.verify','resource':'test-app','environment':'staging','artifact_digest':'sha256:'+hashlib.sha256(self.artifact.read_bytes()).hexdigest()},subject_identity_id=self.agent)
        self.row=ExactActionApprovalService.issue(self.db,product_id='ucii-alexa',proposal_id=str(uuid4()),subject_identity_id=self.agent,human_identity_id=self.human,action_json=self.action.canonical_message(),action_digest=self.action.digest(),issuance_authorization_id=str(uuid4()),now=self.now,expires_at=self.now+timedelta(minutes=3))
        self.args=dict(approval_id=self.row.id,human_identity_id=self.human,subject_identity_id=self.agent,action_json=self.action.canonical_message(),action_digest=self.action.digest(),artifact_path=self.artifact,receipt_directory=self.receipts,verify_current_evidence=lambda action:True,clock=lambda:self.now)
    def tearDown(self):
        self.db.close();self.engine.dispose();self.tmp.cleanup()
    def state(self):
        self.db.refresh(self.row);return self.row.state
    def test_receipt_and_single_use(self):
        result=execute(self.db,**self.args)
        self.assertEqual(result['outcome'],'ARTIFACT_VERIFIED');self.assertFalse(result['deployment_performed'])
        self.assertEqual(self.state(),'CONSUMED')
        files=list(self.receipts.iterdir());self.assertEqual(len(files),1)
        self.assertEqual(json.loads(files[0].read_text()),result)
        with self.assertRaises(SandboxDenied):execute(self.db,**self.args)
        self.assertEqual(len(list(self.receipts.iterdir())),1)
    def test_revoked_or_expired_produces_no_effect(self):
        self.args['clock']=lambda:self.now+timedelta(minutes=4)
        with self.assertRaises(SandboxDenied):execute(self.db,**self.args)
        self.args['clock']=lambda:self.now
        ExactActionApprovalService.revoke(self.db,approval_id=self.row.id,human_identity_id=self.human,reason='test',now=self.now)
        with self.assertRaises(SandboxDenied):execute(self.db,**self.args)
        self.assertEqual(list(self.receipts.iterdir()),[])
    def test_missing_evidence_or_artifact_mismatch_does_not_reserve(self):
        self.args['verify_current_evidence']=lambda action:False
        with self.assertRaises(SandboxDenied):execute(self.db,**self.args)
        self.args['verify_current_evidence']=lambda action:True
        self.artifact.write_text('changed')
        with self.assertRaises(SandboxDenied):execute(self.db,**self.args)
        self.assertEqual(self.state(),'ACTIVE');self.assertEqual(list(self.receipts.iterdir()),[])
    def test_evidence_loss_after_reservation_blocks_effect_and_retry(self):
        answers=iter([True,False]);self.args['verify_current_evidence']=lambda action:next(answers)
        with self.assertRaises(SandboxUncertain):execute(self.db,**self.args)
        self.assertEqual(self.state(),'RESERVED');self.assertEqual(list(self.receipts.iterdir()),[])
        self.args['verify_current_evidence']=lambda action:True
        with self.assertRaises(SandboxDenied):execute(self.db,**self.args)
    def test_changed_binding_and_real_deployment_rejected(self):
        for operation,resource in [('sandbox.artifact.verify','other-app'),('infrastructure.deploy','test-app')]:
            changed=CanonicalAction.from_proposal({'operation':operation,'resource':resource,'environment':'staging','artifact_digest':self.action.artifact_digest},subject_identity_id=self.agent)
            args={**self.args,'action_json':changed.canonical_message(),'action_digest':changed.digest()}
            with self.assertRaises(SandboxDenied):execute(self.db,**args)
        self.assertEqual(self.state(),'ACTIVE')
    def test_uncertain_commit_keeps_durable_receipt_and_no_retry(self):
        with patch.object(ExactActionApprovalService,'consume',side_effect=RuntimeError('lost database')):
            with self.assertRaises(SandboxUncertain):execute(self.db,**self.args)
        self.assertEqual(self.state(),'RESERVED');self.assertEqual(len(list(self.receipts.iterdir())),1)
        with self.assertRaises(SandboxDenied):execute(self.db,**self.args)
    def test_artifact_symlink_rejected(self):
        link=self.root/'link';link.symlink_to(self.artifact);self.args['artifact_path']=link
        with self.assertRaises(OSError):execute(self.db,**self.args)
        self.assertEqual(self.state(),'ACTIVE')

if __name__=='__main__':unittest.main()
