# Current architecture

Updated 2026-10-13 (source-location correction; no runtime changes).

## Components

| Component | Responsibility |
| --- | --- |
| Sites web frontend | Compact request/result UI; public recipes and links; sign-in, lists, permissions and Activity adapters |
| HTTPS nginx boundary on Oracle | Routes /alexa/mcp and the existing authentication/authority endpoints to local services |
| gateway/server.py | FastMCP Streamable HTTP server on 127.0.0.1:8006; health, identity, agent proof, authority check, fixed artifact tool |
| gateway/auth.py | UCII password-login adapter, opaque server-held session handles, duration/rotation and authenticated application routes |
| Alexa protected signer | Signs fresh bounded agent challenges using separately held credentials |
| gateway/lifecycle_service.py | Independently validates configured HUMAN session and controller custody; grants/revokes the two fixed permissions |
| gateway/executor_service.py | Separate protected process; validates owner before personal storage; fixed tool checks, shopping lists and Activity |
| Existing UCII service | Authoritative identity, authentication, credentials and delegated authority; shared infrastructure remains separate |
| Private application storage | Named shopping lists and edit events in SQLite; artifact receipts and UCII permission history |

## Access and authority

Public health needs no HUMAN session. Public recipes and outbound links do not call a privileged agent action. The fixed artifact invocation uses current agent permission without requiring HUMAN login.

Personal list reads/edits and Activity require the configured HUMAN session. List creation and edits additionally require shopping.list.edit. Permission changes require independent HUMAN validation and protected controller possession. Artifact verification uses sandbox.artifact.verify. Block revokes the scoped permission.

The browser never supplies signer/controller secrets, trusted verification callbacks, arbitrary storage paths or agent identity. HUMAN password authentication is not a cryptographic device factor. Identity proof does not grant action authority.

## Retained advanced path

Canonical proposals, exact approvals, reservation/consumption and reconciliation remain in backend modules and tests. They are not the main UI or the current demo and must not be confused with the fixed-tool Allow/Block flow.

## Reproduction boundary

The backend and exported Sites v36 frontend now reside in this public repository: [`gateway/`](../gateway/) and [`frontend/ucii-alexa-control/`](../frontend/ucii-alexa-control/). The frontend import landed on `main` at `fbd697e` on 2026-10-13. The original published v36 source reference was `df8e53713e5046a8187fc03bfe28c07285f10ab1`. The export's local starter documentation may not describe the live wiring accurately. Complete sanitized deployment configuration, custody prerequisites and clean-environment reproduction remain unverified; see [reproduction](reproduction.md).

[Historical architecture](archive/architecture.md) · [Current integration](website-ui-integration.md)
