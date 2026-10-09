"""Trusted sandbox execution primitive; no HTTP/MCP route or production wiring.

The protected caller must independently authenticate the HUMAN and verify fresh
agent credential and exact-action authority in verify_current_evidence(). Never
supply that callback or artifact path from a browser/model request.
"""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import stat
from uuid import UUID, uuid4

from pq_auth.authorization.exact_action import ExactActionApproval, ExactActionApprovalService, validate_binding


class SandboxDenied(RuntimeError):
    pass


class SandboxUncertain(RuntimeError):
    """Reservation remains spent; reconcile the receipt, never retry effects."""


def _artifact(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        details = os.fstat(fd)
        if not stat.S_ISREG(details.st_mode) or details.st_size > 65536:
            raise SandboxDenied('Sandbox artifact must be a bounded regular file')
        with os.fdopen(fd, 'rb') as stream:
            fd = None
            content = stream.read(65537)
        if len(content) > 65536:
            raise SandboxDenied('Sandbox artifact too large')
        return 'sha256:' + hashlib.sha256(content).hexdigest()
    finally:
        if fd is not None:
            os.close(fd)


def execute(db, *, approval_id, human_identity_id, subject_identity_id,
            action_json, action_digest, artifact_path, receipt_directory,
            verify_current_evidence, clock=datetime.utcnow):
    """Verify a fixed artifact and create one sandbox receipt, never deploy.

    verify_current_evidence receives the validated action and must return exactly
    True only after independent current HUMAN/credential/authority verification.
    Called before reservation and immediately before the sole filesystem effect.
    The actual effect is receipt creation; infrastructure.deploy is unsupported.
    """
    action = validate_binding(action_json, action_digest, subject_identity_id)
    if (action['version'] != 'ucii-alexa-action-v1'
            or action['operation'] != 'sandbox.artifact.verify'
            or action['resource'] != 'test-app' or action['environment'] != 'staging'):
        raise SandboxDenied('Only sandbox.artifact.verify for staging test-app is supported')
    directory = Path(receipt_directory)
    details = directory.lstat()
    if not stat.S_ISDIR(details.st_mode) or details.st_mode & 0o077:
        raise SandboxDenied('A private protected receipt directory is required')
    if _artifact(artifact_path) != action['artifact_digest']:
        raise SandboxDenied('Artifact digest mismatch')
    row = db.get(ExactActionApproval, str(UUID(approval_id)))
    if row is None or row.proposal_id is None:
        raise SandboxDenied('Exact approval unavailable')
    if verify_current_evidence(action) is not True:
        raise SandboxDenied('Current protected evidence unavailable')
    reservation = ExactActionApprovalService.reserve(db, approval_id=approval_id,
        product_id='ucii-alexa', human_identity_id=human_identity_id,
        subject_identity_id=subject_identity_id, action_json=action_json,
        action_digest=action_digest, now=clock())
    if reservation is None:
        raise SandboxDenied('Exact approval invalid, expired, revoked or already used')
    try:
        db.refresh(row)
        if verify_current_evidence(action) is not True:
            raise SandboxUncertain('Evidence expired or changed after reservation')
        if _artifact(artifact_path) != action['artifact_digest']:
            raise SandboxUncertain('Artifact changed after reservation')
        # Network verification may take time; evaluate expiry after it returns.
        current = clock()
        if current >= row.expires_at:
            raise SandboxUncertain('Approval expired during evidence verification')
        receipt = {'version':'ucii-alexa-sandbox-receipt-v1',
            'receipt_id':str(uuid4()), 'approval_id':approval_id,
            'proposal_id':row.proposal_id, 'reservation_id':reservation,
            'human_identity_id':human_identity_id, 'subject_identity_id':subject_identity_id,
            'action_digest':action_digest, 'artifact_digest':action['artifact_digest'],
            'operation':action['operation'], 'resource':action['resource'],
            'environment':action['environment'], 'outcome':'ARTIFACT_VERIFIED',
            'deployment_performed':False, 'recorded_at':current.isoformat()+'Z'}
        # A reservation-named, exclusive receipt permits read-only reconciliation
        # after a lost response/commit. No effect is ever repeated automatically.
        path = directory / (reservation+'.json')
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as stream:
            json.dump(receipt, stream, sort_keys=True)
            stream.flush(); os.fsync(stream.fileno())
        directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try: os.fsync(directory_fd)
        finally: os.close(directory_fd)
        if not ExactActionApprovalService.consume(db, approval_id=approval_id,
                reservation_id=reservation, execution_receipt_id=receipt['receipt_id'], now=clock()):
            raise SandboxUncertain('Receipt written; consumption needs reconciliation')
        return receipt
    except Exception as error:
        # RESERVED is deliberately retained, including on partial filesystem failure.
        raise SandboxUncertain('Reserved sandbox outcome requires read-only reconciliation') from error


def status(db, *, approval_id, human_identity_id, subject_identity_id, receipt_directory):
    """Owner-bound read-only receipt retrieval; never replay or release a use.

    A valid receipt alongside RESERVED reports reconciliation required; this
    function never turns a filesystem observation into database consumption.
    The protected caller authenticates the HUMAN before calling this function.
    """
    row = db.get(ExactActionApproval, str(UUID(approval_id)))
    if (row is None or row.product_id != 'ucii-alexa'
            or row.human_identity_id != human_identity_id
            or row.subject_identity_id != subject_identity_id):
        raise SandboxDenied('Exact approval not found for this owner')
    result = {'approval_id':row.id,'proposal_id':row.proposal_id,
        'action_digest':row.action_digest,'state':row.state,
        'receipt':None,'reconciliation_required':row.state == 'RESERVED'}
    if row.reservation_id is None:
        return result
    directory = Path(receipt_directory)
    details = directory.lstat()
    if not stat.S_ISDIR(details.st_mode) or details.st_mode & 0o077:
        raise SandboxUncertain('Invalid receipt directory custody')
    path = directory / (str(UUID(row.reservation_id))+'.json')
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except FileNotFoundError:
        if row.state == 'CONSUMED':
            raise SandboxUncertain('Consumed approval receipt unavailable')
        return result
    try:
        details = os.fstat(fd)
        if not stat.S_ISREG(details.st_mode) or details.st_mode & 0o077 or details.st_size > 8192:
            raise SandboxUncertain('Invalid receipt custody')
        with os.fdopen(fd,'r') as stream:
            fd = None
            receipt = json.load(stream)
    finally:
        if fd is not None: os.close(fd)
    action = validate_binding(row.action_json,row.action_digest,row.subject_identity_id)
    expected = {'version':'ucii-alexa-sandbox-receipt-v1', 'approval_id':row.id,
        'proposal_id':row.proposal_id,'reservation_id':row.reservation_id,
        'human_identity_id':row.human_identity_id,'subject_identity_id':row.subject_identity_id,
        'action_digest':row.action_digest,'artifact_digest':action['artifact_digest'],
        'operation':action['operation'],'resource':action['resource'],
        'environment':action['environment'],'outcome':'ARTIFACT_VERIFIED',
        'deployment_performed':False}
    if (not isinstance(receipt,dict) or set(receipt) != set(expected)|{'receipt_id','recorded_at'}
            or any(receipt.get(k) != v for k,v in expected.items())
            or receipt.get('deployment_performed') is not False
            or str(UUID(receipt['receipt_id'])) != receipt['receipt_id']
            or (row.state == 'CONSUMED' and row.execution_receipt_id != receipt['receipt_id'])):
        raise SandboxUncertain('Receipt binding mismatch')
    result['receipt'] = receipt
    return result
