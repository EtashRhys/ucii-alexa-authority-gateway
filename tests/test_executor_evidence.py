import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from uuid import uuid4

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gateway'))
from executor_evidence import EvidenceVerifier

class Response:
    status=200
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,size):return json.dumps(self.data).encode()[:size]

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.agent=str(uuid4());self.calls=[];self.messages=[]
        self.verifier=EvidenceVerifier(human_token='test',verify_human=lambda token:self.calls.append(token),sign=lambda message:self.messages.append(message) or b'signature',identity_id=self.agent,fingerprint='a'*64)
        self.action={'subject_identity_id':self.agent,'operation':'sandbox.artifact.verify','resource':'test-app','environment':'staging','artifact_digest':'sha256:'+'b'*64,'version':'ucii-alexa-action-v1'}
        self.result={'identity_id':self.agent,'credential_fingerprint':'a'*64,'operation':'sandbox.artifact.verify','credential_status':'ACTIVE','authority_state':'ACTIVE','authorized':True,'executed':False,'authority_id':str(uuid4())}
    def check(self):
        with patch('executor_evidence.urllib.request.build_opener') as opener:
            opener.return_value.open.return_value=Response(self.result)
            result=self.verifier(self.action)
            request=opener.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url,'http://127.0.0.1:8000/v1/authorization/delegated/check')
            self.assertNotIn('test',request.headers.values())
            return result
    def test_fresh_signed_checks_and_human_revalidation(self):
        self.assertTrue(self.check());self.assertTrue(self.check())
        self.assertEqual(self.calls,['test','test'])
        self.assertNotEqual(self.messages[0],self.messages[1])
        signed=json.loads(self.messages[0]);self.assertIn('action_digest',signed)
    def test_wrong_credential_operation_identity_or_revocation_denied(self):
        original=self.result.copy()
        for key,value in [('identity_id',str(uuid4())),('credential_fingerprint','c'*64),('operation','other'),('credential_status','REVOKED'),('authority_state','REVOKED'),('authorized',False),('executed',True),('authority_id',None)]:
            self.result={**original,key:value};self.assertFalse(self.check())
    def test_human_failure_prevents_signing_and_http(self):
        self.verifier.verify_human=lambda token:(_ for _ in ()).throw(PermissionError())
        with patch('executor_evidence.urllib.request.build_opener') as opener:
            with self.assertRaises(PermissionError):self.verifier(self.action)
            opener.assert_not_called()
        self.assertEqual(self.messages,[])
    def test_wrong_subject_never_signs(self):
        self.action['subject_identity_id']=str(uuid4())
        self.assertFalse(self.verifier(self.action));self.assertEqual(self.messages,[])

if __name__=='__main__':unittest.main()
