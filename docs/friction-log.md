# Friction Log

Record friction as it occurs. Do not manufacture or retroactively exaggerate issues for judging.

## Judging significance

Amazon's current official rules state that friction-log entries are optional but can contribute a **bonus of up to 10% to the final Stage 2 judging score**. During Stage 1 downselection, Amazon's internal review team assesses submitted friction-log entries and passes a recommended bonus to the Stage 2 judging panel.

Treat this as a first-class build artifact:

- record friction contemporaneously from the first Alexa+/Amazon/AWS development session;
- preserve concrete evidence such as error text, documentation references, setup steps, and workarounds where appropriate;
- keep entries factual, reproducible, and useful to Amazon's developer teams;
- do not manufacture friction or inflate severity;
- review the log before submission, but do not reconstruct it from memory at the end.

## Entry template

### YYYY-MM-DD — Short title

- **Product/tool/API/SDK:**
- **Task attempted:**
- **Steps taken:**
- **Expected:**
- **Actual:**
- **Severity:** low / medium / high / blocking
- **Workaround:**
- **Actionable suggestion:**
- **Evidence/reference:**

---

## Entries

The entries below concern the website implementation inspected on 2026-10-02. They are internal UI/integration issues, not established Amazon/Alexa+/AWS defects. No Amazon/AWS onboarding or API failure was observed in this session; do not present these entries as qualifying platform friction without independent evidence.

### 2026-10-02 — Website service adapter remains disconnected

- **Product/tool/API/SDK:** UCII for Alexa+ website; internal service adapter.
- **Task attempted:** Inspect whether the published UI is ready for real identity, authority and execution integration.
- **Steps taken:** Read lib/authority.ts, app/api/gateway/route.ts and app/page.tsx at website commit 3658f4be252f1ce0f6b69819b844f438b19b820b.
- **Expected:** A documented mapping from controls to verified backend contracts and renderable authoritative responses.
- **Actual:** Server adapter intentionally returns 503 INTEGRATION_NOT_CONFIGURED. Several call sites discard successful responses, and status labels remain fixed placeholders.
- **Severity:** blocking for real end-to-end operation; intentional disconnected behavior is not itself a platform defect.
- **Workaround:** Keep unavailable states truthful and protected execution disabled. Local drafting/review remains usable.
- **Actionable suggestion:** Implement the allowlisted adapter and normalized state rendering together; complete docs/website-ui-integration.md before claiming integration.
- **Evidence/reference:** Website source files above; [integration contract](website-ui-integration.md).
- **Status:** Open; no backend integration attempted or completed here.

### 2026-10-02 — Request text does not determine the drafted operation

- **Product/tool/API/SDK:** UCII for Alexa+ website; local request composer.
- **Task attempted:** Inspect action preparation for the different suggestion texts.
- **Steps taken:** Read operation initialization and propose() in app/page.tsx at the same website commit.
- **Expected:** A GPU discovery request does not silently become an infrastructure deployment action.
- **Actual:** operation initializes to infrastructure.deploy and is reused for every draft until manually edited; proposal preparation does not interpret the request.
- **Severity:** medium in the disconnected UI; must be corrected before real action integration.
- **Workaround:** Review/edit exact operation and resource; backend remains disconnected and no executor exists.
- **Actionable suggestion:** Require validated canonical action preparation or explicit operation selection, and clarify ambiguity before authorization.
- **Evidence/reference:** app/page.tsx operation state and propose(); integration contract section 4.
- **Status:** Open; documented, not fixed by this documentation change.


### 2026-10-07 — Oracle integration inspection lacks ripgrep

- **Product/tool/API/SDK:** Self-hosted Oracle development environment; internal UCII/Alexa+ integration tooling.
- **Task attempted:** Locate existing service-entitlement and enrollment implementations before wiring the website's economic access.
- **Steps taken:** Read live OpenAPI from localhost port 8000; inspect authorization request schemas; run a bounded source search under src, tests and docs.
- **Expected:** Source search returns existing implementation and documentation references.
- **Actual:** Shell reported `Command 'rg' not found`; the entitlement source search did not run. OpenAPI retrieval succeeded.
- **Severity:** low; source inspection is delayed, not a UCII runtime failure.
- **Workaround:** Use Python standard-library source scanning without installing packages. Follow-up execution is pending.
- **Actionable suggestion:** Provide a dependency-free inspection command or explicitly list optional development tools in setup instructions.
- **Evidence/reference:** User-provided Oracle terminal output, 2026-10-07 approximately 14:37–14:41 America/Toronto; UCII checkout dfea543.
- **Status:** Open pending fallback inspection.
- **Classification:** Internal development friction; no Amazon/Alexa+/AWS platform defect or qualifying bonus claim established.

### 2026-10-07 — Alexa+ runtime foundation is not yet deployed

