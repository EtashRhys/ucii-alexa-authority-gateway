# Friction log — finished build status

Reconciled 2026-10-11 against repository source, published Site v36 provenance, the retained build record and Brad's explicit signed-out/signed-in acceptance.

The [original chronological log](archive/friction-history-through-2026-10-09.md) is preserved intact. Earlier Open/Pending labels describe those sessions. This current summary supersedes them for delivery planning; it does not rewrite old observations or claim new tests.

## Current resolution summary

| Issue or constraint | Current status | Evidence / limit |
| --- | --- | --- |
| Disconnected website service adapter / absent gateway | Resolved for current capabilities | Real MCP and owner-accepted request flows; original October 2/7 gaps no longer describe the build |
| Request text silently mapped to infrastructure.deploy | Removed from current workflow | Deterministic supported requests; deployment/advanced proposal UI removed |
| Wrong health hostname / unsupported edge redirect mode | Resolved | Verified API hostname, manual redirects, owner-confirmed hosted recovery October 7 |
| Premature startup probes and temporary nginx 404/502 | Historical readiness friction | Later successful calls recorded; do not diagnose a current outage from old errors |
| Identity-card layout overlap | Resolved and later simplified | Owner accepted stacking/layout; primary UI now compact request/result panels |
| Empty/incomplete publication archive | Resolved for recorded deployments | Repackaging succeeded; v36 deployed |
| HUMAN account enrollment timeout | Reconciled | Exactly one active account confirmed; registration was not repeated |
| HUMAN token in session query URL | Header-based integration implemented | Gateway uses /v1/auth/session with Authorization; compatibility paths are not claimed removed |
| Empty local socket request crashed custody service | Bounded handling implemented | Alexa wrapper isolates invalid/disconnected clients; retained tests cover boundary |
| Login latency | User confirmed fast login after restart | Timings recorded; exact earlier root cause remains unproven |
| Permission controls / artifact invocation / Activity | Accepted | Saved Allow/Block, real invocation/denial and Activity accepted October 9 |
| Shopping server/frontend rollout mismatch | Resolved in owner acceptance | Initial list and named-list functionality subsequently confirmed October 9 |
| Named-list rollout and compact result UI | Accepted | Final October 9 entry confirms working functionality; Brad confirms current requests October 11 |
| Anonymous HUMAN identity retrieval / stale personal results | Fixed in v35/v36 source | Session gate and identity match; personal results clear on sign-out/account change; current overall flows owner accepted |
| Alexa toolkit/CLI/device/simulator access | Documented platform constraint | Custom frontend + real MCP is the chosen path; no gated toolkit/API test claimed |
| Oracle lacks ripgrep | Historical development limitation | Dependency-free searches used later; no claim ripgrep was installed |
| Judge email signup and SMTP | Removed from current scope | No email service configured; private shared app login chosen October 11 |
| Full source/setup reproducibility | Submission task remains | Frontend source is separate from backend GitHub repo; clean-install verification and sanitized deployed configs need packaging |

## 2026-10-11 — Final scope and judge access reconciled

- **Product/component:** Internal UCII for Alexa+ build records and judge handoff.
- **Task:** Align repository plans and friction status with the working compact application.
- **Observed:** Brad explicitly confirmed signed-out requests and signed-in requests work and the site looks and works as intended. Published Site is public, v36; source commit df8e53713e5046a8187fc03bfe28c07285f10ab1 matches the inspected frontend checkout.
- **Documentation friction:** README still described Activity/invocation as next work. The active plan still required SMTP, verified signup and multi-user isolation, and described accepted named-list work as pending.
- **Resolution:** Current docs now describe public requests, saved named lists, two scoped Allow/Block permissions, protected agent checks and durable Activity. Email signup requirements are removed; older broad design and chronological checkpoints are explicitly historical.
- **Judge plan:** Share the existing app credentials privately after changing to a temporary app-specific password at the laptop terminal. Judges share the existing demonstration HUMAN, lists, permissions and Activity; they are not individually enrolled.
- **Pending:** Password change and private credential handoff, frontend-source/setup packaging, video/submission materials. These are not unresolved failures of the working request flow.
- **Correction:** The October 9 statement that an existing SMTP account was selected was inaccurate. No email service is configured; no verification-email flow was implemented.
- **Verification limit:** This review did not rerun Oracle tests or perform a fresh browser sign-in. It records owner acceptance separately from prior test results: Oracle transcript reports 61 passing at c7532fb; shopping/named-list checkpoints report 68/71 local tests and later owner acceptance.
- **Classification:** Internal documentation/scope reconciliation. No new Amazon/AWS defect or qualifying bonus claim.

## Submission classification

Use the actual access/documentation constraint and supported simulator-path feedback where relevant. The nginx, edge-fetch, packaging, UCII authentication, rollout and UI issues are internal integration observations. Do not present them as Amazon API failures.

The historical log records successful milestones as well as friction; do not submit every milestone as a platform defect. Any potential bonus remains subject to official judging, with final rules to be reviewed before submission.

[Product feedback](product-feedback.md) · [Build breakdown](build-review-2026-10-11.md) · [Submission checklist](submission-checklist.md)
