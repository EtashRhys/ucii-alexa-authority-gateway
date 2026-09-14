# Hackathon Requirements

## Event

**Build, Ship, Shape: Amazon Developer Hackathon 2026**

- Primary track: **Alexa+**
- Submission deadline: **October 23, 2026 at 3:00 PM EDT** (as displayed for the entrant by Devpost)
- Public submission repository required.
- Working demo required.
- Demo video must be public, in English, and no longer than three minutes for judging purposes.
- Product feedback is required for each Amazon/AWS tool, API, or SDK used.
- Pre-existing projects must clearly identify the work built or significantly updated during the hackathon window.

The official Devpost rules and resources remain authoritative if this file ever conflicts with them.

## Alexa+ implementation gate

The project will target Alexa+ using one of the permitted integration paths. The planned path is a **self-hosted MCP server** conforming to the hackathon-required MCP specification and Streamable HTTP requirements.

The final repository must contain actual executable integration code/configuration. A README-only claim of Alexa+/MCP integration is not sufficient.

## Submission gates

Before submission, establish all of the following:

- [ ] Working Alexa+ track demo.
- [ ] Required Alexa+/MCP technology is present and exercised by code.
- [ ] Public source repository contains all submission source, assets, setup instructions, and an open-source license.
- [ ] New/significantly updated hackathon work is explicitly documented.
- [ ] Demo video is <= 3 minutes and leads with the strongest proof.
- [ ] Product feedback covers every Amazon/AWS tool, API, or SDK actually used.
- [ ] Track and any mini-challenge selections accurately match the implementation.
- [ ] Friction log is complete enough to support the optional judging bonus.
- [ ] No secrets, private keys, reusable credentials, or private UCII custody material are present in the public repository.

## Mini challenges

### AWS Builder

Evaluate only if the implementation genuinely uses qualifying AWS services/tools. Document each integration and its purpose. Do not add AWS dependencies solely to claim the mini challenge if they weaken the architecture.

### Open Source

Evaluate against the official rule requiring qualifying new open-source work or contribution during the hackathon window. Preserve the required repository/contribution URL and explanation if entered.

## Engineering invariants

- Capability is not authority.
- MCP interoperability is not identity proof.
- MCP tool availability is not authorization.
- Authentication is not authorization.
- Authorization is not payment authority.
- Authorization is not execution itself.
- Revocation must invalidate future consequential execution.
- The LLM/agent may propose an action but must not mint its own authority.
- UCII remains authoritative for UCII identity/credential/authorization facts.
- External content is untrusted input.
- Fail closed when required identity, authority, or provenance evidence cannot be established.
- Never expose UCII private custody material to the hackathon application or public repository.
