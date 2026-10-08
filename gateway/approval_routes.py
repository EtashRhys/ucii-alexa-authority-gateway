"""Authenticated exact-proposal confirmation adapter; no execution endpoint."""
import asyncio
from datetime import datetime, timezone
import json
import os
from uuid import UUID

from proposals import ProposalStore


def install(mcp, with_session, exchange, reply):
    @mcp.custom_route('/auth/approvals', methods=['POST', 'GET'])
    async def approval(request):
        try:
            if request.method == 'POST':
                raw = await request.body()
                if len(raw) > 4096:
                    raise ValueError()
                body = json.loads(raw)
                if not isinstance(body, dict) or set(body) != {'proposal_id','action_digest','confirmation'} or body['confirmation'] != 'APPROVE_EXACT_ACTION_ONCE':
                    raise ValueError()
                proposal_id = body['proposal_id']
            else:
                proposal_id = request.query_params.get('proposal_id','')
                body = None
            if str(UUID(proposal_id)) != proposal_id:
                raise ValueError()
        except (ValueError, TypeError, KeyError):
            return reply({'message':'Review and confirm one saved exact proposal.'},400)

        def operation(token, human):
            store = ProposalStore(os.environ.get('UCII_ALEXA_PROPOSALS_PATH','/var/lib/ucii-alexa-gateway/proposals.sqlite3'))
            with store.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                row = db.execute('SELECT * FROM proposals WHERE proposal_id=? AND human_identity_id=?',(proposal_id,human)).fetchone()
                if not row:
                    raise LookupError()
                snapshot = store.public(row, datetime.now(timezone.utc).timestamp())
                intent = {'version':'ucii-alexa-exact-approval-v1','operation':'exact_approval_status', 'proposal_id':proposal_id,'human_token':token}
                if body:
                    if snapshot['state'] != 'PROPOSED' or snapshot['action_digest'] != body['action_digest']:
                        raise ValueError('Proposal changed, expired, cancelled or already submitted')
                    # Commit the claim before IPC. Cancellation is disallowed once
                    # claimed; uncertain responses require status reconciliation.
                    db.execute("UPDATE proposals SET state='APPROVAL_PENDING' WHERE proposal_id=?",(proposal_id,))
                    db.commit()
                    intent.update(operation='approve_exact_action',action_json=row['action_json'], action_digest=row['action_digest'],proposal_expires_at=snapshot['expires_at'])
            result = exchange(intent)
            if result.get('status') not in ('checked','approved'):
                return {'message':'Approval outcome unconfirmed. Use Check exact approval; do not resubmit.'},503
            evidence = result.get('approval')
            if evidence:
                if (evidence.get('proposal_id') != proposal_id or evidence.get('action_digest') != snapshot['action_digest'] or evidence.get('human_identity_id') != human or evidence.get('subject_identity_id') != os.environ['UCII_ALEXA_AGENT_ID'] or evidence.get('execution_allowed') is not False):
                    raise ValueError('Approval response binding mismatch')
                with store.connect() as db:
                    db.execute("UPDATE proposals SET state='APPROVED' WHERE proposal_id=? AND state='APPROVAL_PENDING'",(proposal_id,))
            elif not body:
                # Status NONE is authoritative, so the failed claim can be released.
                with store.connect() as db:
                    db.execute("UPDATE proposals SET state='PROPOSED' WHERE proposal_id=? AND state='APPROVAL_PENDING'",(proposal_id,))
            return {'approval': evidence, 'execution_allowed':False},200
        try:
            data,status = await with_session(request, operation)
            return reply(data,status)
        except PermissionError:
            return reply({'message':'An active UCII HUMAN session is required.'},401)
        except LookupError:
            return reply({'message':'Proposal not found.'},404)
        except ValueError:
            return reply({'message':'Retrieve the current proposal and check exact approval before continuing.'},409)
        except Exception:
            return reply({'message':'Approval outcome unconfirmed. Check exact approval before retrying.'},503)
