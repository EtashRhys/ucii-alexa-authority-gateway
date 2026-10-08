"""Server-held action drafts. These records confer no approval or authority."""
import asyncio
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
from uuid import UUID, uuid4

from canonical_action import CanonicalAction
from starlette.responses import JSONResponse

LIFETIME_SECONDS = 900


class ProposalStore:
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.is_absolute():
            raise ValueError("Proposal database must be an absolute path")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute('''CREATE TABLE IF NOT EXISTS proposals (
            proposal_id TEXT PRIMARY KEY, human_identity_id TEXT NOT NULL,
            idempotency_key TEXT NOT NULL, action_json TEXT NOT NULL,
            action_digest TEXT NOT NULL, created_at REAL NOT NULL,
            expires_at REAL NOT NULL, state TEXT NOT NULL,
            UNIQUE(human_identity_id, idempotency_key))''')
        db.commit()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def create(self, action, *, human_identity_id, idempotency_key, now=None):
        if str(UUID(idempotency_key)) != idempotency_key:
            raise ValueError("A canonical idempotency UUID is required")
        now = time.time() if now is None else now
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM proposals WHERE human_identity_id=? AND idempotency_key=?", (human_identity_id, idempotency_key)).fetchone()
            if row:
                if row['action_json'] != action.canonical_message():
                    raise FileExistsError("Idempotency key is already bound to another action")
                return self.public(row, now)
            # Bound private draft history; no approval/provenance is deleted here.
            db.execute("DELETE FROM proposals WHERE expires_at < ?", (now - 86400,))
            count = db.execute("SELECT COUNT(*) FROM proposals WHERE human_identity_id=? AND expires_at>? AND state='PROPOSED'", (human_identity_id, now)).fetchone()[0]
            if count >= 64:
                raise OverflowError("Too many pending proposals")
            proposal_id = str(uuid4())
            db.execute("INSERT INTO proposals VALUES (?,?,?,?,?,?,?,?)", (proposal_id, human_identity_id, idempotency_key, action.canonical_message(), action.digest(), now, now + LIFETIME_SECONDS, 'PROPOSED'))
            row = db.execute("SELECT * FROM proposals WHERE proposal_id=?", (proposal_id,)).fetchone()
            return self.public(row, now)

    def get(self, proposal_id, *, human_identity_id, cancel=False, now=None):
        if str(UUID(proposal_id)) != proposal_id:
            raise ValueError("A canonical proposal UUID is required")
        now = time.time() if now is None else now
        with self.connect() as db:
            if cancel:
                db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM proposals WHERE proposal_id=? AND human_identity_id=?", (proposal_id, human_identity_id)).fetchone()
            if row is None:
                raise LookupError("Proposal not found")
            if cancel and row['state'] == 'PROPOSED' and row['expires_at'] > now:
                db.execute("UPDATE proposals SET state='CANCELLED' WHERE proposal_id=?", (proposal_id,))
                row = db.execute("SELECT * FROM proposals WHERE proposal_id=?", (proposal_id,)).fetchone()
            return self.public(row, now)

    @staticmethod
    def public(row, now):
        message = row['action_json']
        digest = 'sha256:' + hashlib.sha256(message.encode('utf-8')).hexdigest()
        if digest != row['action_digest']:
            raise ValueError("Stored proposal integrity mismatch")
        return {
            'proposal_id': row['proposal_id'], 'action': json.loads(message),
            'action_digest': digest,
            'created_at': datetime.fromtimestamp(row['created_at'], timezone.utc).isoformat(),
            'expires_at': datetime.fromtimestamp(row['expires_at'], timezone.utc).isoformat(),
            'state': 'EXPIRED' if row['expires_at'] <= now and row['state'] == 'PROPOSED' else row['state'],
            'approval': 'NOT_ESTABLISHED', 'execution_allowed': False,
        }


def install_proposal_routes(mcp, authenticated_human):
    @mcp.custom_route('/auth/proposals', methods=['POST', 'GET', 'DELETE'])
    async def proposals(request):
        headers = {'Cache-Control': 'no-store'}
        def reply(data, status=200):
            return JSONResponse(data, status_code=status, headers=headers)
        try:
            human_id = await authenticated_human(request)
        except Exception:
            return reply({'message': 'An active UCII HUMAN session is required.'}, 401)
        try:
            path = os.environ.get('UCII_ALEXA_PROPOSALS_PATH', '/var/lib/ucii-alexa-gateway/proposals.sqlite3')
            store = ProposalStore(path)
            if request.method == 'GET':
                result = await asyncio.to_thread(store.get, request.query_params.get('proposal_id', ''), human_identity_id=human_id)
            else:
                if request.headers.get('content-type', '').split(';')[0].strip() != 'application/json':
                    return reply({'message': 'JSON required.'}, 415)
                raw = await request.body()
                if len(raw) > 8192:
                    return reply({'message': 'Proposal request too large.'}, 413)
                body = json.loads(raw)
                if not isinstance(body, dict):
                    raise ValueError()
                if request.method == 'DELETE':
                    if set(body) != {'proposal_id'}:
                        raise ValueError()
                    result = await asyncio.to_thread(store.get, body['proposal_id'], human_identity_id=human_id, cancel=True)
                else:
                    if set(body) != {'action', 'idempotency_key'}:
                        raise ValueError()
                    action = CanonicalAction.from_proposal(body['action'], subject_identity_id=os.environ['UCII_ALEXA_AGENT_ID'])
                    result = await asyncio.to_thread(store.create, action, human_identity_id=human_id, idempotency_key=body['idempotency_key'])
            return reply({'proposal': result})
        except FileExistsError:
            return reply({'message': 'This request key belongs to a different action.'}, 409)
        except OverflowError:
            return reply({'message': 'Too many pending proposals. Cancel an unused proposal.'}, 429)
        except LookupError:
            return reply({'message': 'Proposal not found.'}, 404)
        except (ValueError, TypeError):
            return reply({'message': 'Supply an exact action, environment and deployment artifact digest.'}, 400)
        except Exception:
            return reply({'message': 'Proposal storage unavailable. No approval or execution occurred.'}, 503)