- **Product/tool/API/SDK:** Internal Alexa+ UCII gateway deployment and website integration.
- **Task attempted:** Identify the existing backend to connect the published website.
- **Steps taken:** Check expected checkout, Alexa-named systemd services, live UCII API and gateway repository tree.
- **Expected:** Locate runtime implementation and supported contracts if already provisioned.
- **Actual:** /opt/ucii/ucii-alexa-authority-gateway was absent; no Alexa-named service was listed. Gateway repository main at 26a963508c501e128f54466a57378bdd880ceaee contained documentation/assets but no backend implementation. UCII service was active; supported public authorization routes were present.
- **Severity:** blocking for end-to-end website operation; missing implementation is not a platform defect.
- **Workaround:** Inspect reusable UCII and related-project implementations, then implement the gateway against verified public contracts. Keep disconnected website states truthful meanwhile.
- **Actionable suggestion:** Track gateway setup, website integration and runtime acceptance separately so a completed UI is not mistaken for a deployed backend.
- **Evidence/reference:** Oracle terminal inspection on 2026-10-07 approximately 14:35 America/Toronto; live OpenAPI and repository inspection; [website integration contract](website-ui-integration.md).
- **Status:** Open. No deployed gateway or completed lifecycle is claimed.
- **Classification:** Internal build/deployment gap; no Amazon/Alexa+/AWS platform defect or qualifying bonus claim established.

#### Session requirements recorded with these findings

Brad confirmed ownership of UCII and requires Alexa+-scoped entitlement usage to satisfy the economic gate without paying ourselves. Authentication, HUMAN governance, delegation and execution permission remain separate. Reuse relevant existing repositories and documentation rather than recreating established mechanisms. The grant request schema currently exposes identity_id, allowed_operations and granted_by; expiry, use limits and exact-action enforcement require source inspection before conclusions or changes.

### 2026-10-07 — Website health integration used the wrong hostname and unsupported redirect mode

- **Product/tool/API/SDK:** Sites-hosted website / Cloudflare Worker fetch; internal UCII connection adapter.
- **Task attempted:** Wire Connection details / Check connection to real UCII health.
- **Steps taken:** Publish a server-side health probe; compare Oracle local health and nginx routing; correct the URL to https://api.ucii.sportgen-ai.com/health; expose the caught error after the hosted check continued to fail.
- **Expected:** Render healthy UCII independently of unconfigured Alexa+, authority gateway and executor.
- **Actual:** The original ucii.sportgen-ai.com/health returned nginx 404; api.ucii.sportgen-ai.com/health returned 200 and {"service":"UCII","status":"healthy","version":"1.0.0"}. Hosted fetch then failed immediately with TypeError: Invalid redirect value, must be one of "follow" or "manual"; "error" is unsupported at the edge. Generic exception handling initially hid the cause.
- **Severity:** medium; blocked the first live website connection check.
- **Workaround:** Use the verified API hostname and redirect:"manual"; existing response validation rejects redirects as unhealthy. Record safe exception details instead of only a generic retry message.
- **Actionable suggestion:** Validate runtime-specific fetch options and surface diagnostic causes before repeating user tests.
- **Evidence/reference:** Oracle nginx/health output and user-rendered website error on 2026-10-07 around 14:59–15:05 America/Toronto. Website fix source commit 876fd5f93fddb8474918dcc0f22ed8c9d737cca4.
- **Status:** Fix built; publication and hosted user confirmation tracked separately. UCII runtime itself answered healthy; no end-to-end authority integration is claimed.
- **Classification:** Internal implementation / hosting-runtime compatibility friction, not an established Amazon/Alexa+/AWS defect.


## 2026-10-07 — Verified connection and identity enrollment

- Website health recovery confirmed by the operator: UCII online, then real MCP initialize/list/call succeeded through the public HTTPS gateway.
- Immediate HTTPS test after Nginx reload returned 404; subsequent local and public initialization both returned HTTP 200. No further routing change was required.
- No HUMAN or Alexa integration agent existed in the identity listing. Separate one-use, root-controlled product enrollment authorizations covered POST /v1/identity for product ucii-alexa without payment.
- HUMAN and integration AI_AGENT creation and subsequent retrieval succeeded. Full provisioning responses were retained using systemd encrypted credentials; controller material was not printed.
- systemd-creds reported that the host credential secret is on unencrypted media. Custody currently uses host encryption; this warning does not establish hardware-backed or encrypted-disk protection.
- Identity records alone do not establish credential possession, human authentication, delegated authority, or execution permission.
- Added a read-only MCP identity tool with server-configured bindings and explicit UNVERIFIED status. Oracle deployment and website identity wiring subsequently confirmed by the operator.
- These are internal integration observations, not claimed Amazon product defects.


## 2026-10-07 — Live identity cards and protected credential proof

