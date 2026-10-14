# Submission checklist

Updated 2026-10-13. Working build accepted; frontend source imported; remaining deployment reproducibility work tracked separately.

## Completed / accepted

- [x] Hackathon registration and Alexa+ track selected.
- [x] AssemblyAI project submitted; Alexa+ promoted to build priority.
- [x] $150 AWS credit receipt reported by Brad; redemption/balance/expiry not independently checked here.
- [x] Public standalone backend repository and MIT license present.
- [x] Public working Site v36.
- [x] Real self-hosted Streamable HTTP MCP code and frontend protocol 2025-11-25 integration.
- [x] Existing HUMAN sign-in/sign-out and protected agent signing connected.
- [x] Public requests work signed out, per Brad's 2026-10-11 acceptance.
- [x] Signed-in requests work, per Brad's 2026-10-11 acceptance.
- [x] Saved shopping/named-list flow and Allow/Block accepted.
- [x] Fixed artifact Allow/Block, successful invocation and subsequent denial accepted.
- [x] Saved Activity and permission history accepted.
- [x] Current scope and friction status reconciled with the final compact build.
- [x] Judge access decision: existing app login; no registration/email collection.

## Judge handoff

- [ ] Change the app password to a unique temporary value from the laptop terminal.
- [ ] Verify login after that change.
- [ ] Supply Site URL, app login and short walkthrough privately.
- [ ] Record a plan to rotate the temporary password after judging.

## Repository / reproducibility

- [x] Include exported Sites v36 frontend source in this public repository at `frontend/ucii-alexa-control/` (import commit `fbd697e`).
- [x] Publish source layout, prerequisites and explicit verification limits in `docs/reproduction.md`.
- [ ] Preserve sanitized deployed gateway/signer/nginx configuration and setup prerequisites.
- [ ] Execute and record a clean-environment frontend/backend setup and full end-to-end verification; the documented instructions are not yet verified as reproducing the live deployment.
- [ ] Final full-repository/source-package secrets review.
- [ ] Clearly identify new/significantly updated hackathon work separately from pre-existing UCII.

## Submission materials

- [ ] Final official rules/FAQ review before submission, including MCP compatibility and deadline.
- [ ] Complete project description and public source links.
- [ ] Public English demo video <=3 minutes.
- [ ] Complete required product feedback for technologies actually used.
- [ ] Select factual friction entries; internal issues are not Amazon API failures.
- [ ] Confirm Open Source mini-challenge eligibility against official requirements.
- [ ] Enter AWS Builder only if a genuine qualifying AWS integration exists; none is established by this review.
- [ ] Confirm final track/mini-challenge fields and submit before the official deadline.

## Scope exclusions

Email signup/SMTP, multi-user onboarding, live Alexa device integration, paid LLMs, purchases, infrastructure deployment and advanced exact-approval UI are not current build tasks. Judges share one demonstration identity and state.

[Current plan](implementation-plan.md) · [Judge walkthrough](judging-strategy.md) · [Build breakdown](build-review-2026-10-11.md)
