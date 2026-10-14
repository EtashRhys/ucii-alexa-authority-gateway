# UCII for Alexa+ integration

This application starts disconnected. No identity, policy, decision, execution or provenance is simulated.

`lib/authority.ts` is the browser service boundary. `app/api/gateway/route.ts` deliberately returns HTTP 503 until a verified server-side adapter is configured against the self-hosted authority gateway's published contract. The interface's dotted request names are internal adapter operations, not claims about existing UCII endpoints.

Adapter operations: health, identity.get, authentication.start, policy.propose, policy.lock, authorization.check, delegation.propose, revocation.request, activity.list. Map to supported public UCII /v1 interfaces only after validating the production contracts. Store credentials and custody material server-side. No direct DB access or private UCII imports.

The current version allows local action and policy drafts, connection attempts, navigation and review. Alexa conversation, authority mutation, proof retrieval and protected execution require backend integration. Drafts and diagnostics are transient and are not authoritative records.

Before enabling execution: retrieve bound verified principals; canonicalize the exact action; validate the UCII decision, signature, action binding, policy version, validity and consumption/revocation state on the gateway; perform a fresh authorization check immediately before execution. A string decision alone must never enable protected execution. Current UI has no executor control, deliberately.

Before enabling approvals: retrieve current policy/version, authenticate a human approval ceremony, apply a narrowly scoped change, then recheck the exact original action. Preserve identity when revoking authority. Retrieve provenance from UCII; never turn local UI events into proof.
