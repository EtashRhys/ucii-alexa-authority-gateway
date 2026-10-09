# Current implementation plan

## Goal
Use a configured tool normally. Let its HUMAN owner allow or block it. Enforce the saved UCII permission on every controlled invocation and record the result.

## Keep
- UCII HUMAN/agent identities, protected signing and HUMAN login.
- Real self-hosted MCP Streamable HTTP gateway.
- UCII standing operation authority and revocation.
- Simple conversation, Permissions, Activity and Security pages.

## Current capabilities
- Public UCII health: live MCP call, no UCII sign-in.
- Fixed staging artifact tool: simple authenticated Allow/Block management implemented; Oracle deployment acceptance pending.
- Advanced exact proposals/approvals: retained outside the primary workflow.

## Immediate checklist
- [x] Simplify Authority to Permissions; remove unconnected purchase/document/deployment policy forms.
- [x] Implement fixed-tool permission management in protected controller custody, owner HUMAN authentication and server-derived agent/operation.
- [x] Permit only sandbox.artifact.verify; leave other operations and historical revocations untouched.
- [x] Verify 56 isolated local tests; Site TypeScript passed.
- [ ] Pull/test/restart Oracle gateway and Alexa lifecycle; verify Allow → Block → Allow in the website.
- [ ] Connect the controlled artifact tool from conversation using current signed UCII authority. Do not require exact proposal issuance for this fixed harmless tool.
- [ ] Record and display durable action/denial history.
- [ ] Rehearse public check, allowed controlled request, HUMAN block and subsequent denial.

## Authority boundary
Only the configured HUMAN, authenticated independently inside controller custody, can save these tool permissions. The agent/model cannot change its own authority. This narrow fixed-tool change uses current HUMAN session plus protected controller proof; terminal one-use issuance permits remain for generic advanced grant routes. No arbitrary operations, file paths or subjects are accepted by the simple route.

## Alexa access
Official hackathon FAQ confirms actual Alexa+ toolkit/CLI/simulator access is unavailable to participants. Use our clearly labeled conversation simulation backed by real MCP. No hardware or AWS role onboarding needed. https://amazonappdev2026.devpost.com/details/faqs

## Evidence and history
Oracle 52 tests passed at c067b2c; executor enablement printed but final readiness output has not been supplied. New 56-test Oracle run and live permission acceptance remain pending.

- [Friction log](friction-log.md): contemporaneous implementation observations.
- [Hackathon requirements](hackathon-requirements.md): submission requirements.
- [Historical implementation record](archive/implementation-history-through-2026-10-09.md): superseded plans and checkpoints, not the current task list.

Deployment expansion, broad policy categories and extra AWS infrastructure are paused. Preserve Guardian and Voice isolation.


Current checkpoint: fixed staging artifact conversation tool implemented and locally verified (59 tests). Oracle rollout and Block → Allow → Block validation are next. No HUMAN sign-in is needed to invoke this harmless fixed tool under existing agent permission; permission changes remain owner-authenticated. Protected receipts are saved server-side. Durable Activity retrieval is now implemented; Oracle rollout and refresh validation are pending.

Activity checkpoint: owner-only saved artifact receipts and permission history implemented, compact frontend published; 61 local tests passed. Deploy gateway/executor update and verify records after refreshing the browser. Confirmation is inline in the permission card.