- Operator confirmed both website identity cards retrieve active public records through MCP.
- Gateway restart initially produced HTTPS 502. Journal showed startup completed nine seconds after restart; later local identity call returned HTTP 200. Future deployment tests should wait for readiness.
- Agent first ML-DSA-65 credential and verification/execution economic entitlement provisioned using the existing UCII operator workflow. This grants no underlying action authority.
- Dedicated Alexa signer service and IPC group installed, with encrypted systemd credential delivery. Socket confirmed mode 660. Initial socket check at 492 ms was premature; startup completed after approximately five seconds.
- A fresh agent credential signature and separate request-bound entitlement proof were sent to POST /v1/credentials/verify. UCII returned HTTP 200, verified true, matching identity and fingerprint, status ACTIVE.
- Gateway live verification tool deployed; Oracle invocation and hosted website verification subsequently confirmed by the operator.
- Website publish packaging initially produced an empty archive; regenerated unchanged build packaging and deployment succeeded.


## 2026-10-07 — Hosted verification acceptance and card layout correction

- **Task:** Test the live Verify agent credential control and inspect its rendered card.
- **Expected:** Matching agent proof, fingerprint and time displayed without overlapping controls.
- **Actual:** Operator confirmed VERIFIED and matching fingerprint. Retrieve identity and Verify agent credential initially competed for horizontal space on the card.
- **Severity:** Low; visible layout defect, verification itself worked.
- **Fix:** Full-width vertically stacked card buttons, explicit spacing and wrapping; build passed, publication succeeded, operator confirmed the result.
- **Evidence:** Operator's rendered website text and visual feedback at approximately 16:17–16:22 America/Toronto; Site fix commit 1a3655a0b734757db2121575c13b3bb027455a20.
- **Status:** Resolved and user confirmed.
- **Classification:** Internal website layout friction.

## 2026-10-07 — Alexa developer-tool availability clarified

- **Task:** Determine whether Alexa+ device/console setup was needed before wiring.
- **Finding:** Official FAQ says gated add-on tools are unavailable to hackathon participants; a website acting as a real Streamable HTTP MCP client is an accepted simulated-experience path.
- **Resolution:** Build and test the actual MCP client/server integration now; label the future conversational surface accurately as a simulator. Do not claim an actual Alexa device connection.
- **Source:** https://amazonappdev2026.devpost.com/details/faqs (rechecked October 7).
- **Classification:** Documented platform access constraint and setup clarification, not an observed failed Alexa API call or fabricated Amazon defect.

## 2026-10-07 — Publication archive retry

- A layout publication archive was rejected as invalid/incomplete. Repackaging the unchanged successful build produced an accepted archive and successful deployment.
- Earlier identity publication similarly yielded a zero-byte archive. Preserve archive-size/contents verification in deployment workflow rather than retrying an empty artifact.
- Classification: Internal build/publication tooling friction; resolved for today's deployments.


## 2026-10-08 — HUMAN authentication integration

- Confirmed existing active HUMAN identity had no authentication account.
- Initial terminal prompt opened /dev/tty with r+ and failed because the device is non-seekable. Switched to read-only terminal input; failure occurred before enrollment mutation.
- Initial script imposed a 16-character password minimum beyond UCII's existing eight-character contract. Operator requested eight; corrected the script to match UCII.
- Registration HTTP request timed out after 30 seconds. Read-only reconciliation confirmed exactly one active linked account and healthy UCII. Registration was not repeated.
- Existing session validation took a token query parameter, creating URL/access-log exposure risk. Added a header-only /v1/auth/session endpoint in UCII, preserving compatibility routes. Five focused tests passed on Oracle; live unauthenticated request returned 401.
- Real login and header-based session resolution matched the existing HUMAN identity. No password or token was printed.
- Gateway browser login routes use a separate HTTP adapter, not MCP tools. UCII bearer tokens stay in server memory behind opaque 15-minute handles. Dedicated service entitlement coverage added for login economic access; no action authority granted.
- Gateway login/session/sign-out round-trip passed. Signed-out session returned 401.
- Nginx exact HTTPS login/session routes installed and validated. Public session request without authentication returned 401.
- Website login form, HttpOnly Secure SameSite cookie, session display and sign-out implemented. Hosted browser acceptance remains pending.
- These are internal implementation/runtime observations, not claimed Amazon product defects.


### 2026-10-08 — Hosted HUMAN session acceptance and authority-check scope
- Owner confirmed hosted login displays AUTHENTICATED on Security / Identity and Home, and sign-out returns SIGNED OUT. Password authentication is explicitly separate from cryptographic device proof and action approval.
- Reviewed UCII delegated authority router, request/response schemas and evaluator. The existing check verifies the bound agent credential and exact logical operation; resource and environment constraints are not evaluated by this endpoint.
- Added read-only MCP tool `ucii_authority_check`: internally generates and signs an operation challenge, verifies the returned identity/credential/operation and authority state, and always reports execution blocked. No authority grants, payments or execution are performed.
- Python compilation passed. Oracle live acceptance and website button wiring remain pending; no live authority outcome has been asserted.


