# Judging Strategy

The product must be valuable independently of the hackathon. Judging strategy guides presentation; it does not override engineering truth or security boundaries.

## Tech Implementation

Prove, rather than merely describe:

- a real self-hosted Alexa+-compatible MCP integration;
- public-boundary UCII integration;
- independent identity/credential verification where required;
- bounded authorization around a consequential action;
- revocation followed by a fresh denial;
- provenance sufficient to explain the decision path;
- meaningful AWS integration if entering AWS Builder.

## Design

The user should be able to understand three distinct facts:

1. what the agent can technically do;
2. who/what the agent is cryptographically established to be;
3. what the agent is currently authorized to do.

Denials should explain the missing authority without encouraging bypasses. Grants should visibly communicate scope and expiry. Revocation should be immediate and understandable.

## Potential Impact

Frame the problem beyond a single Alexa demo: interoperable agents increasingly gain access to consequential tools, while capability discovery alone does not provide a portable authority model. UCII supplies a reusable identity/authority layer without requiring the capability protocol itself to become the trust root.

## Quality of the Idea

Avoid an ordinary API wrapper. The differentiator is a live authority-state transition around an unchanged agent and unchanged MCP capability:

```text
VERIFIED identity + NO authority       -> DENY
VERIFIED identity + BOUNDED authority  -> EXECUTE
VERIFIED identity + REVOKED authority  -> DENY
```

## Demo priority

The three-minute demo should lead with the observable security behavior, not architecture slides. Show the denied action quickly, grant narrowly, execute successfully, revoke, and prove the same request now fails. Explain the architecture after the proof is visible.

## Optional judging bonus

Maintain the friction log continuously. Record actionable product feedback while memories, error messages, onboarding steps, and workarounds are fresh rather than reconstructing them at submission time.
