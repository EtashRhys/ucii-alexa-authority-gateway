"""Dedicated local protected sandbox process. No grant or deployment capability."""
import base64
import json
import os
from pathlib import Path
import socket
import urllib.request
from uuid import UUID

from sandbox_executor import execute, status, SandboxDenied
from executor_evidence import EvidenceVerifier

SOCKET='/run/ucii-alexa-executor/executor.sock'
ARTIFACT='/etc/ucii-alexa-executor/artifact.json'
RECEIPTS='/var/lib/ucii-alexa-executor'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None


def verify_human(token):
    if not isinstance(token,str) or not token or len(token)>8192:
        raise PermissionError('HUMAN session required')
    request=urllib.request.Request('http://127.0.0.1:8000/v1/auth/session',headers={'Authorization':'Bearer '+token})
    with urllib.request.build_opener(NoRedirect).open(request,timeout=10) as response:
        raw=response.read(16385)
        if response.status!=200 or len(raw)>16384:raise PermissionError('Invalid HUMAN response')
    if json.loads(raw).get('identity_id')!=os.environ['UCII_ALEXA_HUMAN_ID']:
        raise PermissionError('HUMAN identity mismatch')


def sign(message):
    request={'version':'ucii-local-signer-v1','operation':'sign',
        'credential_id':os.environ['UCII_ALEXA_AGENT_CREDENTIAL_ID'],
        'algorithm':'ML-DSA-65','purpose':'operational_sign',
        'message_b64':base64.b64encode(message).decode('ascii')}
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
        client.settimeout(10);client.connect('/run/ucii-alexa-signer/signer.sock')
        client.sendall((json.dumps(request)+'\n').encode())
        raw=receive(client,65536)
    result=json.loads(raw)
    if result.get('status')!='signed':raise SandboxDenied('Signer unavailable')
    return base64.b64decode(result['signature_b64'],validate=True)


def receive(client,limit=16384):
    raw=b''
    while b'\n' not in raw:
        chunk=client.recv(4096)
        if not chunk:raise ValueError('Incomplete local request')
        raw+=chunk
        if len(raw)>limit:raise ValueError('Local request exceeded limit')
    line,_,rest=raw.partition(b'\n')
    if rest.strip():raise ValueError('Only one local request allowed')
    return line


def handle(request,session_factory):
    if isinstance(request,dict) and request.get('version')=='ucii-alexa-activity-v1':
        if set(request)!={'version','human_token'}:raise ValueError('Invalid activity request')
        verify_human(request['human_token'])
        from activity import read
        with session_factory() as db:
            return {'status':'checked','activity':read(db,agent=os.environ['UCII_ALEXA_AGENT_ID'],receipts=RECEIPTS)}
    if isinstance(request,dict) and request.get('version')=='ucii-alexa-conversation-tool-v1':
        from conversation_tool import run
        agent=os.environ['UCII_ALEXA_AGENT_ID']
        verifier=EvidenceVerifier(human_token=None,verify_human=lambda token:None,
            sign=sign,identity_id=agent,fingerprint=os.environ['UCII_ALEXA_AGENT_FINGERPRINT'])
        # Invocation uses the agent's saved permission. HUMAN authentication is
        # required to change that permission, not to request this fixed check.
        return {'status':'checked','tool_result':run(request,agent=agent,verify=verifier,
            artifact=ARTIFACT,receipts=RECEIPTS)}
    if (not isinstance(request,dict) or set(request)!= {'version','command','approval_id','action_digest','human_token'}
            or request['version']!='ucii-alexa-executor-v1'
            or request['command'] not in {'execute','status'}
            or str(UUID(request['approval_id']))!=request['approval_id']):
        raise ValueError('Invalid executor request')
    verify_human(request['human_token'])
    from pq_auth.authorization.exact_action import ExactActionApproval
    human,agent=os.environ['UCII_ALEXA_HUMAN_ID'],os.environ['UCII_ALEXA_AGENT_ID']
    with session_factory() as db:
        row=db.get(ExactActionApproval,request['approval_id'])
        if (row is None or row.product_id!='ucii-alexa' or row.human_identity_id!=human
                or row.subject_identity_id!=agent or row.action_digest!=request['action_digest']):
            raise SandboxDenied('Exact approval binding mismatch')
        if request['command']=='status':
            return {'status':'checked','execution':status(db,approval_id=row.id,
                human_identity_id=human,subject_identity_id=agent,receipt_directory=RECEIPTS)}
        verifier=EvidenceVerifier(human_token=request['human_token'],verify_human=verify_human,
            sign=sign,identity_id=agent,fingerprint=os.environ['UCII_ALEXA_AGENT_FINGERPRINT'])
        receipt=execute(db,approval_id=row.id,human_identity_id=human,
            subject_identity_id=agent,action_json=row.action_json,action_digest=row.action_digest,
            artifact_path=ARTIFACT,receipt_directory=RECEIPTS,verify_current_evidence=verifier)
        return {'status':'completed','receipt':receipt}


def main():
    # Import UCII models only inside the configured production runtime.
    from pq_auth.auth import models as _auth_models
    from pq_auth.config import SessionLocal
    for name in ('UCII_ALEXA_HUMAN_ID','UCII_ALEXA_AGENT_ID','UCII_ALEXA_AGENT_CREDENTIAL_ID'):
        value=os.environ[name]
        if str(UUID(value))!=value:raise RuntimeError('Invalid executor configuration')
    # Artifact is fixed, root-controlled and not writable by this process.
    details=Path(ARTIFACT).lstat()
    import stat
    if not stat.S_ISREG(details.st_mode) or details.st_uid!=0 or details.st_mode & 0o022:
        raise RuntimeError('Protected artifact unavailable')
    path=Path(SOCKET)
    if path.exists():
        if not path.is_socket() or path.stat().st_uid!=os.getuid():
            raise RuntimeError('Unexpected socket path')
        path.unlink()
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as server:
        server.bind(SOCKET);os.chmod(SOCKET,0o660);server.listen(8)
        print('Alexa sandbox executor socket ready',flush=True)
        while True:
            client,_=server.accept()
            with client:
                client.settimeout(15)
                try:
                    result=handle(json.loads(receive(client)),SessionLocal)
                except (PermissionError,SandboxDenied,ValueError,KeyError,TypeError):
                    result={'status':'denied','reason':'Protected session, exact approval or current authority unavailable'}
                except Exception:
                    result={'status':'uncertain','reason':'Retrieve protected execution status before any retry'}
                try:client.sendall((json.dumps(result)+'\n').encode())
                except OSError:pass

if __name__=='__main__':main()
