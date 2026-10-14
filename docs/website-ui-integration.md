# Current website integration

Updated 2026-10-13. Exported Sites v36 frontend is now in this repository at [`frontend/ucii-alexa-control/`](../frontend/ucii-alexa-control/) (import `fbd697e`); original published source reference: `df8e53713e5046a8187fc03bfe28c07285f10ab1`. The table below documents the owner-accepted live integration; do not assume every exported starter file reflects the deployed runtime without comparison.

| Frontend surface | Adapter / backend path | Access |
| --- | --- | --- |
| UCII health | /api/gateway → /alexa/mcp → ucii_health | Public |
| Public agent identity / proof | /api/gateway → MCP identity/verification tools | Public agent context; no permission issuance |
| HUMAN identity | /api/gateway → authenticated identity retrieval | Matching HUMAN session required in Site adapter |
| Sign in/out/session | /api/auth → /alexa/auth/login or /session | Existing UCII account; secure HttpOnly cookie carries opaque handle |
| Allow/Block | /api/permissions → /alexa/auth/authority → protected lifecycle | Configured HUMAN and explicit confirmation |
| Fixed artifact | /api/gateway → /alexa/mcp → ucii_artifact_verify → protected executor | Current agent sandbox.artifact.verify permission |
| Named shopping lists | /api/shopping → /alexa/auth/authority → protected executor | HUMAN required; shopping.list.edit additionally gates creation/edits |
| Activity | /api/activity → authenticated authority route → protected executor | Configured HUMAN; read-only retrieval |
| Recipe samples | Frontend local templates | Public; no generated/live recipe service |
| Driving directions / Amazon.ca / UCII | Frontend external links | Public; external destination handles subsequent interaction |

MCP adapter exercises initialize, notifications/initialized, tools/list and tools/call with protocol 2025-11-25. UCII bearer tokens remain in the gateway behind opaque session handles. Mutating Site adapters enforce origin checks and finite request shapes; missing required evidence blocks protected requests.

Lists are saved, not purchases. Artifact checks create evidence, not deployments. Recipes and links are accurately distinguished from real MCP tools.

Advanced proposal/approval routes remain in source for retained backend capabilities but have no controls in the current main interface.

No signup or email verification flow is required for judge access. Judges share the existing app identity after a password change and private credential handoff.

[Earlier broad integration contract](archive/website-ui-integration.md) · [Current plan](implementation-plan.md)
