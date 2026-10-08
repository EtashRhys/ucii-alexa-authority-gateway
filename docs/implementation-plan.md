# Implementation Plan

## Workflow

Every implementation objective follows:

> inspect -> reason -> one bounded change -> targeted verification -> diff/review -> commit -> synchronized checkpoint

Avoid batching unrelated changes. Do not mark roadmap work complete until proof exists.

## Competition sequencing

- [x] Finish and submit AssemblyAI by September 30 before beginning the Alexa+ implementation build.
- [x] After AssemblyAI submission, promote Alexa+ to the highest-priority competition build.
- [ ] Alexa+ takes priority over the October 12-18 competition build.
- [ ] Preserve enough time before October 23 for adversarial testing, repeated demo rehearsal, friction/product-feedback completion, video production, and submission verification.

Confirmed by Brad Phee on 2026-10-02: the AssemblyAI build is complete and officially submitted; Alexa+ is now the highest-priority competition build.

Planning and rule-preservation documentation may be updated before AssemblyAI submission, but do not split active implementation focus.

## Phase 0 — Foundation

- [x] Create standalone public repository.
- [x] Establish project concept and architectural boundary.
- [x] Establish hackathon requirement contract.
- [x] Start friction and product-feedback records before integration work.
- [x] Verify current official Alexa+ minimum MCP requirement: spec 2025-11-25 or later over Streamable HTTP for the self-hosted MCP path.
- [x] Record the official up-to-10% Stage 2 friction-log bonus and contemporaneous logging requirement.
- [x] Reverify official Alexa+ resources immediately before implementation because hackathon requirements may change.

## Phase 1 — Minimal MCP boundary

- [x] Establish supported language/runtime and dependency policy.
- [x] Implement self-hosted MCP Streamable HTTP server using MCP spec 2025-11-25 or later.
- [x] Expose one harmless diagnostic/read-only tool first.
- [x] Prove Alexa+/simulation can invoke the MCP server.
- [x] Record onboarding friction from the first implementation session and preserve supporting evidence.

## Phase 2 — UCII identity integration

- [ ] Integrate through public UCII SDK/API only.
- [ ] Bind the external agent/request to the required UCII identity evidence.
- [ ] Verify credentials/authentication as required by the selected flow.
- [ ] Fail closed on missing/invalid evidence.

## Phase 3 — Bounded authority

- [ ] Define one consequential demo operation.
- [ ] Require exact UCII authorization before execution.
- [ ] Demonstrate verified identity with zero authority -> denied.
- [ ] Demonstrate bounded authority grant -> allowed.
- [x] Demonstrate operation-authority revocation -> denied on fresh signed check (hosted acceptance 2026-10-08; execution remains blocked).
- [ ] Preserve attributable provenance for the sequence.

## Phase 4 — Alexa+ product experience

- [ ] Make authority outcomes understandable to the user without exposing secrets.
- [ ] Keep capability/identity/authority states visibly distinct.
- [ ] Add human approval only where the demo contract requires it.
- [ ] Ensure failures are coherent and safe rather than silent.
- [ ] Ensure the experience is a real agentic authority workflow, not a basic MCP wrapper around existing UCII APIs.

## Phase 5 — AWS Builder evaluation

- [ ] Select AWS service(s) only if they improve the application.
- [ ] Document exact integration and why it exists.
- [ ] Add cost/budget controls before sustained use.
- [ ] Verify qualifying implementation against official mini-challenge requirements.

## Phase 6 — Adversarial validation

- [ ] unauthorized tool invocation;
- [ ] revoked authority;
- [ ] stale authorization;
- [ ] wrong identity/credential;
- [ ] action outside delegated scope;
- [ ] fabricated model approval;
- [ ] prompt/remote-content attempt to bypass policy;
- [ ] replay/duplicate request where applicable;
- [ ] missing provenance/evidence;
- [ ] AWS/service failure behavior.

## Phase 7 — Submission

