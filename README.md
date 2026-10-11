# UCII for Alexa+

A working web conversation simulation backed by real self-hosted MCP and UCII identity, permissions and revocation.

**Use a tool. Set a boundary. Enforce it. Record what happened.**

## Current build — 2026-10-11

[Open the application](https://ucii-alexa-control.sportgen-ai.chatgpt.site).

- Public UCII health uses real MCP without UCII sign-in.
- Public sample recipes and external map, Amazon.ca and UCII links need no sign-in.
- Signed-in users can create, view and edit saved named shopping lists.
- The configured HUMAN controls Allow/Block for shopping-list edits and the fixed staging artifact tool. UCII checks agent permission independently; Block revokes the applicable permission.
- Activity shows durable tool results and permission history.
- UCII HUMAN login, selectable session duration and protected ML-DSA-65 agent proof are connected.
- Brad confirmed signed-out and signed-in requests work on 2026-10-11. No UI changes are required for judge signup.

The frontend is a bounded Alexa+ simulation, not a live Alexa device integration or general-purpose LLM. Artifact checks deploy nothing; shopping lists purchase nothing.

## Judge access

The page is public. Judges will use the existing app account, supplied privately with a temporary app-specific password after Brad changes it at the laptop terminal. No email signup, verification email, SMTP or multi-user onboarding is required for this submission. Shared login means shared lists, permissions and Activity; it does not provide individual judge identity.

## Project records

[Build breakdown](docs/build-review-2026-10-11.md) · [Current plan](docs/implementation-plan.md) · [Architecture](docs/architecture.md) · [Judge walkthrough](docs/judging-strategy.md) · [Friction log](docs/friction-log.md) · [Submission checklist](docs/submission-checklist.md)

This GitHub repository contains gateway/backend code, tests, deployment helpers and project records. The published frontend remains in its separate Sites source repository. Consolidating or providing judge-accessible frontend source and verifying clean setup remain submission tasks; do not claim this repository alone reproduces the full application.

Advanced exact-action approval work remains implemented and tested but is outside the current interface and required demo. Earlier plans are historical references.

License: [MIT](LICENSE).
