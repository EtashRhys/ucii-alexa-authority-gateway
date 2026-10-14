# Finished build review — 2026-10-11

> **2026-10-13 source-import addendum:** This is a historical review of the October 11 baseline, not the current repository inventory. The Sites v36 frontend was subsequently imported into this repository under [`frontend/ucii-alexa-control/`](../frontend/ucii-alexa-control/) on `main` (commit `fbd697e`). References below to missing frontend source and outstanding frontend packaging describe the earlier snapshot and are superseded by this addendum. Sanitized live configuration, custody dependencies and clean-room reproduction remain unverified. See [`docs/reproduction.md`](reproduction.md).

## Review basis

Backend baseline: main at efe0442cefc880fe72b434f33c3c46bbc8474b2d. Published frontend: public Site v36 at df8e53713e5046a8187fc03bfe28c07285f10ab1. Brad confirmed signed-out and signed-in requests work on October 11. Earlier live acceptance and tests are retained in the historical friction log.

This review updates documentation only. It does not change runtime behavior, identities, custody, UCII, Guardian or Voice, and does not establish a new live test run.

## Evolution of the project

| Phase | Scope | Disposition |
| --- | --- | --- |
| Early concept | Broad authority dashboard, categories such as purchases/calendar/smart-home/development, eventual Alexa integration | Archived concept/design; not current build tasks |
| Middle engineering | Infrastructure authority, canonical proposals, exact approvals, issuance permits, reservation and receipts | Implemented backend/tests retained; advanced controls removed from main UI |
| Current product | Compact supported requests, public health/recipes/links, saved named lists, two Allow/Block controls, Activity | Working build accepted by owner |
| Judge onboarding exploration | New HUMAN accounts, verified email, SMTP, per-user permissions/storage | Not implemented; removed from current plan |
| Final judge approach | Existing app login provided privately after password change | Decision made; password/handoff pending |

## Capability truth

| Capability | Implementation and access |
| --- | --- |
| Health | Real self-hosted MCP → UCII; no HUMAN login |
| Recipes | Two local labeled templates; public |
| Driving directions | External map link; public, no navigation execution |
| Amazon.ca requests | External search/deals links; no price comparison or purchase |
| UCII homepage/docs | External links |
| Named shopping lists | Existing HUMAN session; private saved storage; create/add/remove requires current shopping.list.edit |
| List viewing | HUMAN session; viewing remains available while edits are blocked |
| Fixed artifact check | Real MCP and protected fixed staging file; requires current sandbox.artifact.verify; no deployment |
| Permission changes | Existing authenticated HUMAN + protected controller custody; explicit Allow/Block |
| Activity | Owner-authenticated saved tool/list events and permission history |
| Agent proof | Fresh protected ML-DSA-65 credential verification; not a HUMAN device factor |
| Conversation | Deterministic bounded Alexa+ simulation; no general-purpose LLM/live Alexa device |

## Repository inventory

The inspected baseline contains **60 tracked files**: 14 gateway modules, 12 test files, 6 deployment artifacts, 1 smoke script, 4 visual assets, 20 documentation files, and 3 root files. The reconciliation adds review/archive documentation and removes the empty thumbnail placeholder; these baseline counts are intentionally not a final post-commit count.

### Backend modules

| File under gateway/ | Role |
| --- | --- |
| activity.py | Owner-validated retrieval of receipts, list events and permission history. |
| approval_routes.py | Retained advanced exact-approval HTTP routes; absent from main UI. |
| auth.py | Login, session handles, duration/rotation, owner checks and application adapters. |
| canonical_action.py | Immutable action canonicalization and digest binding for retained advanced proposals. |
| conversation_tool.py | Fixed staging artifact invocation, signed permission checks and durable result recording. |
| exact_approval.py | Retained controller-bound exact approval/status/revocation. |
| executor_evidence.py | Independent HUMAN/agent/current-authority evidence composition. |
| executor_service.py | Protected local IPC process dispatching tool, shopping, Activity and advanced execution requests. |
| lifecycle_service.py | Alexa-only controller custody and independently validated permission mutations. |
| proposals.py | Retained durable owner-bound canonical proposal lifecycle. |
| sandbox_executor.py | Retained exact-approval reservation/receipt/consumption and read-only reconciliation primitive. |
| server.py | Real FastMCP health, identity, proof, authority and artifact tools; HTTP auth integration. |
| shopping_list.py | Private SQLite named lists, one-time migration, replay-safe edits and transactional edit/event records. |
| tool_permissions.py | Two-operation HUMAN Allow/Block management; Block revokes only the relevant scoped permission. |

### Tests

