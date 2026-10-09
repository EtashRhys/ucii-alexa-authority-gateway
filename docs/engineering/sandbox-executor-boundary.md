# Sandbox executor boundary — 2026-10-09

## Live acceptance recorded
Owner confirmed proposal be12aa2a-29ad-4b6b-a1fe-e98b9e7ce05f changed from exact approval ACTIVE to REVOKED, then a fresh status retrieval remained REVOKED. Proposal state became APPROVAL_REVOKED. Execution stayed blocked. Preserve this record and the historical expired approval.

Oracle gateway acceptance at 3568429: 34 tests passed; exact approval installer completed with valid nginx configuration. Services restarted, requiring sign-in.

## Bounded execution primitive
gateway/sandbox_executor.py is trusted-side code with no route, daemon registration, installation, or website execution control. It supports only sandbox.artifact.verify on test-app in staging. It does not implement infrastructure.deploy. A new fixed sandbox artifact must be provisioned before live testing; the old server.py digest is not a deployment artifact.

The protected composition must supply fixed artifact/receipt paths and independently verify current HUMAN authentication, agent credential possession and exact-action authority. Its verify_current_evidence callback is a required integration seam, not implemented authentication. A model/browser must never supply that callback or paths. Production wiring is explicitly pending.

After checking the configured artifact digest and evidence, the primitive reserves an exactly matching UCII approval atomically. It rechecks expiry/evidence and artifact bytes before writing one exclusive, fsynced private receipt, then records consumption in UCII. Receipt outcome is ARTIFACT_VERIFIED with deployment_performed=false. Replays cannot repeat the filesystem effect.

Failures after reservation leave RESERVED unchanged. A lost database commit after receipt creation requires protected read-only reconciliation against the reservation-named receipt. No automatic release or retry is permitted. Receipt status/reconciliation adapter is still pending. The SQLite transition and filesystem write are separate durability boundaries, not an atomic cross-system transaction.

Seven new isolated temporary-SQLite tests cover receipt/single-use success, expired/revoked denial, absent evidence/artifact mismatch, evidence loss after reservation, altered target/real deployment rejection, a lost consumption commit with durable receipt, and artifact symlink refusal. Full local suite: 41 tests passed. Test callbacks stand in for external authentication only; no live executor acceptance is claimed.

## Next bounded changes
1. Compose independent fresh HUMAN and signed UCII agent verification/authority checks in a dedicated protected executor process.
2. Provision a fixed root-controlled sandbox artifact and private receipts directory.
3. Add owner-bound execution/status IPC, including read-only uncertain-outcome reconciliation.
4. Add authenticated gateway/website request and receipt display.
5. Run Oracle isolated tests and denial probes before approving a fresh sandbox request.
6. Verify one success, replay denial, expiry/revocation rejection and durable receipt retrieval.

Existing standing infrastructure.deploy authority stays REVOKED. Guardian, Voice, identities, credentials and controller custody remain unchanged.


## Independent evidence adapter and status follow-up

Oracle 41-test acceptance is confirmed at c98da34 (11.094 seconds). executor_evidence.EvidenceVerifier now provides the required independent check: protected HUMAN resolver, fresh protected signer challenge including action digest, and strict public UCII signed delegated/check response validation. It checks active agent credential and separate sandbox operation delegation. The adapter's signer/HUMAN functions must be supplied by protected composition, never ordinary request data. This component is not registered with a daemon or endpoint yet.

sandbox_executor.status returns only owner/product/agent-bound approval and validated receipt evidence. RESERVED with receipt reports reconciliation_required=true without mutating UCII. Missing/mismatched receipts for CONSUMED fail uncertain. No release, replay or automatic finalization exists. Final expiry is checked after network evidence returns, before the receipt effect. Full local suite is now 48 tests; Oracle rerun pending.


## Dedicated process and installation

Oracle 48-test acceptance at 0fdaff8 is confirmed. executor_service.py composes EvidenceVerifier with independent fixed-local HUMAN session validation and protected signer access. Exact action comes from the owner/product/agent-bound UCII approval; request cannot supply paths or action JSON. IPC contract is exactly version=ucii-alexa-executor-v1, command=execute|status, approval_id, action_digest, human_token. Receipt retrieval authenticates the owner but performs no effects.

Dedicated unit uses ucii-alexa-executor account, ucii-alexa-executor-ipc group, and supplementary database/signer groups. Runtime socket /run/ucii-alexa-executor/executor.sock, fixed root artifact /etc/ucii-alexa-executor/artifact.json, private receipts /var/lib/ucii-alexa-executor. Database write access is required for reservation/consumption; this is trusted service code, not a public generic SQL boundary. No controller secrets or authority issuance functions are loaded.

Run Oracle tests first, then sudo python3 deploy/install_executor.py. Installer refuses an existing/partial installation instead of replacing it, creates only fixed artifact/unit/bindings, starts the service, and observes socket existence without sending an execution. It grants nothing and exposes no public route. On readiness failure inspect service logs rather than rerun installation. Four new service tests bring the local suite to 52; Oracle installation/denial acceptance pending. Gateway/website adapters and sandbox-specific delegation remain subsequent steps.
