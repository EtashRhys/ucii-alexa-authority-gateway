"""One fixed read-only tool, gated by current UCII agent permission."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
from uuid import UUID

OPERATION = 'sandbox.artifact.verify'
EXPECTED = b'{"product":"ucii-alexa","resource":"test-app","environment":"staging","purpose":"sandbox-artifact-verification","version":1}\n'

def run(request, *, agent, verify, artifact, receipts):
    if (not isinstance(request, dict) or set(request) != {'version', 'request_id'}
            or request['version'] != 'ucii-alexa-conversation-tool-v1'
            or str(UUID(request['request_id'])) != request['request_id']):
        raise ValueError('Invalid fixed tool request')
    action = {'version':'ucii-alexa-action-v1', 'operation':OPERATION,
        'resource':'test-app', 'environment':'staging', 'subject_identity_id':agent,
        'artifact_digest':'sha256:' + hashlib.sha256(EXPECTED).hexdigest()}
    allowed = verify(action) is True
    matched = False
    if allowed:
        fd = os.open(artifact, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as stream:
            details = os.fstat(stream.fileno())
            if (not stat.S_ISREG(details.st_mode) or details.st_uid != 0
                    or details.st_mode & 0o022 or details.st_size > 65536):
                raise ValueError('Protected artifact unavailable')
            matched = stream.read(65537) == EXPECTED
        # Recheck current permission immediately before recording the result.
        allowed = verify(action) is True
    result = {'request_id':request['request_id'], 'operation':OPERATION,
        'subject_identity_id':agent, 'resource':'test-app', 'environment':'staging',
        'status':'completed' if allowed else 'blocked',
        'artifact_matches':matched if allowed else None,
        'artifact_digest':action['artifact_digest'],
        'checked_at':datetime.now(timezone.utc).isoformat(), 'deployed':False}
    directory = Path(receipts)
    details = directory.lstat()
    if (not stat.S_ISDIR(details.st_mode) or details.st_uid != os.getuid()
            or details.st_mode & 0o077):
        raise ValueError('Private receipt directory required')
    fd = os.open(directory / ('tool-' + request['request_id'] + '.json'),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(result, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)
    return result
