# Current implementation plan

Updated 2026-10-11. The working product scope is locked for submission preparation.

## Accepted build

Brad confirmed on 2026-10-11 that signed-out and signed-in requests work and the site looks and works as intended. This is owner acceptance, not a new automated or browser test by the documentation reviewer.

| Capability | Current state |
| --- | --- |
| UCII health | Real MCP request, available without UCII sign-in |
| Sample recipes | Public, locally defined pancake and tomato-pasta templates |
| Maps, Amazon.ca, UCII | Public outbound links; external services perform any subsequent action |
| Named shopping lists | Saved create/view/add/remove and list switching; owner accepted |
| Shopping edit permission | Separate UCII shopping.list.edit Allow/Block |
| Fixed artifact verification | Real MCP tool, protected fixed staging artifact, no deployment |
| Artifact permission | Separate UCII sandbox.artifact.verify Allow/Block |
| Activity | Saved list edits, tool results and permission history; owner accepted |
| HUMAN sign-in | Existing UCII account; selectable 15/60/240-minute session |
| Agent identity/proof | Server-bound AI_AGENT identity and protected ML-DSA-65 verification |
| Public identity privacy | Anonymous HUMAN retrieval blocked; personal results clear on account change/sign-out |

Named-list acceptance and the finished request/result interface were already recorded in the final October 9 friction entry; previous pending rollout wording is superseded. The last supplied Oracle transcript reports 61 tests passing at c7532fb; later shopping/named-list work records 68/71 local tests and owner acceptance. Do not relabel 71 as a newly observed Oracle run.

## Primary workflow

Home request/result workspace → public response or sign-in when needed → saved list/tool request → inline Allow/Block confirmation → current UCII permission check → result → Activity.

Only the configured authenticated HUMAN can manage permissions. Shopping reads require sign-in but remain available while edits are blocked. The artifact tool can be invoked without a HUMAN session, using the agent's current saved permission; invocation does not grant authority. Block revokes the corresponding permission.

No arbitrary operation, path, subject or deployment target can be selected through the fixed tool. Agent signing and protected controller custody remain independent of browser requests. Preserve Guardian and Voice isolation.

## Judge access decision

- Public Site remains available at https://ucii-alexa-control.sportgen-ai.chatgpt.site/.
- Judges use the existing app login, delivered privately.
- Brad will change the password to a temporary app-specific value at the laptop terminal. This has not happened yet.
- No judge email collection, signup, SMTP sender, verification-token service or multi-user provisioning is being built.
- Owner identity restrictions remain in place. Judges act as the existing demonstration HUMAN and share lists, permission changes and Activity.
- Do not put credentials in source, friction entries, screenshots or public submission text.
- Rotate the temporary password after judging.

The prior statement that an existing SMTP account had been selected was incorrect: Brad explicitly confirmed no email service is configured. Judge signup is removed from the current delivery plan, not implemented.

## Remaining work

- [ ] Change the app password at the laptop terminal.
- [ ] Supply credentials privately with the short judge walkthrough.
- [ ] Prepare the <=3-minute demo video, description and required feedback.
- [ ] Make the exact frontend source judge-accessible alongside this backend.
- [ ] Verify reproducible setup and preserve sanitized deployed gateway/signer/nginx configuration.
- [ ] Complete the submission checklist and final official-rule review.

The owner has already tested the signed-out/signed-in flows; no repeat test is required merely to close this documentation update. Recheck login after the password change.

## Outside current scope

Advanced proposals, exact approvals and deployment controls are absent from the main interface. Their backend code, records and tests remain for compatibility and history. Broad policy dashboards, purchases, live Alexa devices, paid LLM integration and AWS expansion are not required to finish this build. New capabilities require a concrete post-submission need.

[Build breakdown](build-review-2026-10-11.md) · [Friction log](friction-log.md) · [Submission checklist](submission-checklist.md)
