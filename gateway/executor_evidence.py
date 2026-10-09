"""Independent evidence checks for a protected sandbox composition.

No routes, grants or effects. The protected process supplies its own signer and
HUMAN verifier; callers cannot provide browser proof flags or arbitrary URLs.
"""
import base64
from datetime import datetime, timezone
import hashlib
import json
import re
import secrets
import urllib.request
from uuid import UUID


class EvidenceVerifier:
    def __init__(self, *, human_token, verify_human, sign, identity_id, fingerprint):
        self.human_token = human_token
        self.verify_human = verify_human
        self.sign = sign
        if str(UUID(identity_id)) != identity_id or not re.fullmatch('[0-9a-f]{64}', fingerprint):
            raise ValueError('Protected agent binding is invalid')
        self.identity_id, self.fingerprint = identity_id, fingerprint

    def __call__(self, action):
        # Independent HUMAN session resolution occurs on each effect-boundary check.
        self.verify_human(self.human_token)
        if action.get('subject_identity_id') != self.identity_id:
            return False
        canonical = json.dumps(action, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        message = json.dumps({
            'purpose':'ucii-alexa-sandbox-effect-check-v1',
            'identity_id':self.identity_id, 'operation':action['operation'],
            'action_digest':'sha256:'+hashlib.sha256(canonical.encode()).hexdigest(),
            'nonce':secrets.token_urlsafe(32),
            'issued_at':datetime.now(timezone.utc).isoformat(),
        },sort_keys=True,separators=(',', ':'))
        signature = base64.b64encode(self.sign(message.encode())).decode('ascii')
        request = urllib.request.Request('http://127.0.0.1:8000/v1/authorization/delegated/check',
            data=json.dumps({'identity_id':self.identity_id,
                'credential_fingerprint':self.fingerprint,'operation':action['operation'],
                'message':message,'signature':signature}).encode(),
            headers={'Content-Type':'application/json'}, method='POST')
        # Redirects are rejected: the token/proof boundary is local and fixed.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        with urllib.request.build_opener(NoRedirect).open(request, timeout=10) as response:
            if response.status != 200:
                return False
            raw = response.read(16385)
        if len(raw) > 16384:
            raise ValueError('UCII evidence response exceeded limit')
        result = json.loads(raw)
        if not isinstance(result, dict):
            return False
        authority_id = result.get('authority_id')
        return (result.get('identity_id') == self.identity_id
            and result.get('credential_fingerprint') == self.fingerprint
            and result.get('operation') == action['operation']
            and result.get('credential_status') == 'ACTIVE'
            and result.get('authority_state') == 'ACTIVE'
            and result.get('authorized') is True
            and result.get('executed') is False
            and isinstance(authority_id,str) and str(UUID(authority_id)) == authority_id)