### 2026-10-08 — Live operation-authority denial and website wiring
- Oracle acceptance passed: signed `infrastructure.deploy` check returned `NOT_GRANTED`, `operation_authorized: false`, `executed: false` and `execution_allowed: false`. This is a real UCII result, not a simulated denial.
- Published website source `a80c99e266b63d6bf636117e0e559e758ddd53da`: Check authority now validates the HUMAN session on the server, calls the MCP operation check, validates the bound active agent identity and fresh result, and displays DENIED for non-active authority.
- Positive operation-only authority remains AUTHORIZATION_REQUIRED for the proposed action. Resource and environment are explicitly unchecked, and execution remains blocked.
- UI evidence expires after one minute and clears when the proposal or HUMAN session changes. Activity entries describe local-session observations only.
- TypeScript checking and production build passed; private publication succeeded. Hosted button acceptance remains for owner testing.


### 2026-10-08 — Hosted denial accepted and controller custody reconciled
- Owner confirmed hosted Check authority displays the real NOT_GRANTED / DENIED result for infrastructure.deploy while execution remains blocked.
- Controller custody conversion initially failed because decryption inferred the artifact filename instead of its embedded credential name. Supplying the original systemd credential name resolved it; no state changed during failed attempts.
- Owner confirmed the saved Alexa controller authority verifies against UCII and a canonical encrypted lifecycle credential was prepared. No controller rotation, grant or revocation occurred.
- Dedicated Alexa lifecycle service and authenticated grant/revoke controls remain pending.


### 2026-10-08 — Isolated protected approval boundary
- Dedicated Alexa lifecycle service uses Alexa's encrypted controller credential and the existing UCII database access group.
- A connect-only readiness probe exposed an inherited empty-request crash. Alexa wrapper now bounds socket reads and isolates empty, oversized, timed-out and disconnected clients without stopping the service. Observed startup took about 33 seconds; readiness checks use the socket artifact and explicit ready log.
- Owner confirmed a grant lacking HUMAN authentication returns DENIED.
- Added non-MCP /auth/authority gateway route for explicit grant/revoke confirmation. It resolves the HUMAN session, passes the server-held UCII token only over local IPC, and verifies public mutation metadata.
- Protected custody independently validates that HUMAN token with UCII and consumes a matching root-owned one-use lifecycle authorization before invoking UCII's controller/authority primitives.
- Python compilation passed. Gateway route live acceptance, root operator authorization preparation, HTTPS routing and website approval UI remain pending. Operation grants are standing authority; expiry of an issuance permit must not be presented as expiry or single-use execution of the granted authority.


### 2026-10-08 — HTTPS approval gate and hosted review controls
- Owner verified local and HTTPS /auth/authority return HTTP 401 without a HUMAN session.
- Published website source `e57b6d755bc103f338e491c78842e747df3c1937`: operation grant review and exact-record revoke review now use a server-side adapter with strict origin, finite request shape, session validation and response checks. UCII tokens stay on the server.
- Review explicitly describes standing operation authority, not a single-use action grant. Resource/environment constraints and protected execution remain unestablished.
- No grant authorization has been prepared and no successful grant/revoke is asserted. Next acceptance: authenticated website confirmation must remain blocked when the root-controlled operator permit is missing.
- TypeScript checking, production build and private publication succeeded.


### 2026-10-08 — Committed grant reconciled and ACTIVE check accepted
- Owner prepared one exact operation-grant issuance permit. Hosted confirmation showed generic missing/used-permit feedback, but read-only inspection found one consumed permit and one ACTIVE authority record. No grant retry or replacement permit was issued.
- Owner confirmed a fresh hosted signed operation check returns ACTIVE for infrastructure.deploy. Proposed-action status remains AUTHORIZATION_REQUIRED because resource/environment approval and execution are not established.
- Cause of the original confirmation feedback remains unconfirmed. Hardened custody response semantics so failures after permit consumption report uncertain outcome and require authoritative reconciliation, rather than claiming a definite denial.
- Check authority was disabled until Exact resource was filled; owner confirmed this resolved the UI blockage.
- Reviewed exact-record revocation response: UCII returns record/state/reason/time, not allowed_operations. Hosted response validation must accept this finite revoke contract before revocation testing.
- Implementation plan now records verified acceptance separately from pending production controls. Root permit consumption and public signed authority checks are authoritative evidence; local UI events are not durable provenance.


