# Implementation Plan

## Workflow

Every implementation objective follows:

> inspect -> reason -> one bounded change -> targeted verification -> diff/review -> commit -> synchronized checkpoint

Avoid batching unrelated changes. Do not mark roadmap work complete until proof exists.

## Competition sequencing

- [ ] Finish and submit AssemblyAI by September 30 before beginning the Alexa+ implementation build.
- [ ] After AssemblyAI submission, promote Alexa+ to the highest-priority competition build.
- [ ] Alexa+ takes priority over the October 12-18 competition build.
- [ ] Preserve enough time before October 23 for adversarial testing, repeated demo rehearsal, friction/product-feedback completion, video production, and submission verification.

Planning and rule-preservation documentation may be updated before AssemblyAI submission, but do not split active implementation focus.

## Phase 0 — Foundation

- [x] Create standalone public repository.
- [x] Establish project concept and architectural boundary.
- [x] Establish hackathon requirement contract.
- [x] Start friction and product-feedback records before integration work.
- [x] Verify current official Alexa+ minimum MCP requirement: spec 2025-11-25 or later over Streamable HTTP for the self-hosted MCP path.
- [x] Record the official up-to-10% Stage 2 friction-log bonus and contemporaneous logging requirement.
- [ ] Reverify official Alexa+ resources immediately before implementation because hackathon requirements may change.

## Phase 1 — Minimal MCP boundary

- [ ] Establish supported language/runtime and dependency policy.
- [ ] Implement self-hosted MCP Streamable HTTP server using MCP spec 2025-11-25 or later.
- [ ] Expose one harmless diagnostic/read-only tool first.
- [ ] Prove Alexa+/simulation can invoke the MCP server.
- [ ] Record onboarding friction from the first implementation session and preserve supporting evidence.

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
- [ ] Demonstrate revocation -> denied on fresh check.
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
