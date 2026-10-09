# UCII for Alexa+

A simple conversation interface backed by real MCP and UCII identity, permissions and revocation.

**Use a tool. Set a boundary. Enforce it. Record what happened.**

## Current build
- Public UCII health works through the real MCP gateway without UCII sign-in.
- HUMAN login and agent signing are connected.
- Permissions shows only public health and one fixed staging artifact tool.
- Allow/Block management uses authenticated HUMAN approval inside protected controller custody. Oracle update and live acceptance are pending.
- Controlled tool invocation and durable Activity are next. No deployment capability is exposed.

The conversation is a bounded Alexa+ simulation. Official hackathon guidance accepts a custom frontend calling a real Streamable HTTP MCP server; actual Alexa+ developer tools are gated and unavailable to participants.

## Development
[Current plan](docs/implementation-plan.md) · [Friction log](docs/friction-log.md) · [Submission requirements](docs/hackathon-requirements.md)

Advanced exact-action approval work is retained, but is not required for the simple fixed-tool experience. Earlier plans are historical references, not additional implementation requirements.

License: [MIT](LICENSE).
