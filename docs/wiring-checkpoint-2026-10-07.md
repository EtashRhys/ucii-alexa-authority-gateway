# Wiring checkpoint — October 7, 2026

Paused by Brad after successful hosted verification and layout acceptance. Resume the remaining website controls; preserve today's working integration.

## Accepted milestones

- Correct public UCII health connection and edge-compatible fetch behavior.
- Persistent self-hosted MCP gateway with HTTPS Streamable HTTP routing.
- Website performs actual initialize, initialized notification, tools/list and tools/call using protocol 2025-11-25.
- Separate HUMAN and integration agent enrollment using single-use product enrollment economic capabilities.
- Full provisioning responses retained in encrypted operator custody.
- Both website identity cards retrieve actual active UCII public records.
- Agent first ML-DSA-65 signing credential and operation-scoped economic entitlement provisioned.
- Separate protected signer with encrypted systemd credential delivery.
- Fresh credential signature plus separate request-bound economic proof accepted by the UCII verification API: HTTP 200, verified true, matching participant, ACTIVE.
- Same verification succeeded through the gateway MCP tool and hosted website control.
- Website shows the fingerprint and proof check time; displayed fresh-proof status expires after one minute.
- Identity-card buttons stack vertically with spacing; operator confirmed the fix.

## Website source checkpoints

The website remains in its existing separate Sites source repository.

- Identity wiring: ba530df71e161af335f6194229bd34032cbad5d9.
- Agent verification: d72f77c8da745dc255a7dd89a80752c6953074bb.
- Accepted button layout: 1a3655a0b734757db2121575c13b3bb027455a20.
- TypeScript checking and production builds passed for the functional changes; layout build passed.

This gateway repository contains the live diagnostic, identity retrieval and agent verification tool implementations. Terminal-installed service configurations still need to be preserved as reproducible deployment artifacts. Keep operational identity bindings and custody inventories private.

## Pending

- Human authentication: the HUMAN card remains unverified and Begin verification is not wired.
- Authenticated approval and protected application/gateway access before authority mutations or execution.
- Real authorization decisions, policy, bounded delegation, revocation and protected execution.
- Authoritative provenance/activity.
- Conversational simulator: conversation remains offline; local drafts are not Alexa interpretations.
- Strict recurring service entitlement product isolation, validity and revocation acceptance. Current entitlement model enforces identity plus method/path; issuer labels do not enforce product boundaries.
- Reproducible deployment setup and full end-to-end/adversarial acceptance.

Enrollment and first-credential provisioning already succeeded. Do not rerun those steps blindly on resume; use existing operator state.

## Alexa path

Official FAQ confirms participants should use a self-hosted MCP server and their own web simulator/front end; gated add-on developer tools and direct device/console integration are unavailable to participants.

Source, rechecked October 7: https://amazonappdev2026.devpost.com/details/faqs.

No actual Alexa device connection is claimed. No AWS integration was implemented today.

## Next session

1. Synchronize the documentation checkpoint and preserve deployed configuration.
2. Connect human authentication/approval and protected gateway access using established UCII contracts.
3. Wire the existing Proposed action check to actual UCII authorization and show denial without a grant.
4. Complete grant/revoke/execution/activity in bounded website-tested steps.
5. Complete the accepted conversational simulator flow.

Guardian and Voice integrations were not modified. This checkpoint schedules no background work.