| File under tests/ | Coverage |
| --- | --- |
| test_activity.py | Owner isolation and saved history retrieval |
| test_approval_routes.py | Advanced approval/revoke route gates and immutable bindings |
| test_auth_duration.py | Session deadlines, rotation, logout and owner/session requirements |
| test_canonical_action.py | Immutable canonical binding and ambiguous/changed scope rejection |
| test_conversation_tool.py | Allowed/blocked artifact results and no artifact read when blocked |
| test_exact_approval.py | Exact issuance/reconciliation/revoke, expiry, custody and session checks |
| test_executor_evidence.py | Fresh agent proofs and HUMAN/identity/operation rejection |
| test_executor_service.py | IPC bounds, unauthenticated rejection and caller-path/subject rejection |
| test_proposals.py | Durable snapshot, cancellation, idempotency, expiry and owner isolation |
| test_sandbox_executor.py | Receipt/single-use behavior, revocation/expiry, evidence loss and uncertain reconciliation |
| test_shopping_list.py | Saved edits, permission denial, named lists, migration and replay controls |
| test_tool_permissions.py | Scoped Allow/Block, controller/session confirmation and unrelated-operation preservation |

The last supplied Oracle transcript reports 61 tests passing at c7532fb. Shopping-list checkpoints record 68 and 71 local tests, with later owner acceptance. This documentation-only audit adds no tests and does not claim a fresh 71-test Oracle run.

### Deployment and diagnostics

| File | Purpose |
| --- | --- |
| deploy/install_proposals.py | Historical proposal route/storage installer |
| deploy/install_exact_approval.py | Historical exact-approval route/table setup |
| deploy/prepare_exact_approval.py | Operator-controlled exact issuance permit preparation |
| deploy/install_executor.py | Protected fixed artifact, executor account/configuration/unit setup |
| deploy/ucii-alexa-executor.service | Separate executor process boundary |
| deploy/ucii-alexa-lifecycle.service | Separate Alexa lifecycle/controller boundary |
| scripts/smoke_mcp.py | MCP initialize/list/call diagnostic |
| requirements.txt | Application dependencies; not a self-contained replacement for the installed UCII runtime |

Historical install scripts are not a fresh complete-machine setup guide. Do not rerun custody/enrollment/migrations blindly.

### Documentation and assets

| Path/group | Current purpose |
| --- | --- |
| README.md | Public overview, judge access and source-packaging boundary |
| docs/project-concept.md | Final product and real/simulated capability distinction |
| docs/implementation-plan.md | Accepted scope and actual remaining tasks |
| docs/architecture.md | Current component/access model |
| docs/website-ui-integration.md | Current frontend/backend route map |
| docs/design-build.md and visual-design-contract.md | Accepted compact UI; original visual concepts archived |
| docs/judging-strategy.md | Short shared-login judge walkthrough and video emphasis |
| docs/submission-checklist.md | Accepted build separated from incomplete submission packaging |
| docs/friction-log.md | Current resolution table and accurate access decision |
| docs/product-feedback.md | Evidence-based access/guidance feedback; no invented AWS use |
| docs/hackathon-requirements.md | Retained competition requirements; completed priority sequence corrected |
| docs/aws-cost-controls.md | Credit receipt recorded; spend/balance/integration not assumed |
| docs/wiring-checkpoint-2026-10-07.md | Explicitly historical deployment checkpoint |
| docs/engineering/* | Explicitly historical advanced exact-approval/executor checkpoints |
| docs/archive/* | Original architecture, design, implementation/integration, visual and friction history |
| assets/* | Four existing thumbnail/demo UI PNG/SVG files retained unchanged |
| docs/thumbnail.svg | Empty placeholder removed; real thumbnails are in assets/ |
| LICENSE | MIT license |

## Cleanup performed

- Replaced obsolete pending README/plan language with accepted capabilities.
- Removed email signup, SMTP, multi-user provisioning and registration from the delivery plan.
- Corrected the inaccurate “existing SMTP selected” claim without erasing its historical record.
- Kept original friction evidence in an archive and made current resolution status easy to read.
- Replaced broad visual/layout requirements with the accepted compact interface; preserved original concepts.
- Marked dated engineering/checkpoint next steps as historical.
- Updated the judge strategy to the current shopping-list and Allow/Block workflow.
- Removed only the empty SVG placeholder; preserved runtime code, tests, actual visual assets and records.

Retained advanced modules are still wired into service imports and have tests. Deleting them as a documentation cleanup would change runtime behavior; they are not redundant disposable files.

## Remaining work, not working-build failures

1. Change the app password at the laptop terminal; verify that new login.
2. Privately provide judges the link, temporary app credentials and walkthrough. Shared state is intentional; no individual judge enrollment/provenance is claimed.
3. Supply the exact frontend source and sanitized deployed configurations alongside the public backend; verify clean setup.
4. Complete the <=3-minute video, project text, official-rule review, feedback and submission fields.
5. Rotate the temporary password after judging.

The frontend currently remains in its separate Sites source repository. The GitHub tree has no app/ frontend source, complete gateway/signer service inventory, full nginx setup or clean-machine verification. Do not claim a standalone reproducible full application until those source/setup tasks are complete. This is a submission packaging gap, not evidence that the accepted live application is broken.

AWS credits have been received per Brad, but no qualifying AWS runtime integration is established. The app performs no spending or purchases. Live Alexa device access is not part of the chosen custom-frontend simulation path.

[Current plan](implementation-plan.md) · [Friction status](friction-log.md) · [Judge walkthrough](judging-strategy.md)
