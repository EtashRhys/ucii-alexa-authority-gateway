# Architecture

## Status

**Canonical build architecture — frozen for implementation planning**

This document defines the authority architecture for the Alexa+ hackathon build. It supersedes the earlier narrow `DENY -> GRANT -> ALLOW -> REVOKE -> DENY` concept as the complete product architecture while preserving that lifecycle as an important proof.

The project is an external UCII client and interoperability layer. UCII remains independently deployable and authoritative. Alexa+, MCP, the LLM, and the executor are never authority roots.

## Product thesis

> **Capability is not authority.**

> **Conversation is the interface. UCII is the personal authority layer.**

Alexa+ may understand a request and possess the technical capability to invoke a tool. Neither fact gives Alexa+ permission to cause the consequential action.

The human owns the authority policy. Alexa+ interprets intent. UCII evaluates and enforces authority. The executor performs only actions backed by valid UCII authorization.

## Core architecture

```text
                         HUMAN
                           |
             owns and configures authority
                           |
                           v
                +----------------------+
                | UCII AUTHORITY LAYER |
                |                      |
                | identity             |
                | authority policy     |
                | standing authority   |
                | temporary delegation |
                | prohibited actions   |
                | expiry / revocation  |
                | provenance / audit   |
                +----------+-----------+
                           |
                           | authoritative decision
                           |
HUMAN -- conversation --> ALEXA+
                           |
                    interprets intent
                           |
                           v
                 STRUCTURED ACTION REQUEST
                           |
                           v
                   UCII POLICY CHECK
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        AUTHORIZED   AUTHORIZATION_     DENIED
                     REQUIRED             |
             |             |              +--> STOP
             |             v
             |           HUMAN
             |      authentication /
             |      explicit approval
             |             |
             |      temporary bounded
             |         delegation
             |             |
             +<------------+
             |
             v
          EXECUTOR
             |
             v
        REAL ACTION
             |
             v
      UCII PROVENANCE
```

## Separation of responsibilities

### Human

The human is the source of personal authority policy.

The human can:

- define standing authority;
- define limits and scopes;
- require different authentication/approval ceremonies for different classes of action;
- approve case-specific exceptions;
- revoke delegated authority;
- prohibit operations;
- change policy as circumstances change.

Different humans can and should have different authority profiles. UCII supplies the enforcement machinery; it does not impose one universal risk tolerance or spending threshold.

### Alexa+

Alexa+ is the conversational and intent layer.

Alexa+ may:

- understand natural-language requests;
- gather context required to form a proposed action;
- canonicalize a request into a structured action;
- ask UCII whether that action is authorized;
- explain an authority decision;
- request the human ceremony specified by UCII;
- invoke the protected executor after authorization.

Alexa+ must not:

- decide how much authority it deserves;
- mint its own delegated authority;
- silently modify the human's authority policy;
- treat conversational confidence as authorization;
- bypass UCII because it believes an action is low risk.

### UCII

UCII is the authoritative control plane.

UCII owns and evaluates:

- identity and credential evidence;
- human-configured authority policy;
- standing delegated authority;
- temporary/case-specific delegation;
- operation and resource scope;
- value/amount constraints;
- destination/environment constraints;
- validity windows;
- maximum-use constraints;
- authentication/approval requirements;
- prohibited operations;
- revocation;
- consumption/expiry;
- attributable provenance.

### MCP gateway

The self-hosted MCP gateway exposes capabilities to Alexa+ and translates valid Alexa+/MCP requests into the canonical request format required by the UCII boundary.

MCP is an interoperability/capability protocol. It is not an identity proof, consent mechanism, or authority source.

### Protected executor

The executor is deliberately narrow and deterministic.

It must not execute a consequential operation merely because Alexa+ called it. Execution requires a valid authorization result/proof for the exact action being performed. The executor must fail closed when required evidence is absent, invalid, stale, consumed, revoked, or outside scope.

## Human authority profile

Each human has an independently configurable authority profile.

The profile is not a fixed global ladder. It is a set of human-selected policies for categories of action.

Illustrative examples:

```text
PURCHASING

<= $25
    standing autonomous authority

$25 - $250
    explicit human confirmation

$250 - $1,000
    authorization credential / step-up

> $1,000
    stronger human approval

> configured absolute limit
    prohibited
```

```text
DOCUMENTS

public
    standing authority

personal
    standing or session authority

confidential
    explicit approval

restricted
    prohibited
```

