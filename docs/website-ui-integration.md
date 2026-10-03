# Website UI Integration Contract

Recorded: 2026-10-02 (America/Toronto).
Website: https://ucii-alexa-control.sportgen-ai.chatgpt.site
Inspected website source commit: 3658f4be252f1ce0f6b69819b844f438b19b820b.

This is the wiring and acceptance contract for the existing Home, Authority, Activity, and Security / Identity UI. It complements [architecture](architecture.md), [design/build](design-build.md), and [implementation plan](implementation-plan.md). Existing UCII governance, product entitlement isolation, and canonical implementation sequence remain authoritative. This document does not mark backend work complete or redefine production API routes.

## Current verified baseline

- The interface, navigation, local action drafts, local policy proposals, dialogs, and local diagnostics work.
- Browser adapter: `lib/authority.ts`.
- Server adapter: `app/api/gateway/route.ts`.
- Product rendering: `app/page.tsx`.
- Every backend call currently receives HTTP 503 with `INTEGRATION_NOT_CONFIGURED`.
- Alexa+ conversation, identity verification, policy retrieval/mutation, delegation, revocation, execution, and provenance are disconnected.
- Many controls currently discard successful responses; connecting APIs must also include normalized state storage and rendering.
- Labels for connection, identity, authority, and policy are fixed disconnected placeholders.
- The microphone displays an unavailable message. The waveform is decorative.
- Request drafting defaults to `infrastructure.deploy` regardless of request text.
- No protected execution control or executor integration exists. The EXECUTE pillar opens Activity.
- Activity filters select UI buttons but do not query or filter real records.
- Site source is currently separate from this gateway repository. This documentation does not copy or synchronize it.

## 1. Trusted integration boundary

Website / Alexa+ -> self-hosted authority gateway -> supported UCII public API -> protected executor.

The UI displays state and prepares proposals. The gateway coordinates and validates. UCII owns identity, governance, policy/authority enforcement and attributable evidence; do not implement a competing authority database or frontend decision engine.

- [ ] Inspect actual supported UCII and gateway contracts before mapping operations.
- [ ] Replace the 503 stub with an allowlisted server-side adapter; no arbitrary URL proxy.
- [ ] Validate versioned request and response schemas and reject unknown operations.
- [ ] Authenticate and bind sessions to the correct participant and agent server-side.
- [ ] Protect mutations against CSRF where cookie sessions are used; enforce origin/CORS and credential-handling rules appropriate to the deployment.
- [ ] Keep private keys, custody material, reusable credentials and secrets out of browser code, logs and proof.
- [ ] Apply existing Alexa+-scoped economic entitlement separately from authentication, governance and action authority.
- [ ] Configure HTTPS, bounded timeouts, safe error handling, and appropriate no-store behavior for sensitive/current authority responses.
- [ ] Preserve self-hostability and avoid adding paid services without a concrete need.

## 2. Existing control mapping

These dotted names are UI adapter operation names, NOT verified production endpoint paths.

| UI control | Current adapter name | Required backend behavior |
|---|---|---|
| Check connection | health | Separate gateway, UCII, conversation and executor availability |
| Retrieve human identity | identity.get, principal=human | Actual bound human identity and verification evidence |
| Retrieve Alexa+ identity | identity.get, principal=agent | Actual agent bound to this participant/integration |
| Begin verification | authentication.start | Start ceremony; add completion, cancellation and expiry operations |
| Check authority | authorization.check | Evaluate canonical action through UCII; validated evidence and reason |
| Request policy review | policy.propose | Read current version, propose diff, verify human, commit through UCII |
| Prepare temporary authority | delegation.propose | Exact grant proposal, verification, grant creation, fresh action check |
| Revoke Alexa authority | revocation.request | Explicit actual delegation IDs/scope, authenticated revocation |
| Lock authority changes | policy.lock | Defined authenticated lock semantics and verified resulting state |
| Refresh activity | activity.list | Real event query, filtering, pagination and proof references |

Additional contracts needed: session/state retrieval, policy and authority retrieval, conversation submission/events, canonical action preparation, approval completion, protected execution/status, and proof retrieval. Names and URLs must be chosen from verified contracts, not inferred from this table.

## 3. Load and render authoritative state

- [ ] Retrieve state on application opening and refresh after every completed mutation.
- [ ] Render responses rather than discard them.
- [ ] Replace fixed OFFLINE/UNVERIFIED/unavailable labels with authoritative or explicitly unknown state.
- [ ] Separate identity existence, credential verification, authenticated session and authority.
- [ ] Distinguish unknown/unavailable from confirmed absent, denied, consumed or revoked.
- [ ] Track evidence references, retrieval time, validity and policy version.
- [ ] Show expired/stale states and block execution pending revalidation.
- [ ] Prevent late responses from applying to an edited/cancelled action; bind responses to action identifiers/digests.
- [ ] Keep conversation, action, approval, connection and revocation states separate; unrelated request failures must not overwrite the active action lifecycle.
- [ ] Ensure reload retrieves backend state; browser drafts and diagnostics never become authority.

## 4. Conversation and canonical action

- [ ] Verify the actual Alexa+ integration supports the requested conversation data.
- [ ] Do not assume MCP supplies browser microphone access, speech recognition or transcripts.
- [ ] Connect real listening/interpreting/finalized transcript/agent response events where supported; otherwise retain honest unavailable states.
- [ ] Replace universal infrastructure.deploy draft defaults with validated interpretation or explicit operation selection.
- [ ] Clarify missing/ambiguous parameters before authorization.
- [ ] Keep utterance, agent interpretation, canonical action and UCII decision distinct.

