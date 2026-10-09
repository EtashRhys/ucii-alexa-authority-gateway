"""Owner-only projection of protected receipts and UCII permission history."""
import json
import os
from pathlib import Path
import stat
from datetime import timezone
from pq_auth.authorization.models import ActionAuthority

def read(db, *, agent, receipts):
    events=[]
    for path in sorted(Path(receipts).glob('tool-*.json'),key=lambda p:p.name):
        try:
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
            with os.fdopen(fd,'rb') as stream:
                details=os.fstat(stream.fileno())
                if not stat.S_ISREG(details.st_mode) or details.st_size>16384:continue
                row=json.loads(stream.read(16385))
            if (row.get('subject_identity_id')!=agent or row.get('operation')!='sandbox.artifact.verify'
                    or row.get('status') not in {'completed','blocked'} or row.get('deployed') is not False):continue
            events.append({'id':row['request_id'],'kind':'tool','time':row['checked_at'],
                'operation':row['operation'],'result':'blocked' if row['status']=='blocked' else 'matched' if row['artifact_matches'] else 'mismatch'})
        except (OSError,ValueError,KeyError,TypeError):continue
    for row in db.query(ActionAuthority).filter(ActionAuthority.subject_identity_id==agent).all():
        if row.allowed_operations!=['sandbox.artifact.verify']:continue
        events.append({'id':row.id+':allow','kind':'permission','time':row.granted_at.replace(tzinfo=timezone.utc).isoformat(),'operation':'sandbox.artifact.verify','result':'allowed'})
        if row.revoked_at:
            events.append({'id':row.id+':block','kind':'permission','time':row.revoked_at.replace(tzinfo=timezone.utc).isoformat(),'operation':'sandbox.artifact.verify','result':'blocked'})
    return sorted(events,key=lambda event:event['time'],reverse=True)[:50]