- [ ] Full regression.
- [ ] Public-repo secret scan.
- [ ] Setup reproduction from a clean environment.
- [ ] Complete product feedback.
- [ ] Complete contemporaneous friction log and verify entries satisfy the official optional bonus fields.
- [ ] Confirm mini-challenge eligibility.
- [ ] Record pre-existing UCII vs. hackathon-created work.
- [ ] Produce <=3 minute demo.
- [ ] Complete Devpost submission well before deadline.


## HUMAN lifecycle + Alexa+-scoped UCII entitlement

This project adopts the same reusable UCII HUMAN onboarding and governance architecture used by other UCII product integrations while keeping Alexa+ product state and economic entitlement strictly isolated.

### Shared UCII lifecycle

`NEW USER → PRODUCT-SCOPED ECONOMIC ACCESS → HUMAN UCII IDENTITY → AUTHENTICATION/CREDENTIAL → GOVERNANCE → RECOVERY → AGENT DELEGATION → AUTHORIZATION → EXECUTION`

The HUMAN UCII identity is durable and portable. Alexa+ must not create a separate HUMAN identity merely because the participant also uses another UCII-enabled product.

Reusable lifecycle capabilities belong in UCII core: bounded controllers, controller expiry/rotation/revocation, credential recovery preserving identity, fail-closed recovery, lockout protection, and pre-established succession/incapacity handling. Alexa+, voice interpretation, an LLM, challenge possession, payment, or entitlement must never become a governance authority root.

### Alexa+ entitlement isolation

Alexa+ economic access must use its own product-scoped entitlement. It is not a general "free UCII" property of the HUMAN identity and is not interchangeable with an entitlement issued for another integration.

`HUMAN UCII IDENTITY = portable`

`ALEXA+ ENTITLEMENT = Alexa+-only economic access`

`OTHER PRODUCT ENTITLEMENT = separate capability`

`GOVERNANCE / DELEGATED AUTHORITY = separate from all entitlements`

A valid Alexa+ entitlement may satisfy only the economic gate for explicitly approved UCII operations required by Alexa+. It must be bounded by the participant/credential, an explicit Alexa+ product/service identifier, allowlisted UCII HTTP method+path operations, validity/expiry, and independent revocation.

The same entitlement presented outside Alexa+ scope must be rejected and normal UCII economic policy/x402 applies where applicable.

### First-use economic bootstrap

Because normal service-entitlement proof is credential-bound, a participant who has no UCII identity/credential cannot yet create that proof. Alexa+ therefore requires a separate narrowly bounded enrollment capability for first use.

That enrollment capability must be minimum-scope, short-lived and/or single-purpose where appropriate, non-transferable, usable only for the exact Alexa+ enrollment surface, and incapable of creating authentication, governance, delegated authority, authorization, revocation authority, or execution authority. A reusable anonymous free-UCII token is forbidden.

After successful participant establishment, the enrollment capability transitions out of the path and normal Alexa+-scoped credential-bound entitlement is used.

### Required isolation proofs

Implementation must prove:

`VALID PARTICIPANT + VALID ALEXA+ ENTITLEMENT + ALLOWED ALEXA+ OPERATION → ECONOMIC GATE SATISFIED`

`SAME PARTICIPANT + SAME ALEXA+ ENTITLEMENT + NON-ALEXA+ OPERATION → ENTITLEMENT REJECTED`

It must also prove that entitlement never substitutes for authentication, HUMAN governance authority, delegated action authority, fresh UCII authorization, or execution permission.

Revoking Alexa+ entitlement must not revoke the HUMAN identity. Revoking Alexa+ delegated authority must not revoke product entitlement. Revoking entitlement must not create or remove governance authority.

This architecture is intentionally shared at the UCII-core level while Alexa+-specific entitlement and integration state remain isolated from every other product.


## Completed website UI foundation — 2026-10-02

