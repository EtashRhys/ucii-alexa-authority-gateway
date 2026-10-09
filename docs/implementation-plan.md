# Current implementation plan

## Goal
Use connected tools through a clearly labeled Alexa+ conversation simulation. The HUMAN owner can Allow or Block controlled tools. UCII checks the saved permission on every invocation and records the result.

## Working and validated
- Public UCII health through real MCP, without sign-in.
- UCII HUMAN and agent identities, protected signing and owner login with selectable session duration.
- Fixed staging artifact verification through conversation; no infrastructure deployment.
- Owner-authenticated Allow/Block management saved in UCII.
- Live allowed artifact checks and subsequent denial after Block confirmed by the user.
- Saved tool results and permission changes displayed in Activity; refresh confirmed by the user.
- Oracle gateway suite: 61 tests passed.

## Main interface
Home, Sign In, Permissions, Activity and Security / Identity. Home shows the saved tool permission. Permission confirmation stays beside its controls. Successful conversation responses are green; blocked/error responses are red.

Advanced proposals, exact approvals, revoke/lock dialogs, unavailable deployment shortcuts and obsolete messages have been removed from the main UI. Historical backend capabilities and records remain intact. Block internally revokes the applicable permission; the user-facing flow is Allow/Block.

## Boundary
Only the configured authenticated HUMAN can change permissions. The agent cannot grant itself permission. The fixed tool accepts no arbitrary operation, resource, file path or subject. Permission is checked independently using protected agent signing. Recorded artifact checks do not deploy anything.

## Shopping list checkpoint
Owner-only saved shopping list implemented: add, remove and view. Edits use separate shopping.list.edit UCII permission; reads require HUMAN sign-in but remain available when agent edits are blocked. List edits and activity records commit together in private executor storage. No purchases or Amazon account integration. Existing HTTPS authority route and services are reused. User confirmed the initial shopping list and Allow/Block flow works on Oracle. Named-list extension implemented with one-time transaction migration preserving existing items/history; 71 local tests passed. Oracle rollout and named-list acceptance are pending. Compact frontend now uses request/result panels, a saved-list dropdown and its own inline permission card. Recipe examples are local labeled templates; directions open an external map link. They do not claim live Alexa access or navigation execution.

## Remaining presentation work
- Rehearse the concise demo: public health → Allow → artifact check → Block → denial → Activity.
- Finish the submission presentation and required hackathon materials.
- Add connected capabilities only when a concrete demo need warrants them.

## Alexa access
Participants do not receive the live Alexa+ toolkit/CLI/simulator. The hackathon accepts a self-hosted MCP server and web simulation. Our simulation is labeled and uses real MCP calls. Live Alexa+ access is not an unfinished integration task.
https://amazonappdev2026.devpost.com/details/faqs

## References
- [Friction log](friction-log.md)
- [Hackathon requirements](hackathon-requirements.md)
- [Historical implementation record](archive/implementation-history-through-2026-10-09.md)

Broad policy categories and deployment expansion are paused. Preserve Guardian and Voice isolation.

## Public judge accounts — in progress
- User made the Site public. Public health, recipes and outbound links remain available without UCII login.
- Published Site v35 stops anonymous HUMAN identity retrieval, checks returned identity against the authenticated session and clears personal results on account change/sign-out. Agent identity remains public. Homepage link now targets https://ucii.sportgen-ai.com/.
- Existing Oracle gateway/lifecycle/executor remain single-owner. Do not enable arbitrary users against shared Brad storage or agent-wide permission toggles.
- Required before judge signup: verified email flow with expiring single-use tokens and retry bounds; production SMTP sender; server-issued HUMAN identity/account; bounded demo entitlement issued only after verification; server-derived per-user list, permission and Activity ownership; two-account isolation checks.
- User selected an existing SMTP account. Sender/server configuration and delivery acceptance are pending; never request passwords or SMTP secrets in chat.
- Signup is not live. Do not present email entry, an unverified account or a successful UI form as verification or entitlement issuance.