### 2026-10-08 — Revocation contract corrected before mutation acceptance
- Published website source `dfde77f0e6082a77e4635254e1e5e367dae641e6` accepts UCII's exact-record REVOKED response without requiring an absent operation list. It still verifies command, record identifier and expected state.
- Added an explicit resource-entry hint and a Close and check authority recovery control after approval errors.
- TypeScript and production build passed; private publication succeeded.
- Five isolated scenarios using the actual custody class passed with controlled dependencies: missing HUMAN proof, rejected permit, post-consumption exception, post-consumption denial, and successful mutation response. These are response-boundary tests, not live mutation acceptance.
- Custody outcome hardening is committed for Oracle installation. Actual revocation and subsequent signed REVOKED/DENIED acceptance remain pending.


### 2026-10-08 — Hosted revocation lifecycle accepted
- Owner confirmed exact-record revoke review, successful UCII revoked response, and subsequent fresh signed infrastructure.deploy check returning REVOKED / DENIED. HUMAN login and identities persisted. No execution occurred.
- Completed live operation-authority sequence: initial NOT_GRANTED/DENIED, committed standing grant reconciled, ACTIVE check, exact-record revocation, fresh REVOKED/DENIED.
- One-minute evidence expiry cleared the record reference needed to open revocation, forcing navigation within a minute. This is a UX defect; a stable record reference may be retained separately from fresh authorization evidence while protected revocation independently rechecks actual state. Fix remains pending.
- Exact-action resource/environment constraints, protected executor, conversation integration, authoritative activity and product entitlement isolation remain pending. This milestone does not establish full production readiness.


## Selectable sign-in duration and revocation record references — 2026-10-08

**Friction:** The fixed 15-minute gateway session interrupted owner testing. Merely extending the browser cookie would not work: UCII's current authentication token expires after one hour. Separately, expiring a one-minute authority check removed the record reference needed to open the revocation review.

**Change:** Sign-in offers 15 minutes, 1 hour (selected initially), or 4 hours. The gateway enforces an absolute chosen deadline. A bounded background task rotates UCII tokens before expiry, including while the browser is closed, and serializes rotation with session checks and authority requests. Passwords are never saved for renewal. Sign-out, eviction and deadline expiry remove the opaque session and cancel renewal. A failed or ambiguous rotation discards the session rather than retrying a potentially consumed token. Gateway restarts still require sign-in.

The website keeps a previously retrieved active authority record reference separately from fresh permission evidence. It remains available for revocation review after the check expires; it never enables execution. Sign-out and confirmed revocation clear the reference. The protected service independently checks the authenticated HUMAN and actual record when confirmation is submitted.

**Validation:** Eight isolated gateway tests passed against a mock UCII HTTP boundary: allowed deadlines, invalid durations, expiry, logout, background rotation with unchanged deadline, rotation failure, concurrent session validation during rotation, and unauthenticated authority rejection. Website TypeScript validation passed. These tests do not claim a completed four-hour live retention test. Oracle must pull the new gateway code, run the tests and restart, then the owner should sign in with a selected duration and verify the displayed expiry. No new authority was granted or revoked for this change.


### 2026-10-08 — Selected session duration accepted on Oracle and hosted website

- Owner pulled gateway source through the selectable-session update, ran all eight session tests successfully on Oracle, and restarted the gateway.
- Owner signed in using the four-hour choice at approximately 17:12 America/Toronto; the hosted HUMAN session displayed expiry 21:12:21. This verifies initial duration selection and the hosted/server deadline contract.
- Website source `9561f439c5a288f818340f298d0f840f51558115` was built and privately published successfully. Live retention and renewal beyond one hour remain pending; four-hour continuous acceptance is not yet claimed.

### 2026-10-08 — Exact deployment request boundary begun

- Reinspection confirmed the current UCII delegated check evaluates operation authority but does not enforce the proposed resource/environment. Protected execution cannot be enabled solely from that positive response.
- Added an immutable canonical-action contract binding the server-derived subject, operation, resource, environment and exact deployment artifact digest. A mutable artifact label is insufficient to identify the exact action a human is approving.
- Six isolated contract tests passed locally. Each changed execution field changes the digest; ambiguous scope and browser-supplied subject/approval fields are rejected. A digest is an identifier, not authorization evidence.
- This module is deliberately not advertised as a live authorization route. Hosted draft/artifact capture, stored proposals, protected one-use approval, consumption and executor enforcement are the dependent wiring steps. No new grant, revocation or deployment occurred.


### 2026-10-08 — Canonical action tests accepted and server-held proposals implemented

