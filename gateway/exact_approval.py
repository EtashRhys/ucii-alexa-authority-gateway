"""Protected exact approval issuance. This module never executes actions."""
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import stat
from uuid import UUID

from pq_auth.authorization.exact_action import ExactActionApproval, ExactActionApprovalService, validate_binding
from pq_auth.identity.controller_authority import ControllerAuthorityService

PRODUCT = 'ucii-alexa'
SCHEMA = 'ucii-alexa-exact-approval-issuance-v1'


def public(row):
    return {'approval_id': row.id, 'proposal_id': row.proposal_id,
            'action_digest': row.action_digest, 'state': row.state,
            'expires_at': row.expires_at.replace(tzinfo=timezone.utc).isoformat(),
            'human_identity_id': row.human_identity_id,
            'subject_identity_id': row.subject_identity_id,
            'execution_allowed': False}


def handle(daemon, request, *, permit_directory=Path('/etc/ucii-alexa-lifecycle'), now=None):
    """Called only inside the protected controller custody process."""
    current = datetime.now(timezone.utc) if now is None else now
    if set(request) not in (
        {'version', 'operation', 'proposal_id', 'human_token'},
        {'version', 'operation', 'proposal_id', 'human_token', 'action_json', 'action_digest', 'proposal_expires_at'},
    ) or request['version'] != 'ucii-alexa-exact-approval-v1':
        raise ValueError('Invalid exact approval request')
    proposal_id = request['proposal_id']
    if str(UUID(proposal_id)) != proposal_id:
        raise ValueError('Invalid proposal reference')
    human = os.environ['UCII_ALEXA_HUMAN_ID']
    daemon.verify_human(request['human_token'])
    db = daemon._session_factory()
    try:
        if not ControllerAuthorityService.verify(db, identity_id=daemon.identity_id,
                presented_secret=daemon._credential.controller_authority):
            raise ValueError('Controller possession unavailable')
        row = db.query(ExactActionApproval).filter_by(product_id=PRODUCT,
            proposal_id=proposal_id, human_identity_id=human,
            subject_identity_id=daemon.identity_id).first()
        if request['operation'] == 'exact_approval_status':
            if set(request) != {'version', 'operation', 'proposal_id', 'human_token'}:
                raise ValueError('Invalid status request')
            return {'status': 'checked', 'approval': public(row) if row else None}
        if request['operation'] != 'approve_exact_action' or 'action_json' not in request:
            raise ValueError('Unsupported exact operation')
        action = validate_binding(request['action_json'], request['action_digest'], daemon.identity_id)
        if action['version'] != 'ucii-alexa-action-v1':
            raise ValueError('Unsupported canonical action')
        if row:
            # Reconciliation only: never create a second use or extend expiry.
            if row.action_json != request['action_json'] or row.action_digest != request['action_digest']:
                raise ValueError('Existing approval binding mismatch')
            return {'status': 'approved', 'approval': public(row)}
        path = permit_directory / (proposal_id + '.exact-approval.json')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            details = os.fstat(fd)
            if not stat.S_ISREG(details.st_mode) or details.st_uid != 0 or details.st_mode & 0o022 or details.st_size > 8192:
                raise ValueError('Root-controlled exact permit required')
            with os.fdopen(fd, 'r') as stream:
                fd = None
                permit = json.load(stream)
        finally:
            if fd is not None:
                os.close(fd)
        fields = {'schema_version','authorization_id','product_id','proposal_id',
                  'human_identity_id','subject_identity_id','action_digest',
                  'authorized_at','expires_at','proposal_expires_at','max_uses'}
        if not isinstance(permit, dict) or set(permit) != fields:
            raise ValueError('Invalid permit contract')
        if (permit['schema_version'] != SCHEMA or permit['product_id'] != PRODUCT
            or permit['proposal_id'] != proposal_id or permit['human_identity_id'] != human
            or permit['subject_identity_id'] != daemon.identity_id
            or permit['action_digest'] != request['action_digest']
            or permit['proposal_expires_at'] != request['proposal_expires_at']
            or type(permit['max_uses']) is not int or permit['max_uses'] != 1):
            raise ValueError('Exact permit binding mismatch')
        def timestamp(value):
            parsed = datetime.fromisoformat(value.replace('Z','+00:00'))
            if parsed.tzinfo is None:
                raise ValueError('Timezone required')
            return parsed.astimezone(timezone.utc)
        start, end, proposal_end = map(timestamp, (permit['authorized_at'],permit['expires_at'],permit['proposal_expires_at']))
        if not start <= current < end or current >= proposal_end:
            raise ValueError('Permit or proposal expired')
        # Unique issuance_authorization_id and product/proposal constraints make
        # this committed UCII record the durable one-use issuance consumption.
        row = ExactActionApprovalService.issue(db, product_id=PRODUCT, proposal_id=proposal_id,
            subject_identity_id=daemon.identity_id, human_identity_id=human,
            action_json=request['action_json'], action_digest=request['action_digest'],
            issuance_authorization_id=permit['authorization_id'],
            now=current.replace(tzinfo=None),
            expires_at=min(current+timedelta(minutes=5), end, proposal_end).replace(tzinfo=None))
        return {'status': 'approved', 'approval': public(row)}
    finally:
        db.close()
