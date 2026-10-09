import io
import json
import os
from pathlib import Path
import socket
import sys
import unittest
from uuid import uuid4
from unittest.mock import patch, Mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gateway'))
import executor_service as service

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.request={'version':'ucii-alexa-executor-v1','command':'execute','approval_id':str(uuid4()),'action_digest':'sha256:'+'a'*64,'human_token':'test-only'}
    def test_unauthenticated_request_never_opens_database(self):
        self.request['human_token']='';factory=Mock()
        with self.assertRaises(PermissionError):service.handle(self.request,factory)
        factory.assert_not_called()
    def test_paths_and_subject_cannot_be_supplied(self):
        for field in ('artifact_path','subject_identity_id','receipt_directory'):
            with self.assertRaises(ValueError):service.handle({**self.request,field:'bad'},Mock())
    def test_wrong_human_is_rejected_before_database(self):
        with patch.dict(os.environ,UCII_ALEXA_HUMAN_ID=str(uuid4())),patch.object(service.urllib.request,'build_opener') as opener:
            response=Mock();response.status=200;response.read.return_value=json.dumps({'identity_id':str(uuid4())}).encode()
            opener.return_value.open.return_value.__enter__=Mock(return_value=response)
            opener.return_value.open.return_value.__exit__=Mock(return_value=False)
            factory=Mock()
            with self.assertRaises(PermissionError):service.handle(self.request,factory)
            factory.assert_not_called()
    def test_bounded_socket_receive_and_empty_client(self):
        client=Mock();client.recv.side_effect=[b'{}\n']
        self.assertEqual(service.receive(client),b'{}')
        for chunks in ([b''],[b'a'*32],[b'{}\n{}\n']):
            client=Mock();client.recv.side_effect=chunks
            with self.assertRaises(ValueError):service.receive(client,16)

if __name__=='__main__':unittest.main()