- Owner ran all six canonical-action tests successfully on Oracle before proposal wiring.
- Implemented authenticated create/retrieve/cancel proposal endpoints outside MCP, using the existing opaque HUMAN session and UCII session validation. Agent identity comes from server configuration, not the draft.
- Private application SQLite records store immutable canonical snapshots and action digests with a fixed 15-minute lifetime. Human-owned idempotency keys preserve the same snapshot and expiry on retries; changed actions with the same key conflict. Cancelled/expired proposals cannot be restored by retrying the original key. This storage is draft state and grants no authority.
- Added existing website artifact capture and Save/Retrieve/Cancel saved proposal controls. The server adapter checks exact returned fields and recomputes the digest. A device-local opaque proposal reference permits reload retrieval; the gateway independently verifies ownership.
- Twenty-three isolated tests passed locally, including persisted snapshots, wrong-owner rejection, concurrent retry uniqueness, expiry/cancellation and proposal-session gates. Website TypeScript checking and build passed for source `fb857edcb0a720b412aa0720bed95e68ce61602e`.
- Added a repeatable Oracle installer for private gateway state storage and the exact HTTPS proposal route, with nginx backup/validation/restore and bounded readiness checking. Its gateway restart ends the current in-memory login; continued live session-renewal testing starts from the next sign-in.
- Oracle installation and hosted save/reload/cancel acceptance remain pending. No approval, new authority grant, revocation or deployment occurred. Protected exact-action approval/consumption and execution remain unconnected.


### 2026-10-08 — Hosted exact proposal lifecycle accepted

- Owner saved an exact infrastructure.deploy test proposal using test-app, staging, and the SHA-256 digest of the gateway source file as a test artifact. No deployment was attempted.
- Hosted save returned PROPOSED and expiry 17:47:58 America/Toronto. After refresh, retrieval returned the stored proposal with the same expiry; retrieval did not extend its lifetime.
- Owner cancelled the saved proposal and retrieved it again; state remained CANCELLED with the same expiry. Approval remained NOT_ESTABLISHED and execution stayed blocked.
- These observations confirm the live storage/HTTPS/website proposal path. The installer terminal output and full new Oracle test run were not supplied, so no additional terminal acceptance is asserted.
- Reinspection confirmed UCII's existing operation-scoped authority model lacks exact-action binding and execution-use consumption. Protected Just this time approval requires core enforcement; a proposal hash or UI confirmation alone cannot substitute for it. Live schema inspection precedes that change.


### 2026-10-08 — Live schema confirmed; exact-action UCII primitive tested

- Owner's read-only SQLite schema output confirms existing operation authority, HUMAN governance/step-up and controller tables, with no exact-action approval/use table. Existing components were inspected before extending authority persistence.
- Added a dedicated model/service to UCII, without installing a route, executing DDL or touching existing identities, credentials, standing grants or controller custody.
- The trusted-side primitive stores independently established exact approval, reserves its single use with an atomic matching update, records a reconciled execution receipt, and revokes unused approval. It does not authenticate or establish approval. Product, HUMAN, agent subject and full canonical action must match; validity is bounded to five minutes.
- Nine isolated actual SQLAlchemy/temporary-SQLite tests passed locally. Parallel reservation had one winner; expired/not-yet-valid, altered scope, wrong product/HUMAN, duplicate issuance and replay were blocked. RESERVED state cannot be silently released after uncertain effects.
- UCII checkpoint `8a2b35c5d3bc38be81337d7f550b1f1f46c5b6e7` includes source, tests and an explicit protected-integration contract. Oracle test execution, narrowly scoped migration, protected approval composition and executor remain pending. No Just this time success or production readiness is claimed.


## Exact approval table activation checkpoint — 2026-10-08

Owner confirmed all nine UCII exact-action approval tests passed on Oracle at 8a2b35c. Tests used temporary SQLite, not the live database. The explicit scripts/install_exact_action_approval.py migration is committed in UCII: it makes a private online SQLite backup, creates only exact_action_approvals, and stops if the table already exists. Local temporary-database verification confirmed preserved identity data, foreign keys, empty approvals, and repeat protection. Live migration is awaiting the owner command. No exact approval is issued by this migration; protected confirmation and execution remain unwired.


## Exact confirmation wiring — 2026-10-08

Owner confirmed live approval table activation and backup at 90527da. New protected confirmation wiring, exact issuance permit preparation, HTTPS installer and status reconciliation are committed. Local 31 tests passed; website TypeScript passed. A draft claim now prevents approval/cancellation races. Uncertain outcomes require UCII status retrieval; duplicate issuance cannot create another use. Root exact permits remain separate from standing authority permits. Oracle deployment/acceptance is pending; no live exact approval or execution is claimed. See docs/engineering/protected-exact-approval-wiring.md.


## Exact approval live acceptance and revocation — 2026-10-08

Oracle: all 31 prior gateway tests passed. Installer restarted services and installed nginx route but readiness GET lacked required proposal UUID, causing HTTP 400. Readiness query now supplies a canonical UUID and expects unauthenticated 401.

Owner accepted exact approval 9ca0fb94-4db5-4b55-8956-f2faece26dcf for proposal 3ec98387-092b-43f0-bdfb-edb44773fc5b, digest sha256:adf177fb9e978faf06ff6237fed59e72a6be17dfd295f3e2b6879b844a3696e0. UI showed ACTIVE, then EXPIRED at 22:47:49 UTC, always execution_allowed=false. Expired record remains unchanged. The prior proposal APPROVED label confused historical issuance with current validity; display now says APPROVAL RECORDED.

