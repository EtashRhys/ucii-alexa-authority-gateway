# Judge walkthrough and presentation

Updated 2026-10-11. The existing public application and shared app login are the submission experience.

## Access

Open https://ucii-alexa-control.sportgen-ai.chatgpt.site/. Public requests need no signup. Provide the existing app login privately after Brad changes the password at the laptop terminal. Judges do not submit their email or create an account.

Judges act as the same configured demonstration HUMAN and share saved lists, permissions and Activity. Permission events identify that HUMAN, not an individually verified judge. Credential handoff and password change are still pending.

## Short walkthrough

1. Signed out: ask “Check if my infrastructure is online”. Explain that this is a real UCII health check, not a deployment.
2. Try “Create a shopping list called Judge demo”. Sign-in is required for personal lists.
3. Sign in with the privately supplied app credentials.
4. Allow shopping-list edits through the inline confirmation or Permissions page.
5. Create the list, add an item and retrieve it. Show that it is saved and nothing is purchased.
6. Block shopping-list edits and repeat an edit. UCII blocks the change while list viewing remains available.
7. Open Activity to show the saved result and permission history.
8. If time permits, show the fixed artifact check and its separate Allow/Block permission; it deploys nothing.

Do not depend on the initial permission state: inspect it and set Block or Allow explicitly for the intended step. Shared judges may have changed the state already.

## Three-minute video

Lead with working requests, then show sign-in, Allow, saved edit, Block, denied edit and Activity. Briefly explain the independent HUMAN/agent/controller boundaries after the visible proof. Include the bounded Alexa+ simulation disclosure. Use the tested workflow; exact-action deployment proposals are not required.

## What to emphasize

- Technical implementation: real MCP and independently enforced UCII permissions.
- Design: compact request/result flow with minimal interruption.
- Impact: reusable human control over agent tools.
- Idea: the same agent/tool remains available while HUMAN permission changes execution.

The frontend is deterministic, recipes are samples, maps/Amazon requests are external links, and live Alexa hardware is not connected. Do not claim a qualifying AWS integration based on credits alone.

[Submission checklist](submission-checklist.md) · [Friction log](friction-log.md)