```text
INFRASTRUCTURE

status.read
    standing authority

staging.deploy
    confirmation / bounded delegation

production.deploy
    strong approval + one-use delegation

destructive production operation
    prohibited
```

These values are examples only. The human chooses the actual rules.

## Authority Settings interface

The Alexa+ product experience must include a human-facing **Authority Settings** surface.

It should allow the human to configure policy without understanding UCII internals. Examples include:

- autonomous spending threshold;
- daily aggregate limit;
- allowed merchants/destinations;
- document/resource classes;
- environment restrictions;
- confirmation requirements;
- step-up requirements;
- absolute prohibitions;
- default validity duration;
- maximum uses.

Changing a consequential policy is itself an authority-sensitive operation.

Alexa+ may interpret:

> "From now on you can spend up to $50 on groceries without asking me."

as a **proposed policy change**, but it must not apply the change directly. The proposal must pass the required human authentication/approval ceremony before UCII records the new policy.

## Canonical action request

Alexa+ converts conversation into a structured request before authorization.

Example:

```text
subject: Alexa+ identity
operation: commerce.purchase
resource: specific product
merchant: specific merchant
amount: 54.99
currency: USD
context: requested by human in active session
```

For infrastructure:

```text
subject: Alexa+ identity
operation: infrastructure.deploy
resource: selected application
environment: staging
requested_change: exact deployment
```

UCII authorizes the structured request, not the raw conversational sentence.

## Decision model

The authorization interface must distinguish at least three outcomes:

### AUTHORIZED

Applicable standing or temporary authority already permits the exact request.

Alexa+ may proceed to the protected executor using the required authorization evidence.

### AUTHORIZATION_REQUIRED

The request is not currently executable, but the human's policy permits a defined step-up path.

The response identifies the required ceremony, for example:

- explicit confirmation;
- authorization credential/PIN;
- trusted-device approval;
- another configured human-approval mechanism.

Alexa+ does not choose the ceremony. UCII policy determines it.

### DENIED

The request is prohibited, outside allowed scope, or otherwise has no permitted escalation path.

Alexa+ must stop.

This richer decision model prevents Alexa+ from becoming the risk engine while still allowing a natural conversational recovery path.

## Standing authority

Standing authority covers classes of actions the human has already chosen to delegate.

Example:

```text
subject: Alexa+
operation: commerce.purchase
category: groceries
amount_max: 25.00
daily_total_max: 100.00
merchant_scope: approved
validity: standing until revoked/changed
```

Alexa+ can act autonomously inside that envelope without repeatedly interrupting the human.

## Temporary / case-specific authority

A request outside standing authority may be approved without changing the standing policy.

Example:

```text
TEMPORARY DELEGATION

subject: Alexa+
operation: commerce.purchase
merchant: exact merchant
resource: exact product
amount_max: 600.00
max_uses: 1
expires_in: 5 minutes
granted_by: authenticated human
```

After successful execution, maximum-use consumption invalidates the delegation. If unused, expiry invalidates it automatically. Manual revocation remains available before either event.

A case-specific grant must be bound as narrowly as practical to the actual transaction. Approval for a $600 item must not become generic permission to spend $600 elsewhere.

## Automatic expiry and consumption

Time and use limits are first-class authority constraints.

A delegation may expire because:

- its validity window ended;
- its maximum-use count was consumed;
- the human revoked it;
- another explicit policy condition invalidated it.

Automatic expiry reduces the amount of forgotten standing privilege. It complements rather than replaces manual revocation.

## Human authentication / step-up

Consequential authority grants and policy modifications require the authentication ceremony selected by policy.

For the hackathon, a bounded authorization credential/PIN may be used as a demonstrable human-verification ceremony if implemented securely. It must not be logged or stored in plaintext.

A birthday, date of birth, or other readily discoverable personal fact must not be used as the secret.

The architecture must leave room for stronger trusted-device or cryptographic approval without requiring that entire production authentication system to be built for the hackathon.

Do not claim a spoken PIN alone is strong multi-factor authentication.

## Prohibited authority

Some operations may have no conversational escalation path.

Example:

```text
operation: infrastructure.production.destroy
policy: PROHIBITED
```

Alexa+ cannot turn that denial into authority by asking the user a simpler confirmation question. Changing the prohibition requires an authorized policy-change ceremony.

## Policy evaluation dimensions

UCII policy may evaluate a request using relevant dimensions such as:

- subject identity;
- operation;
- resource;
- resource classification;
- amount/value;
- category;
- merchant/destination;
- environment;
- time;
- cumulative usage;
- maximum uses;
- existing delegation;
- required authentication/approval;
- explicit prohibition.

