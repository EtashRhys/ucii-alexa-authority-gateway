import sys
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gateway'))
import shopping_list
import executor_service

class ShoppingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.directory=Path(self.tmp.name);self.directory.chmod(0o700)
    def tearDown(self):self.tmp.cleanup()
    def request(self,command='add',item='milk',request_id=None):
        return {'version':'ucii-alexa-shopping-v1','command':command,'item':item,
                'request_id':request_id or str(uuid4()),'human_token':'owner'}
    def run_tool(self,request,verify=lambda action:True):
        return shopping_list.run(request,agent='agent',verify=verify,directory=self.directory)
    def test_saved_add_remove_and_read_when_blocked(self):
        self.assertEqual(self.run_tool(self.request())['items'],['milk'])
        self.assertEqual(self.run_tool(self.request('get',''),lambda a:False)['items'],['milk'])
        blocked=self.run_tool(self.request('remove'),lambda a:False)
        self.assertEqual(blocked['result'],'blocked');self.assertEqual(blocked['items'],['milk'])
        self.assertEqual(self.run_tool(self.request('remove'))['items'],[])
        self.assertEqual(len(shopping_list.activity(self.directory)),3)
    def test_replay_does_not_repeat_edit(self):
        request=self.request();first=self.run_tool(request)
        self.run_tool(self.request('remove'))
        again=self.run_tool(request)
        self.assertEqual(first['result'],again['result']);self.assertEqual(again['items'],[])
        with self.assertRaises(ValueError):self.run_tool({**request,'item':'eggs'})
    def test_permission_loss_before_commit(self):
        checks=iter([True,False])
        result=self.run_tool(self.request(),lambda a:next(checks))
        self.assertEqual(result['result'],'blocked');self.assertEqual(result['items'],[])
    def test_invalid_and_symlink_storage(self):
        for request in (self.request(item=''),self.request(item='x'*81),{**self.request(),'subject_identity_id':'other'}):
            with self.assertRaises(ValueError):self.run_tool(request)
        (self.directory/'shopping.sqlite3').symlink_to(self.directory/'other')
        with self.assertRaises(OSError):self.run_tool(self.request())
    def test_named_lists_isolate_items_and_block_creation(self):
        self.run_tool(self.request())
        created=self.run_tool({**self.request('create',''),'list_name':'Camping'})
        self.assertEqual(created['result'],'created');self.assertIn('Camping',created['lists'])
        self.assertEqual(created['items'],[])
        self.assertEqual(shopping_list.activity(self.directory)[0]['list_name'],'Camping')
        self.run_tool({**self.request(item='tent'),'list_name':'Camping'})
        self.assertEqual(self.run_tool(self.request('get',''))['items'],['milk'])
        self.assertEqual(self.run_tool({**self.request('get',''),'list_name':'camping'})['items'],['tent'])
        blocked=self.run_tool({**self.request('create',''),'list_name':'Travel'},lambda a:False)
        self.assertEqual(blocked['result'],'blocked');self.assertNotIn('Travel',blocked['lists'])
    def test_old_list_migrates_once_and_removed_items_stay_removed(self):
        import sqlite3
        path=self.directory/'shopping.sqlite3'
        db=sqlite3.connect(path)
        db.execute('CREATE TABLE items (name TEXT PRIMARY KEY)');db.execute("INSERT INTO items VALUES ('milk')")
        db.execute('CREATE TABLE events (id TEXT PRIMARY KEY,command TEXT,item TEXT,result TEXT,time TEXT)')
        db.commit();db.close();path.chmod(0o600)
        self.assertEqual(self.run_tool(self.request('get',''))['items'],['milk'])
        self.run_tool(self.request('remove'))
        self.assertEqual(self.run_tool(self.request('get',''))['items'],[])
    def test_request_binding_includes_list_name(self):
        request={**self.request('create',''),'list_name':'Camping'}
        self.run_tool(request)
        with self.assertRaises(ValueError):self.run_tool({**request,'list_name':'Groceries'})
        with self.assertRaises(ValueError):self.run_tool({**self.request('get',''),'list_name':'Missing'})

    def test_session_failure_before_storage_or_signing(self):
        with patch.object(executor_service,'verify_human',side_effect=PermissionError),patch.object(shopping_list,'run') as run:
            with self.assertRaises(PermissionError):executor_service.handle(self.request(),None)
            run.assert_not_called()

if __name__=='__main__':unittest.main()