Define a versioned canonical-action schema including request/action ID, server-resolved human and agent binding, operation, exact resource, operation-specific parameters, environment/destination, and amount/currency/merchant where relevant. Include canonical action digest for evidence/approval/execution binding. A deployment must include the exact artifact/version. Material changes invalidate prior approval and authorization.

## 5. Decision cards and evidence

- [ ] AUTHORIZED: exact action, authority source, scope, validity and proof.
- [ ] AUTHORIZATION_REQUIRED: concrete boundary and permitted Just this time / Discuss with Alexa / Cancel / Change future rule controls.
- [ ] DENIED: authoritative reason; stop without bypass.
- [ ] Unavailable/invalid/stale evidence: explicit failure; no execution.
- [ ] Trusted gateway/executor validates evidence, signature where required, principal binding, action digest, policy version, validity, use limits and revocation.
- [ ] A decision string alone must never enable protected execution.
- [ ] Render status with text/icons and appropriate green/amber/denied styling, not color alone.

## 6. Human approval and policy

- [ ] Replace display-label keys and strings with stable policy identifiers and typed validated values.
- [ ] Show actual current policy/version and exact proposed diff.
- [ ] Authenticate proposal-bound human approval; start of verification is not approval completion.
- [ ] Handle failed, abandoned, expired and replayed ceremonies without changing policy.
- [ ] Reject stale policy-version commits or obtain renewed review.
- [ ] Render the recorded new version only after UCII confirms it.
- [ ] Implement Just this time, Remember this, Remember until, Don't change, Never again, Ask me from now on, and Make this more restrictive.
- [ ] Alexa+ may propose; it cannot commit or manufacture approval.
- [ ] Silence, preferences, conversational confidence and entitlement do not grant authority.
- [ ] Define lock scope, permitted reductions/revocations, and authenticated unlock/recovery behavior; avoid accidental lockout.

## 7. Temporary delegation

- [ ] Bind actual agent, exact operation/resource/parameters, amount, destination/environment, max uses and expiry.
- [ ] Convert expiry labels to validated durations or timestamps.
- [ ] Authenticate, create grant through UCII, retrieve actual authority ID and validity.
- [ ] Recheck original action after grant; grant success is not execution authorization.
- [ ] Show real standing/temporary/expiring/consumed/expired/revoked state and scope.
- [ ] Enforce expiry and use limits server-side, atomically under concurrent requests.

## 8. Protected execution

- [ ] Add explicit protected execution orchestration/control where appropriate.
- [ ] Perform fresh UCII authorization immediately before consequential execution.
- [ ] Reject altered, revoked, expired, consumed or mismatched evidence independently.
- [ ] Use idempotency keys and bind them to exact actions.
- [ ] Define atomic reservation/consumption/release behavior for one-use authority.
- [ ] Return real executor receipts, result/status and provenance references.
- [ ] Treat uncertain timeouts as reconciling/unknown, not success or safe-to-retry failure.
- [ ] Retrieve execution status before retrying possible side effects.
- [ ] Prevent duplicate execution from double-clicks, retries, parallel requests and replay.

## 9. Revocation, activity and proof

- [ ] Retrieve actual grants and require explicit revocation target/scope; current request has no authority ID.
- [ ] Refresh authority after verified revocation and invalidate affected pending paths.
- [ ] Keep identity intact.
- [ ] Check same action again and show fresh denial proof.
- [ ] Retrieve real chronological activity, server-backed filters and pagination.
- [ ] Add View decision / View proof.
- [ ] Summarize principal, exact action, policy/delegation, decision, execution and timestamps; technical identifiers/evidence underneath disclosure.
- [ ] Keep local diagnostics separate from UCII provenance.
- [ ] Minimize conversational content and exclude secrets from stored evidence.

## 10. Acceptance evidence

No task is complete solely because a button changes color or a mocked response succeeds.

- [ ] Verified identities, no applicable authority: actual denial or policy-permitted approval requirement; executor does not run.
- [ ] Authenticated narrow grant: fresh authorization -> real execution -> proof.
- [ ] Consumed one-use grant: repeat request blocked.
- [ ] Revocation: same identity/action -> fresh denial.
- [ ] Different separately authorized operation succeeds after the earlier authority was revoked.
- [ ] Inside standing authority executes; approvable outside authority follows ceremony; prohibited operation stops.
- [ ] Wrong resource/destination/environment/value, altered action, stale policy and expired/invalid evidence block.
- [ ] Cancelled/failed approval leaves existing policy unchanged.
- [ ] Duplicate/concurrent requests cannot exceed uses or duplicate effects.
- [ ] Uncertain executor timeout reconciles without blind retry.
- [ ] Backend outage fails closed without fabricated denial/authorization/provenance.
- [ ] Reload restores real backend state; no draft becomes authority.
- [ ] Product entitlement never substitutes for action authority or HUMAN governance.
- [ ] Mobile, keyboard, focus management, dialogs and reduced-motion behavior remain usable.

Preserve the canonical sequence in design-build.md: correct authority engine and repeatable lifecycle first, real Alexa+/MCP integration afterward. For UI integration slices: connection/identity -> canonical action/decisions -> approval/grants -> execution -> revocation/proof -> conversation. Confirm platform contracts before each dependent step. Do not expand into twenty shallow integrations.
