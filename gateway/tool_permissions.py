"""Fixed-tool HUMAN permission management inside protected controller custody.

Configured HUMAN ownership + current session + controller possession establish
this narrow policy-change authority. No terminal issuance permit is required for
this harmless fixed sandbox tool. Generic/advanced grants keep existing gates.
"""
from datetime import datetime, timezone
import os
from pq_auth.authorization.models import ActionAuthority, ActionAuthorityStatus
from pq_auth.authorization.service import ActionAuthorityService
from pq_auth.identity.controller_authority import ControllerAuthorityService

OPERATION='sandbox.artifact.verify'


def handle(daemon,request):
    if (not isinstance(request,dict) or set(request)!= {'version','operation','command','confirmation','human_token'}
            or request['version']!='ucii-alexa-tool-permission-v1'
            or request['operation']!=OPERATION or request['command'] not in {'get','allow','block'}
            or request['confirmation']!=('' if request['command']=='get' else 'CONFIRM_TOOL_PERMISSION')):
        raise ValueError('Invalid fixed-tool permission request')
    daemon.verify_human(request['human_token'])
    human=os.environ['UCII_ALEXA_HUMAN_ID']
    with daemon._session_factory() as db:
        if not ControllerAuthorityService.verify(db,identity_id=daemon.identity_id,presented_secret=daemon._credential.controller_authority):
            raise PermissionError('Controller possession unavailable')
        rows=db.query(ActionAuthority).filter(ActionAuthority.subject_identity_id==daemon.identity_id).all()
        scoped=[row for row in rows if OPERATION in row.allowed_operations]
        now=datetime.now(timezone.utc).replace(tzinfo=None)
        active=[row for row in scoped if row.status==ActionAuthorityStatus.ACTIVE and (row.expires_at is None or row.expires_at>now)]
        # Never revoke a broad record to implement a narrow tool toggle.
        if any(row.allowed_operations!=[OPERATION] for row in scoped if row.status==ActionAuthorityStatus.ACTIVE):
            raise ValueError('Mixed authority scope requires advanced review')
        if request['command']=='allow' and not active:
            # Retire expired ACTIVE rows because core refuses overlapping ACTIVE grants.
            for row in scoped:
                if row.status==ActionAuthorityStatus.ACTIVE:
                    ActionAuthorityService.revoke(db,row,reason='expired_tool_permission_replaced')
            row=ActionAuthorityService.grant(db,subject_identity_id=daemon.identity_id,allowed_operations=[OPERATION],granted_by=human)
            active=[row];scoped.append(row)
        elif request['command']=='block':
            for row in scoped:
                if row.status==ActionAuthorityStatus.ACTIVE:
                    ActionAuthorityService.revoke(db,row,reason='human_blocked_tool')
            active=[]
        latest=max(scoped,key=lambda row:row.revoked_at or row.granted_at,default=None)
        return {'status':'checked' if request['command']=='get' else 'saved',
            'permission':{'operation':OPERATION,'mode':'ALLOWED' if active else 'BLOCKED',
                'subject_identity_id':daemon.identity_id,
                'changed_by':(human if request['command']=='block' and scoped else latest.granted_by if latest else None),
                'changed_at':((latest.revoked_at or latest.granted_at).replace(tzinfo=timezone.utc).isoformat() if latest else None),
                'authority_id':active[0].id if active else None}}
