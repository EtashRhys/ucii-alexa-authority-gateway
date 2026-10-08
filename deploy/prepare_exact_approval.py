"""Owner authorizes one exact issuance; no approval or execution is performed."""
from datetime import datetime, timedelta, timezone
import grp
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from uuid import UUID, uuid4

if os.geteuid()!=0:
    raise SystemExit('Run as root.')
print('Saved proposal ID: ',end='',flush=True)
with open('/dev/tty','r') as terminal:
    proposal_id=terminal.readline().strip()
if str(UUID(proposal_id))!=proposal_id:
    raise SystemExit('Canonical proposal UUID required.')
with sqlite3.connect('file:/var/lib/ucii-alexa-gateway/proposals.sqlite3?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    row=db.execute('SELECT * FROM proposals WHERE proposal_id=?',(proposal_id,)).fetchone()
if not row or row['state']!='PROPOSED':
    raise SystemExit('A fresh PROPOSED draft is required; nothing changed.')
now=datetime.now(timezone.utc)
expires=datetime.fromtimestamp(row['expires_at'],timezone.utc)
if expires<=now:
    raise SystemExit('Proposal expired; save a fresh proposal.')
action=json.loads(row['action_json'])
digest='sha256:'+hashlib.sha256(row['action_json'].encode()).hexdigest()
if digest!=row['action_digest'] or row['human_identity_id']!='ebc28f40-8ea1-4820-8fcd-8af1d91cad2b' or action['subject_identity_id']!='f7592778-7e1c-41c7-b328-6a42b0c308e9':
    raise SystemExit('Proposal binding mismatch.')
print(json.dumps({'proposal_id':proposal_id,'action':action,'action_digest':digest},indent=2))
print('Type AUTHORIZE_EXACT_ISSUANCE to permit this exact approval once: ',end='',flush=True)
with open('/dev/tty','r') as terminal:
    confirmation=terminal.readline().strip()
if confirmation!='AUTHORIZE_EXACT_ISSUANCE':
    raise SystemExit('Nothing changed.')
root=Path('/etc/ucii-alexa-lifecycle')
if root.is_symlink() or not root.is_dir() or root.stat().st_uid!=0 or root.stat().st_mode & 0o022:
    raise SystemExit('Protected authorization directory unavailable.')
permit={'schema_version':'ucii-alexa-exact-approval-issuance-v1','authorization_id':str(uuid4()),'product_id':'ucii-alexa','proposal_id':proposal_id,'human_identity_id':row['human_identity_id'],'subject_identity_id':action['subject_identity_id'],'action_digest':digest,'authorized_at':now.isoformat(),'expires_at':min(now+timedelta(minutes=10),expires).isoformat(),'proposal_expires_at':expires.isoformat(),'max_uses':1}
path=root/(proposal_id+'.exact-approval.json')
fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o640)
with os.fdopen(fd,'w') as stream:
    os.fchown(stream.fileno(),0,grp.getgrnam('ucii-alexa-lifecycle-ipc').gr_gid)
    json.dump(permit,stream);stream.flush();os.fsync(stream.fileno())
print('PASS: exact issuance permit prepared. No approval issued; execution remains blocked.')
print('Now use Just this time on this saved proposal before',permit['expires_at'])