New finite revoke_exact_approval verifies current HUMAN session/controller custody, targets the product/proposal/owner/agent bound UCII row, and removes only unused unexpired approval. Revocation creates no authority and needs no new issuance permit. Reserved or expired records are unchanged; repeated REVOKED response is reconciliation. Local suite now 34 tests passes. Oracle update and live fresh-approval revocation acceptance pending. No execution or Alexa conversation enabled.


## 2026-10-09 — Exact revocation accepted; sandbox effect boundary prepared

Owner confirmed a fresh exact approval for proposal be12aa2a-29ad-4b6b-a1fe-e98b9e7ce05f was ACTIVE, explicitly revoked, and still REVOKED on subsequent status retrieval. Draft state APPROVAL_REVOKED; execution remained blocked. Previous Oracle update at 3568429 passed all 34 tests and completed the corrected installer/nginx check.

Review identified a misleading potential demo boundary: a digest of gateway/server.py is a test binding, not an actual deployable artifact. The executor foundation therefore uses sandbox.artifact.verify for staging test-app, with ARTIFACT_VERIFIED and deployment_performed=false in receipts. No standing deployment authority was restored.

Added isolated trusted execution primitive and seven tests; all 41 local tests pass. Missing evidence or artifact mismatch causes no effect; evidence loss after reservation prevents effects and retry; a lost consumption commit retains a durable receipt and RESERVED state for reconciliation. Current evidence is an explicit protected-composition callback, not a production auth implementation. No endpoint/website button is enabled until that adapter and status/reconciliation are wired. See engineering/sandbox-executor-boundary.md. No observed Amazon/AWS onboarding friction or actual Alexa connection is claimed.


## 2026-10-09 — Oracle sandbox tests and independent evidence boundary

Owner pulled c98da34. A duplicated terminal paste joined -v with cd and prevented test execution; repository pull succeeded. Re-running the single corrected command passed all 41 tests on Oracle in 11.094 seconds. No services restarted or effects requested.

Added EvidenceVerifier: protected HUMAN validation on every check, fresh signed nonce and exact action digest, fixed local public UCII delegated/check URL, redirect rejection, bounded response and strict current active credential/operation-authority bindings. Sandbox requires its own sandbox.artifact.verify authority; no infrastructure.deploy grant is restored. The verifier is a trusted composition module, not yet process/route wiring.

Owner-bound read-only status validates durable receipt fields against UCII approval/reservation; RESERVED remains reserved even when a valid receipt exists. It reports reconciliation required and never consumes or replays automatically. Added seven tests, including approval expiry while the final network evidence check completes, owner isolation and tampered receipt rejection. All 48 local tests passed. New Oracle tests and protected process/website installation remain pending.


## 2026-10-09 — Dedicated sandbox process prepared

Owner confirmed all 48 tests passed on Oracle at 0fdaff8 in 5.783 seconds. Prepared executor_service.py local finite Unix-socket boundary, ucii-alexa-executor.service separate account/group and fixed paths, and deploy/install_executor.py. Identity/fingerprint bindings are copied only from an explicit allowlist in existing gateway configuration; no secrets printed. Root-owned fixed sandbox artifact is provisioned exclusively, with digest reported. Existing service/configuration installations are not overwritten on retry.

The service derives owner/agent/action from protected configuration and UCII approval, validates HUMAN independently, checks signed current operation authority, and writes only private sandbox receipts. Browser-supplied paths/subjects and unauthenticated requests fail before database access. Empty/oversized local clients are bounded. All 52 local tests pass. Production installation and no-session socket rejection remain owner acceptance steps. No grants, approvals, effects, public routing, or website execution enabled by this source update.


## 2026-10-09 — Scope reset and official Alexa access correction

Owner identified excessive deployment/approval complexity and redirected the product to configured capability first, then HUMAN-controlled guardrails. Preserve working identity/signing/login/UCII authority; pause deployment and exact-approval expansion. Official hackathon FAQ rechecked: participants cannot obtain Alexa+ toolkit/CLI/simulator access or connect self-hosted MCP to real Alexa devices through those tools. Our previous recommendation to make actual Alexa onboarding next was incorrect. Accepted path: existing custom frontend using real initialize/tools-list/tools-call over Streamable HTTP. Sources: https://amazonappdev2026.devpost.com/details/faqs and organizer discussion https://amazonappdev2026.devpost.com/forum_topics/45262-is-the-alexa-mcp-toolkit-alexa-ai-cli-available-to-hackathon-participants . No private account probing or AWS role setup attempted.

