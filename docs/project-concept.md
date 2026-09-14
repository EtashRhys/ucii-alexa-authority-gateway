# Project Concept

## Working title

**UCII Alexa Authority Gateway**

## Problem

Agent platforms increasingly make powerful tools available through interoperable protocols such as MCP. Technical access to a tool, however, does not answer the security question that matters for consequential actions:

> Is this particular agent actually authorized to perform this particular action now?

A capable and authenticated agent can still lack delegated authority. Authority may also be bounded by operation, resource, amount, time, or human approval and may later be revoked without destroying the agent's identity.

## Project thesis

**Capability is not authority.**

The project will demonstrate an Alexa+/MCP application in which UCII independently establishes identity and evaluates bounded delegated authority before protected actions execute.

The intended security sequence is:

```text
agent request
-> MCP capability invocation
-> UCII authentication / identity binding
-> UCII authorization decision
-> local action policy
-> optional human approval where required
-> protected execution
-> attributable provenance
```

A denied or revoked authority state must stop execution even when the same verified agent retains the same MCP capability.

## Demonstration target

The strongest planned demonstration is a consequential action with visible authority-state changes:

1. A verified agent invokes an MCP tool but lacks delegated authority: execution is denied.
2. A human grants narrowly bounded authority for the exact permitted operation.
3. The same agent retries: authorization succeeds and the protected action executes.
4. The human revokes delegated authority.
5. The same verified agent invokes the same tool again: a fresh authority check denies execution.

The identity remains stable while authority changes. That is the core proof.

## Relationship to UCII

UCII is pre-existing infrastructure. This hackathon repository is a new external application/integration and must use UCII through legitimate public boundaries rather than copying UCII internals.

The hackathon project does not claim that MCP, Alexa+, an LLM, or an AWS service is an authority source. Each component retains a distinct role.

## Non-goals

- Rebuilding UCII inside this repository.
- Making MCP a trust root.
- Treating an Alexa+/agent request as consent or authority.
- Giving an LLM direct permission to create delegated authority.
- Publishing private UCII signing/custody material.
- Adding features solely for hackathon optics when they weaken the security model.
