import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from uuid import uuid4
from sqlalchemy import create_engine,MetaData,Table,Column,String
from sqlalchemy.orm import sessionmaker
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gateway'))
from pq_auth.authorization.models import ActionAuthority,ActionAuthorityStatus
from pq_auth.database import Base
if 'identities' not in Base.metadata.tables:Table('identities',Base.metadata,Column('id',String,primary_key=True))
controller=types.ModuleType('pq_auth.identity.controller_authority');controller.ControllerAuthorityService=types.SimpleNamespace(verify=lambda *a,**kw:True)
with patch.dict(sys.modules,{'pq_auth.identity.controller_authority':controller}):import tool_permissions

class ToolPermissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.engine=create_engine('sqlite:///'+str(Path(self.tmp.name)/'db'))
        metadata=MetaData();Table('identities',metadata,Column('id',String,primary_key=True));ActionAuthority.__table__.to_metadata(metadata);metadata.create_all(self.engine)
        self.factory=sessionmaker(bind=self.engine);self.human,self.agent=str(uuid4()),str(uuid4())
        self.env=patch.dict(os.environ,UCII_ALEXA_HUMAN_ID=self.human);self.env.start()
        self.daemon=types.SimpleNamespace(identity_id=self.agent,_session_factory=self.factory,_credential=types.SimpleNamespace(controller_authority='test'),verify_human=lambda token:None if token=='human' else (_ for _ in ()).throw(PermissionError()))
    def tearDown(self):self.engine.dispose();self.env.stop();self.tmp.cleanup()
    def call(self,command='get',**changes):
        return tool_permissions.handle(self.daemon,{'version':'ucii-alexa-tool-permission-v1','operation':tool_permissions.OPERATION,'command':command,'confirmation':'' if command=='get' else 'CONFIRM_TOOL_PERMISSION','human_token':'human',**changes})
    def test_allow_block_restore_preserves_history_and_scope(self):
        self.assertEqual(self.call()['permission']['mode'],'BLOCKED')
        first=self.call('allow')['permission'];self.assertEqual(first['mode'],'ALLOWED')
        self.assertEqual(self.call('allow')['permission']['authority_id'],first['authority_id'])
        self.assertEqual(self.call('block')['permission']['mode'],'BLOCKED')
        second=self.call('allow')['permission'];self.assertNotEqual(first['authority_id'],second['authority_id'])
        with self.factory() as db:
            rows=db.query(ActionAuthority).all();self.assertEqual(len(rows),2)
            self.assertTrue(all(row.allowed_operations==[tool_permissions.OPERATION] for row in rows))
            self.assertEqual(db.get(ActionAuthority,first['authority_id']).status,ActionAuthorityStatus.REVOKED)
    def test_no_session_wrong_scope_or_confirmation_cannot_grant(self):
        for changes in ({'human_token':''},{'operation':'infrastructure.deploy'},{'confirmation':'model approved'},{'subject_identity_id':self.agent}):
            with self.assertRaises((ValueError,PermissionError)):self.call('allow',**changes)
        with self.factory() as db:self.assertEqual(db.query(ActionAuthority).count(),0)
    def test_shopping_and_artifact_permissions_are_independent(self):
        self.call('allow')
        self.assertEqual(self.call('get',operation='shopping.list.edit')['permission']['mode'],'BLOCKED')
        self.call('allow',operation='shopping.list.edit')
        self.call('block',operation='shopping.list.edit')
        self.assertEqual(self.call()['permission']['mode'],'ALLOWED')
        self.assertEqual(self.call('get',operation='shopping.list.edit')['permission']['mode'],'BLOCKED')

    def test_controller_failure_cannot_grant(self):
        with patch.object(tool_permissions.ControllerAuthorityService,'verify',return_value=False):
            with self.assertRaises(PermissionError):self.call('allow')
        self.assertEqual(self.call()['permission']['mode'],'BLOCKED')
    def test_other_operations_untouched(self):
        with self.factory() as db:
            db.add(ActionAuthority(subject_identity_id=self.agent,allowed_operations=['other.operation'],granted_by=self.human,status=ActionAuthorityStatus.ACTIVE));db.commit()
        self.call('allow');self.call('block')
        with self.factory() as db:
            other=db.query(ActionAuthority).filter(ActionAuthority.allowed_operations==['other.operation']).one();self.assertEqual(other.status,ActionAuthorityStatus.ACTIVE)

if __name__=='__main__':unittest.main()