Website source d1fb17b57be019ebd7ce01238a81675ad849b3b6 adds bounded text simulation calling existing real MCP health without UCII login; unsupported requests are rejected rather than silently mapped to infrastructure.deploy. Exact proposal controls moved into a collapsed advanced section. TypeScript and production build passed; user live acceptance pending. Allowed/Blocked tool policy mutation and durable activity remain next implementation items; do not claim full permission flow complete.


## 2026-10-09 — Simple Permissions page and narrow HUMAN tool controls

Owner requested removal of unconnected policy categories and unnecessary documentation. Website Authority renamed Permissions, with two cards: public MCP health and fixed staging artifact verification. Removed primary purchase/document/deployment policy forms; retained advanced records/code. README and current implementation plan rewritten concisely; broad architecture/design/UI contracts moved to archive with redirect notes. Friction log preserved as required contemporaneous evidence.

Simple tool permission route uses existing HTTPS authority endpoint and protected controller custody. Configured HUMAN ownership plus independently verified current HUMAN session and controller possession establishes permission-change authority for sandbox.artifact.verify only; no repeated terminal issuance permits for this fixed harmless capability. Generic advanced grant routes retain existing gates. Request cannot choose operation, identity, or artifact paths. Block revokes only exact one-operation records; restoration creates a fresh record, preserving revoked history. Mixed-scope active records require advanced review rather than broad revocation.

Four real temporary-SQLite permission tests added: allow/block/restore/idempotency/history, absent session/changed scope/fabricated confirmation rejection, controller failure and preservation of unrelated authority. Full local suite 56 passes. Site TypeScript/production build pass, source 1f742d11939af1f50d03eb78a0779917020c52c4. Oracle pull/tests and gateway/lifecycle restart required before live permission acceptance. Controlled execution from conversation and durable Activity remain pending and are stated in the UI. No deployment authority restored.


### 2026-10-09 — Public chat and login latency

- Removed the unsupported deployment example's automatic sign-in dialog. Public health and capability questions do not require HUMAN authentication; permission changes still do.
- Production Site logs showed MCP initialize HTTP 502 behind the unavailable badge. This is a gateway connection failure, not an authentication denial.
- Added safe gateway login stage timings for access proof, password login, and session validation. No passwords, tokens, keys, or upstream exception bodies are logged.
- Gateway tests: 56 passed locally; Site TypeScript check passed. Login speed remains unverified on Oracle; deploy the timing change and inspect one real login before optimizing its bottleneck.

- Oracle confirmed gateway login timings: access proof 0.372s, UCII login 2.778s, session validation 0.263s (3.413s combined). Added UCII service setup, account lookup, password verification, hybrid signing, and token persistence timings in UCII commit 59a6d32. Python compilation passed locally; production timings and UCII regression tests are pending the operator update. No password parameters or identity/security checks changed. Resume conversation tool execution after this bounded latency diagnosis.


### 2026-10-09 — Fixed tool conversation wiring

- Added ucii_artifact_verify MCP tool. Requests can invoke only the protected fixed test-app staging artifact check. HUMAN login is needed to change Allow/Block; invocation uses the agent's current saved permission without a HUMAN session or exact issuance ceremony.
- Protected executor independently checks signed UCII delegated permission, reads only its fixed root-controlled artifact, rechecks permission, and durably records completed or blocked results. No deployment or caller-selected path is supported.
- Local tests: 59 passed; Site TypeScript check passed. Production validation pending: grant gateway membership in ucii-alexa-executor-ipc, restart executor/gateway, then test Block → Allow → Block from conversation.
- Login timing evidence: UCII service setup 0.077s, password verification 0.701s, hybrid signing 0.003s, persistence 0.010s. User confirmed fast sign-in after restart. Instrumentation did not optimize authentication; the earlier delay's exact cause remains unproven.

- Oracle rollout confirmed: 59 tests passed and executor/gateway restarted. Live MCP check at 2026-10-09T17:43:36Z returned NOT_GRANTED for sandbox.artifact.verify, explaining the blocked conversation result. No saved Allow grant was present at that check.
- Added Home Sign in entry to existing authentication form (Manage sign-in when authenticated). Blocked conversation results now link directly to Permissions and distinguish signed-in users from signed-out users. Site TypeScript/build passed; no permission was granted by this UI update.


### 2026-10-09 — Compact permission confirmation and saved Activity

- Moved Confirm/Cancel into the controlled tool permission card beside its controls; removed the detached confirmation panel and message.
- Replaced the empty Activity page and local diagnostics with a compact Time/Action/Result list and header Refresh. Reads up to 50 saved protected artifact receipts and UCII Allow/Block history through the existing /auth/authority route.
- Activity is owner-session authenticated at the gateway and independently verified in the executor before file/database reads. No new nginx route or schema required; no mutation occurs during refresh.
- 61 backend tests passed locally; Site TypeScript check passed. Oracle rollout requires pulling gateway and restarting executor/gateway, then signing in and refreshing Activity to verify historical records survive page reload.