Evidence: [published website](https://ucii-alexa-control.sportgen-ai.chatgpt.site), website source commit `3658f4be252f1ce0f6b69819b844f438b19b820b`, successful TypeScript check and production build recorded during creation. The user has reviewed the published visual result. This is completion of the frontend foundation only; browser interaction/accessibility and live security lifecycle acceptance are not yet verified.

- [x] Build and privately publish the UCII for Alexa+ visual interface from the supplied reference.
- [x] Implement Home, Authority, Activity, and Security / Identity navigation and page surfaces.
- [x] Implement local text request drafting, suggestion selection, editable operation/resource/environment, and cancellation.
- [x] Implement human-readable local policy editors and proposed-value review dialog.
- [x] Implement temporary-authority proposal dialog with resource, operation, expiry choices and one-use limit.
- [x] Implement identity/verification surfaces, connection dialog, and revocation/lock confirmation dialogs.
- [x] Implement activity empty state, filter selection controls, and separately labeled local connection diagnostics.
- [x] Establish browser/server adapter boundaries and an explicit 503 disconnected response without fabricated authorization or execution.
- [x] Add responsive layout rules, focus styles, semantic dialog attributes, and reduced-motion handling to source.
- [x] Pass TypeScript checking and production build; publish the resulting Site.

### Remaining frontend completion

These are implementation tasks as well as wiring and tests. Reuse the existing visual foundation rather than rebuilding it.

- [ ] Complete reusable AUTHORIZED / AUTHORIZATION_REQUIRED / DENIED decision cards and escalation choices.
- [ ] Complete live current-policy diffs, approval completion, durable/bounded policy choices and authority reduction workflows.
- [ ] Render actual identity, authority, connection, policy, execution and activity responses; replace fixed disconnected placeholders.
- [ ] Add protected execution/status and proof disclosure surfaces.
- [ ] Connect supported real conversation events and replace the default-operation draft behavior.
- [ ] Verify browser interactions, keyboard/dialog focus management, mobile layouts and accessibility.
- [ ] Wire and validate the full [website integration contract](website-ui-integration.md), including adversarial and repeatable end-to-end lifecycle tests.

The original Phase 2–4 security/product objectives remain unchecked because a UI shell does not establish verified identities, actual grants, execution, revocation or provenance. In design-build.md, the minimal four-area UI foundation (step 13) has been implemented ahead of the planned backend sequence; the full decision card (step 14) and integrated product experience remain pending.

## Website integration tracking — 2026-10-02

The existing [UCII for Alexa+ website](https://ucii-alexa-control.sportgen-ai.chatgpt.site) now has live MCP health, public identity retrieval, and agent credential verification. HUMAN login/sign-out, signed operation checks, protected operation-grant approval and an ACTIVE operation result have been verified. Revocation acceptance, exact-action constraints, execution, conversation and authoritative activity remain incomplete. Its source currently lives separately from this repository.

Follow [Website UI Integration Contract](website-ui-integration.md) for exact control mappings, response rendering, missing workflows, and acceptance evidence. Preserve the canonical order in [Design Build](design-build.md) and existing HUMAN governance / Alexa+-scoped entitlement requirements.

- [x] Inspect website source and document actual wiring gaps.
- [x] Record observed internal implementation friction separately from unobserved Amazon/AWS friction.
- [ ] Implement and verify the integration contract's unchecked tasks.
- [ ] Establish an explicit source synchronization/porting strategy before maintaining the website from this repo.
- [ ] Attach real lifecycle evidence before marking integration complete.


## Wiring checkpoint — 2026-10-07

Evidence and exact restart state: [October 7 wiring handoff](wiring-checkpoint-2026-10-07.md).

- [x] Correct the public UCII API hostname and edge-compatible health fetch.
- [x] Run the self-hosted MCP gateway persistently on Oracle, with HTTPS routing.
- [x] Invoke initialize, tools/list and tools/call from the website backend.
- [x] Establish separate HUMAN and integration AI_AGENT records using one-use product enrollment economic capabilities.
- [x] Retain identity provisioning responses in encrypted operator custody.
- [x] Retrieve both live public identity records into website cards.
- [x] Provision the agent's first ML-DSA-65 signing credential and operation-scoped service entitlement.
- [x] Run a separate protected signer with encrypted systemd credential delivery.
- [x] Verify a fresh agent signature through the public UCII verification API using a separate economic entitlement proof.
- [x] Connect website Verify agent credential to the real MCP tool and display fingerprint/check time with one-minute proof display expiry.
- [x] Fix overlapping card buttons; operator confirmed the layout.
- [x] Connect HUMAN login/sign-out and authenticated operation-grant review, with an independent root-owned one-use issuance permit.
- [ ] Secure application/gateway access before exposing approval, authority mutations or execution.
- [ ] Complete real delegation, policy, authorization decisions, revocation, execution and provenance/activity.
- [ ] Complete the conversational simulator and requested action interpretation.
- [ ] Prove strict product isolation and expiry/revocation policy for recurring service entitlements. Current model is identity + method/path scoped; issued_by labeling is not product enforcement.
- [ ] Preserve Oracle service configurations/scripts in reproducible deployment files.

UCII application traffic uses its public API. Operator provisioning reused existing UCII administrative modules; those imports are not in the gateway. Source remains split between the Sites repository and this gateway repository, with exact Site commits recorded in the handoff.


## Verified wiring checkpoint — 2026-10-08

This checkpoint distinguishes live acceptance from remaining production work.

- [x] Existing HUMAN account login resolves the original HUMAN identity through UCII.
- [x] Header-only public session endpoint tested; gateway and hosted login/sign-out verified.
- [x] Signed delegated operation check returns NOT_GRANTED with no execution.
- [x] Hosted Check authority renders real DENIED.
- [x] Separate encrypted Alexa controller custody reconciled against UCII.
- [x] Dedicated Alexa lifecycle process verifies HUMAN sessions independently and consumes exact root-owned one-use operator permits.
- [x] Unauthenticated local lifecycle, gateway and HTTPS approval requests rejected.
- [x] Authenticated approval with missing operator permit rejected.
- [x] Read-only database/provenance reconciliation confirms one committed ACTIVE operation grant and one consumed issuance permit.
- [x] Hosted fresh signed check confirms ACTIVE operation authority while proposed-action execution remains blocked.
- [x] Finish exact-record revocation and verify a fresh signed DENIED / REVOKED result (owner confirmed hosted flow 2026-10-08).
- [ ] Resolve misleading grant confirmation feedback; committed state was reconciled before retry.
- [ ] Enforce resource/environment, validity and usage constraints for actual protected actions.
- [ ] Connect a protected executor and durable user-facing provenance/activity.
- [ ] Connect supported conversation interpretation, clearly distinguish simulation from actual Alexa+.
- [ ] Complete recurring entitlement product isolation and remaining adversarial validation.

The one-use limit applies to grant issuance authorization, not execution of the standing authority. The grant is operation-scoped, persists until revoked, and does not establish resource/environment approval. No execution has been permitted or attempted. The current route is a verified integration milestone, not completion of the full production authority design.


### Sign-in duration follow-up — 2026-10-08

- [x] Implement 15-minute, 1-hour and 4-hour choices with a fixed server deadline and secure opaque browser cookie.
- [x] Reuse UCII token refresh behind the gateway; serialize rotation and protected authority requests without storing passwords or changing action authority.
- [x] Validate eight isolated gateway session tests and website TypeScript checks.
- [x] Separate the last retrieved active authority record reference from the one-minute permission check so revocation review remains accessible.
- [ ] Pull and restart the Oracle gateway; verify selected expiry and sign-out through the hosted website.
- [ ] Observe live token renewal and retention beyond one hour for the four-hour option. A restart or failed renewal ends the in-memory session early.

The next execution milestone still requires exact resource/environment binding and a protected executor. The previously revoked operation authority remains revoked; these login changes do not recreate it.