Not every operation needs every dimension.

## Trust rules

1. An inbound Alexa+/MCP request is a request, not authority.
2. Agent/model interpretation may produce a candidate action but cannot create authoritative permission.
3. UCII identity and credential evidence must be independently verified where required.
4. The human defines their authority envelope; UCII enforces it.
5. Alexa+ does not assign its own risk or authority level.
6. Policy changes are themselves protected operations.
7. Temporary exceptions do not silently widen standing authority.
8. The executor consumes an authoritative authorization result rather than trusting conversational text.
9. Consequential execution requires a fresh enough decision for the exact action.
10. Revocation changes authority, not identity.
11. Expiry/consumption changes authority, not identity.
12. Provenance describes established facts and must not manufacture stronger state.
13. Missing, ambiguous, stale, or invalid required evidence fails closed.

## UCII public-boundary rule

UCII remains independently deployable and authoritative. This repository communicates through public UCII SDK/API surfaces.

Prohibited integration shortcuts include:

- direct UCII database access;
- private UCII service imports;
- custody bypasses;
- direct secret sharing;
- embedding UCII private keys in the Alexa+ application;
- allowing the MCP gateway to become an alternate authority database.

## Hackathon proof architecture

The hackathon does **not** need to implement every possible authority category.

It must implement enough of the generic architecture to prove that the behavior is policy-driven rather than hard-coded theater.

The target proof contains three materially different cases:

### 1. Inside the authority envelope

A low-consequence action already covered by standing authority:

```text
REQUEST
  -> UCII policy check
  -> AUTHORIZED
  -> protected execution
  -> provenance
```

### 2. Outside standing authority but approvable

A consequential action exceeds standing authority:

```text
REQUEST
  -> UCII policy check
  -> AUTHORIZATION_REQUIRED
  -> human step-up
  -> narrowly bound temporary delegation
  -> fresh UCII policy check
  -> AUTHORIZED
  -> protected execution
  -> delegation consumed/expired
  -> provenance
```

### 3. Prohibited / outside permissible authority

Alexa+ has the technical capability, but human policy prohibits the requested action:

```text
REQUEST
  -> UCII policy check
  -> DENIED
  -> no execution
```

The demonstration should also show that changing a user policy changes subsequent UCII decisions without changing Alexa+'s technical capability.

## Judge-facing lifecycle

The original grant/revoke proof remains valid but is now one part of the larger product:

```text
AUTHENTICATE HUMAN
        |
        v
CONFIGURE AUTHORITY ENVELOPE
        |
        v
ALEXA+ INTERPRETS INTENT
        |
        v
CANONICAL ACTION REQUEST
        |
        v
UCII POLICY CHECK
        |
        +--> AUTHORIZED ----------> EXECUTE
        |
        +--> AUTHORIZATION_REQUIRED
        |          |
        |          v
        |     HUMAN STEP-UP
        |          |
        |          v
        |   TEMPORARY DELEGATION
        |          |
        |          v
        |    FRESH UCII CHECK ----> EXECUTE
        |
        +--> DENIED --------------> STOP
```

Revocation and automatic expiry must both be demonstrable authority-loss mechanisms where included in the final demo.

## Demo repeatability requirement

Repeatability is a first-class engineering requirement, not a submission-week cleanup task.

Before visual polish, the implementation must have a deterministic demo reset/re-arm mechanism that restores a known safe state without manual UUID editing, stale authority bindings, one-off database surgery, or frontend fabrication.

The demo should be runnable repeatedly by the developer and, where appropriate, judges without granting the public application unrestricted lifecycle authority.

A reset must restore only the narrowly defined demo state and must never become a general public grant/revoke capability.

## Security posture

- fail closed;
- least authority;
- bounded grants;
- explicit revocation;
- automatic expiry/consumption where configured;
- protected policy changes;
- no reusable secrets in logs;
- no private keys in the public repository;
- deterministic authorization boundary around consequential execution;
- transaction/action-bound exceptions;
- attributable provenance for materially important transitions;
- no frontend-fabricated UCII state.

## Product language

**Capability is not authority.**

**Conversation is the interface. UCII is the control plane.**

**Alexa+ understands what you want. UCII determines what Alexa+ is allowed to make happen.**

**The human defines the authority envelope. Alexa+ operates autonomously inside it, requests additional authority at its boundaries, and stops where the human has prohibited action.**

**Human authority always wins.**
