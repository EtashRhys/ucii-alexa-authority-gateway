# Hackathon Requirements

## Event

**Build, Ship, Shape: Amazon Developer Hackathon 2026**

- Primary track: **Alexa+**
- Submission period: **August 31, 2026 at 10:15 AM PDT through October 23, 2026 at 12:00 PM PDT**.
- Submission deadline: **October 23, 2026 at 12:00 PM PDT / 3:00 PM EDT**.
- Public submission repository required unless the permitted private-repository judging path is used; this project intentionally uses a public repository.
- Working demo required.
- Demo video must be public, in English, and no longer than three minutes for judging purposes.
- Product feedback is required for each Amazon/AWS tool, API, or SDK used.
- Pre-existing projects must clearly identify the work built or significantly updated during the hackathon window.
- Building may begin now: the official submission period is already open.

The official Devpost rules and resources remain authoritative if this file ever conflicts with them.

## Project priority

- Finish and submit the AssemblyAI Voice Agent Hackathon project first.
- Immediately after AssemblyAI submission, this Alexa+ project becomes the next competition-build priority.
- The Alexa+ build takes priority over the October 12-18 competition build because of the substantially larger Alexa+ prize opportunity and the need for adequate build, rehearsal, friction-log, and submission time.
- Do not dilute the active AssemblyAI critical path with Alexa+ implementation before AssemblyAI is submitted unless a rules/eligibility preservation task is genuinely time-critical.

## Alexa+ implementation gate

The planned path is a **self-hosted MCP server**.

Current official Alexa+ requirements:

- implement **MCP specification version 2025-11-25 or later**;
- use **Streamable HTTP** for the self-hosted MCP path;
- include actual executable integration code/configuration;
- demonstrate the required Alexa+/MCP technology at runtime, not merely mention it in documentation.

The rules also permit an Agent Skill or a simulated Alexa+ experience, but this repository currently targets the stronger self-hosted MCP integration path. Reverify the official requirements immediately before implementation and again before submission.

Amazon's judging guidance explicitly treats a basic MCP wrapper around an existing API as an obvious idea. The project therefore must demonstrate a coherent agentic authority workflow rather than merely exposing UCII endpoints through MCP.

## Judging criteria

Stage 2 uses four equally weighted criteria:

1. **Tech Implementation**
2. **Design**
3. **Potential Impact**
4. **Quality of the Idea**

The demo and implementation must be engineered to compete across all four rather than optimizing only for technical correctness.

### Friction-log bonus

Amazon's current official rules state that friction logs can earn a **bonus of up to 10% to the final Stage 2 judging score**. During Stage 1 downselection, Amazon's internal review team assesses friction entries and passes a recommended bonus to the Stage 2 judging panel.

Therefore:

- friction logging begins with the first actual Alexa+/Amazon/AWS development session;
- entries are recorded contemporaneously;
- every entry remains factual and evidence-backed;
- useful workarounds and actionable suggestions are captured while fresh;
- friction is never manufactured or exaggerated.

## Prize strategy

Alexa+ Track 1st Place currently includes:

- **$25,000 cash**
- **$15,000 AWS Credits**
- meeting with the Amazon Developer team
- project feature on Amazon Developer channels

A project may win one track prize and one mini-challenge prize. AWS Builder and Open Source each currently offer **$5,000 cash + $5,000 AWS Credits** plus additional Amazon exposure/meeting benefits. Mini-challenge participation must be earned by genuine qualifying implementation; do not bolt on irrelevant technology merely for eligibility.

## Submission gates

Before submission, establish all of the following:

- [ ] Working Alexa+ track demo.
- [ ] Required Alexa+/MCP technology is present and exercised by code.
- [ ] Self-hosted MCP implements spec 2025-11-25 or later over Streamable HTTP.
- [ ] Public source repository contains all submission source, assets, setup instructions, and an open-source license.
- [ ] New/significantly updated hackathon work is explicitly documented.
- [ ] Demo video is <= 3 minutes and leads with the strongest proof.
- [ ] Product feedback covers every Amazon/AWS tool, API, or SDK actually used.
- [ ] Track and any mini-challenge selections accurately match the implementation.
- [ ] Friction log is complete enough to support the optional up-to-10% judging bonus.
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
