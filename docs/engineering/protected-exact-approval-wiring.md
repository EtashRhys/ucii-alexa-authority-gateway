# Protected exact approval wiring — 2026-10-08

The owner activated UCII exact_action_approvals at 90527da. The migration created only that table and saved a private online SQLite backup. No approval was issued by migration.

## Confirmation path

A saved, unexpired, owner-bound PROPOSED draft is required. POST /auth/approvals accepts only proposal_id, action_digest, and explicit APPROVE_EXACT_ACTION_ONCE confirmation. It derives HUMAN and agent identity from server configuration/session. The draft is atomically claimed as APPROVAL_PENDING before IPC; cancelled, expired, changed, or previously submitted drafts cannot be claimed. Cancellation is blocked while pending or approved. A future exact-approval revocation control is required before execution is enabled.

The protected Alexa lifecycle process independently verifies UCII HUMAN password session and current controller custody. Root-owned, non-writable exact issuance permits bind product, proposal UUID, HUMAN UUID, agent UUID, digest, and original proposal expiry. They are separate from consumed standing grant/revoke permits. The committed UCII approval record's unique issuance/proposal constraints durably consume this permit for one approval. Reconciliation returns the original record, never a new use or extended expiry.

Approval expires at the earliest of five minutes, issuance permit expiry, or proposal expiry. It covers the full canonical operation/resource/environment/artifact binding. No standing delegation is created or reactivated. Password authentication remains password authentication; no trusted-device or cryptographic HUMAN factor is claimed.

GET /auth/approvals independently retrieves UCII evidence. Uncertain POST outcomes require this check, not another POST. An authoritative NONE result releases a failed pending claim; an existing row marks the draft approved. The single-threaded protected daemon serializes issuance and reconciliation requests.

## Deployment and acceptance

Local: 31 gateway tests passed, including actual temporary SQLite issuance/duplicate reconciliation, changed-action denial, controller/session/permit denial, expiry, writable permit denial, cancellation/claim gating and no-session gating. Website TypeScript passed. Oracle tests and end-to-end exact approval acceptance are pending.

Run from gateway repo after pulling:

    PYTHONPATH=/opt/ucii/UCII/src /opt/ucii/UCII/.venv/bin/python -m unittest discover -s tests -v
    sudo python3 deploy/install_exact_approval.py

Installer backs up and validates nginx, installs the exact approvals route, and restarts only Alexa gateway/lifecycle services. Sign in again. Save a fresh proposal. Run sudo python3 deploy/prepare_exact_approval.py, paste its saved proposal UUID and explicitly confirm the displayed action. Then use Just this time and Check exact approval.

The earlier cancelled test proposal stays cancelled. The gateway/server.py hash used earlier is a test binding fixture, not a deployable application artifact. No executor or Alexa+ conversation is enabled. Every response continues execution_allowed=false.

Remaining before execution: exact approval revocation, fresh credential/evidence checks, authoritative execution-time reservation, artifact/resource enforcement, uncertain execution reconciliation and immutable receipt. Broader device step-up and actual Alexa+ transport remain separate integration work.


## Revocation update

DELETE /auth/approvals requires explicit REVOKE_EXACT_APPROVAL, current HUMAN session, proposal ID and matching digest. Protected custody independently verifies HUMAN/controller and selects the owner/product/agent/proposal-bound UCII row. It revokes only ACTIVE, unused, unexpired approval; expired or RESERVED records remain unchanged. No root issuance permit is needed for removal of an existing owner-bound approval. A repeated revoked result does not mutate or restore authority. Draft state becomes APPROVAL_REVOKED. Website offers Revoke exact approval only with retrieved, unexpired ACTIVE evidence. Status now derives EXPIRED on the server without altering retained ACTIVE rows; reservation enforces the stored expiry independently.

Owner live issuance and expiry accepted for 9ca0fb94-4db5-4b55-8956-f2faece26dcf. Local 34 tests pass; live revocation acceptance pending. Installer readiness now sends required proposal UUID and expects 401. Execution stays disabled.
