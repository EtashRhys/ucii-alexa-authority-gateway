# Design Build

## Status

**Canonical product design and implementation sequence**

This document translates the frozen authority architecture in `docs/architecture.md` into the product experience and order of operations for the Alexa+ build.

Architecture defines what must be true. This document defines **how we build it and how the human experiences it**.

The build rule is:

> **Make the authority engine correct first, make the human interaction obvious second, connect Alexa+ third, and add visual polish only after the complete loop is repeatable.**

The UX rule is:

> **Alexa handles the conversation. UCII handles the authority. The human should see only the decision they need to make, while verifiable proof remains one click away.**

## Product experience

The finished experience has five jobs:

```text
UNDERSTAND
What does the human want?

DECIDE
Does Alexa+ already have authority?

DISCUSS
If not, what does the human want to do about it?

ENFORCE
UCII records and enforces the decision.

REMEMBER
If requested, the approved decision affects future situations.
```

The ordinary user must not need to understand UCII internals, cryptographic identifiers, policy JSON, or lifecycle mechanics.

## Phase 0 — Freeze the judged product

Before implementation, write and lock the exact judged demonstration. This is an acceptance contract, not an aspiration.

### Moment A — Ordinary autonomous action

The human requests something already inside the authority envelope.

Alexa+ performs it without unnecessary interruption.

UI:

```text
AUTHORIZED
Existing authority
```

This proves the system permits useful autonomy inside human-defined boundaries.

### Moment B — Authority boundary

The human requests something outside standing authority.

Alexa+ explains that additional authority is required.

The interface presents:

```text
AUTHORIZATION REQUIRED

Alexa wants to:
[exact action]

Current rule:
[why approval is required]

[ JUST THIS TIME ]
[ DISCUSS WITH ALEXA ]
[ CANCEL ]

Change future rule ▾
```

### Moment C — In-the-moment discussion

The human says:

> "Hold on, Alexa. Let's discuss this."

Alexa+ discusses the circumstances and proposes an exact adjustment.

```text
PROPOSED CHANGE

Current:
$25 autonomous limit

Proposed:
$75 for this merchant

[ JUST THIS TIME ]
[ REMEMBER THIS ]
[ REMEMBER UNTIL... ]
[ DON'T CHANGE ]
```

The human confirms through the required ceremony. UCII records the authorized change. A fresh authorization check occurs before execution.

### Moment D — Approved learning becomes visible

A later matching request is evaluated against the saved UCII policy.

If the prior human decision was saved as a durable rule:

```text
AUTHORIZED
Saved authority rule
```

Alexa+ may remember conversational preferences, but UCII policy—not conversational memory—is the source of execution authority.

### Moment E — Tighten authority

The human can narrow authority just as naturally:

> "Actually, ask me before doing that from now on."

Alexa+ proposes the exact restriction. The human confirms. UCII records it. A subsequent matching request now requires approval or is denied according to the new rule.

The system must prove that adaptation is not merely a path to giving the AI more power.

## Phase 1 — Define the minimal authority language

Do not begin with a universal policy language.

Define the smallest generic schema capable of proving the architecture:

```text
AuthorityPolicy

subject
operation
resource
category
destination
environment

constraints:
    amount_max
    cumulative_max
    max_uses
    valid_from
    valid_until

behavior:
    standing
    approval_required
    prohibited

step_up:
    none
    confirm
    credential
    trusted_device

persistence:
    one_time
    bounded
    persistent

granted_by
created_at
provenance
```

Not every operation uses every field.

The policy must be data-driven. Avoid hard-coded product logic such as `if amount > 25: ask_user()`.

## Phase 2 — Define the canonical action

Natural language must be converted into a structured action before authorization.

Example purchase:

```text
ACTION

subject:
    Alexa+ identity

operation:
    commerce.purchase

resource:
    Product XYZ

merchant:
    Amazon

amount:
    54.99

currency:
    CAD

quantity:
    1
```

Example infrastructure action:

```text
ACTION

subject:
    Alexa+ identity

operation:
    infrastructure.deploy

resource:
    selected application

environment:
    staging

version:
    exact artifact/version
```

Boundary:

```text
CONVERSATION
     ↓
INTERPRETATION
     ↓
CANONICAL ACTION
     ↓
AUTHORIZATION
```

UCII authorizes the canonical action, not raw conversational text.

## Phase 3 — Build the policy decision engine

Inputs:

```text
Human authority profile
+
Alexa+ identity
+
Canonical action
```

Outputs:

```text
AUTHORIZED
```

or:

```text
AUTHORIZATION_REQUIRED
requirement: confirmation | credential | trusted_device | configured mechanism
```

or:

```text
DENIED
reason: prohibited | outside scope | invalid evidence | other explicit reason
```

No consequential execution is required at this phase.

Target tests include:

- inside standing authority;
- exact boundary;
- outside authority;
- wrong resource;
- wrong merchant/destination;
- wrong environment;
- expired authority;
- consumed authority;
- revoked authority;
- prohibited action;
- missing policy;
- missing/invalid identity;
- malformed or ambiguous action.

Ambiguity fails closed.

## Phase 4 — Build temporary authority

Implement **Just this time** before durable policy adaptation.

A one-time approval creates narrowly bounded authority for the exact action:

```text
Alexa+ identity
+
exact operation
+
exact resource
+
exact amount/value boundary
+
exact destination/environment where applicable
+
max uses = 1
+
short expiry
```

Lifecycle:

```text
AUTHORIZATION_REQUIRED
        ↓
human approval
        ↓
temporary authority created
        ↓
FRESH AUTHORIZATION
        ↓
AUTHORIZED
        ↓
protected execution
        ↓
authority consumed
```

Test replay immediately. A consumed one-use grant cannot execute a second time.

## Phase 5 — Build persistent policy adaptation

Implement **Remember this rule** only after temporary authority is correct.

Durable changes use explicit policy versioning:

```text
CURRENT POLICY
      ↓
PROPOSED POLICY
      ↓
HUMAN-READABLE DIFF
      ↓
HUMAN CONFIRMATION
      ↓
POLICY VERSION N+1
```

Example:

```text
Policy v7
groceries:
    autonomous <= $25

        ↓ approved change

Policy v8
groceries:
    autonomous <= $75
```

Provenance records the transition without storing unnecessary conversational content or secrets.

## Phase 6 — Make narrowing first-class

Authority adaptation must support:

```text
EXPAND AUTHORITY
NARROW AUTHORITY
TEMPORARY EXCEPTION
PROHIBIT
RESTORE PREVIOUS POLICY
```

There is a deliberate safety asymmetry:

- expanding consequential authority may require stronger confirmation;
- narrowing/revoking authority should be immediate and easy where safely possible.

A human request to reduce authority must not require Alexa+ to agree with the human's risk assessment.

## Phase 7 — Human verification

Implement a legitimate protected human-verification boundary without attempting to build an entire production authentication ecosystem for the hackathon.

```text
Sensitive authority change
        ↓
HUMAN VERIFICATION REQUIRED
        ↓
configured authorization ceremony
        ↓
verified
        ↓
change permitted
```

Safeguards:

- never log authorization credentials;
- never expose credentials in provenance;
- never embed credentials in frontend source;
- Alexa+ cannot assert that verification succeeded;
- failed or abandoned verification changes nothing;
- do not use birthday/date-of-birth or readily discoverable personal information as the secret;
- do not describe a spoken PIN alone as strong MFA.

The architecture remains compatible with stronger trusted-device or cryptographic approval later.

## Phase 8 — Protected executor

The executor accepts only a canonical action backed by valid UCII authorization evidence.

```text
Canonical Action
+
UCII Authorization Evidence
        ↓
Protected Executor
        ↓
Real Action
```

No valid authority means no execution.

The executor must independently reject missing, stale, consumed, revoked, mismatched, or out-of-scope authorization.

## Phase 9 — Provenance with progressive disclosure

Proof must be available without turning the normal interface into a security console.

### Normal view

```text
✓ Alexa+ Verified

Authority
Groceries up to $75

Recent Action
Purchase — $54.99
AUTHORIZED
```

### First disclosure — View proof ▾

```text
AUTHORIZATION PROOF

Identity
✓ Alexa+ verified

Action
Purchase Product XYZ
$54.99

Authority
✓ Saved grocery policy
Limit: $75

Decision
✓ AUTHORIZED

Policy
Version 8

Time
1:42 PM

[ Technical details ▾ ]
```

### Second disclosure — Technical details ▾

May expose relevant:

- identity ID;
- credential fingerprint;
- policy ID/version;
- authority ID;
- authorization ID;
- UCII decision/evidence;
- cryptographic evidence where useful;
- provenance reference.

The hierarchy is:

> **Human meaning first. Technical proof underneath.**

## Phase 10 — Build the clean user space

Keep primary navigation deliberately small.

### Home

Conversation is visually dominant.

A compact authority panel shows only current essentials:

```text
UCII

Human       VERIFIED
Alexa+      VERIFIED

Authority   ACTIVE

Current action
──────────────
Purchase
$54.99

AUTHORIZED
```

### Authority

Human-friendly policy configuration:

```text
MY ALEXA AUTHORITY

Purchases
Alexa can spend without asking
[$ 25]

Daily limit
[$ 100]

New merchants
[ Ask me ]

Large purchases
[ Require verification ]

────────────

Infrastructure

Read status
[ Allowed ]

Deploy staging
[ Ask me ]

Deploy production
[ Strong approval ]

Delete production
[ Never ]
```

No policy JSON in the normal user experience.

### Activity

Simple chronological history:

```text
TODAY

1:42 PM
✓ Purchase $54.99
  Authorized by grocery rule
  View proof ▾

1:31 PM
● Grocery rule changed
  $25 → $75
  View proof ▾

1:29 PM
! Purchase required approval
  View proof ▾

12:04 PM
× Production deployment
  Denied
  View proof ▾
```

### Security / Identity

Quietly available rather than visually dominant:

```text
YOU
Human UCII identity verified

ALEXA+
UCII identity verified

Human verification
Configured

Authority policy
Version 8

Emergency controls
[ Revoke Alexa Authority ]
[ Lock Authority Changes ]
```

## Phase 11 — Build one consistent decision card

The authorization card is a core reusable UI component.

```text
┌──────────────────────────────────────┐
│ AUTHORIZATION REQUIRED               │
│                                      │
│ Alexa wants to purchase:             │
│ Product XYZ                          │
│ Amazon                               │
│ $54.99                               │
│                                      │
│ Your current autonomous limit: $25   │
│                                      │
│ [ JUST THIS TIME ]                   │
│ [ DISCUSS WITH ALEXA ]               │
│ [ CANCEL ]                           │
│                                      │
│ Change future rule ▾                 │
└──────────────────────────────────────┘
```

After discussion:

```text
Alexa:
Based on our discussion, I can propose:

Groceries from Amazon
Current: ask above $25
New: allow up to $75

How should I apply this?

[ JUST THIS TIME ]
[ REMEMBER THIS ]
[ UNTIL... ]
[ DON'T CHANGE ]
```

This component should be reused rather than inventing different approval experiences for every capability.

## Phase 12 — Safeguards for adaptation

Hard product invariants:

1. Alexa+ may propose authority changes but cannot commit them.
2. Silence is never consent.
3. Ambiguous conversation never expands authority.
4. Policy expansion requires explicit confirmation.
5. High-consequence changes may require stronger verification.
6. Temporary authority is enforced server-side and actually expires/consumes.
7. Approval for action/resource A cannot execute B.
8. Approval for one amount/value cannot silently expand to a larger value.
9. Approval for one destination/environment cannot execute another.
10. Consumed one-use authority cannot be replayed.
11. Explicit prohibition overrides lower-priority permissive authority.
12. A fresh authorization check occurs before consequential execution.
13. Conversation cannot downgrade a hard security floor.
14. Failed or abandoned approval leaves the previous policy intact.
15. Frontend state never substitutes for authoritative UCII state.

## Phase 13 — Add preference memory

Only after authoritative policy behavior is correct should preference learning be integrated.

Maintain a hard separation:

```text
ALEXA+ MEMORY
"What the human tends to prefer."

        !=

UCII POLICY
"What Alexa+ is actually allowed to do."
```

Memory may improve proposals:

> "You've preferred confirmation for unfamiliar merchants before. Would you like me to make that a rule?"

Memory never authorizes execution.

## Phase 14 — Integrate MCP / Alexa+

Integrate the real conversational/capability ingress only after the authority product works independently.

```text
Alexa+
   ↓
MCP Streamable HTTP
   ↓
UCII Alexa Authority Gateway
   ↓
Canonical Action
   ↓
UCII
   ↓
Protected Executor
```

Order:

1. implement/prove the required MCP transport/specification;
2. expose a harmless diagnostic/read-only tool;
3. prove Alexa+/approved simulation can invoke it;
4. connect the consequential demo operation;
5. verify the same UCII authorization boundary remains authoritative.

Alexa integration failures must not be confused with authority-engine failures.

## Phase 15 — Deterministic demo reset

Build repeatability before final visual polish.

One controlled **RESET DEMO** operation restores only known demo state:

```text
known identities
known baseline policy
no stale temporary authority
no consumed demo grant
no pending approval
known activity/provenance starting state
known demo resources
```

It must not become a general public lifecycle-authority endpoint.

End-to-end acceptance loop:

```text
RESET
→ autonomous action
→ authority boundary
→ discuss
→ temporary approval
→ execute
→ consumed
→ persistent policy change
→ matching action now autonomous
→ tighten rule
→ matching action now requires approval
→ prohibited action denied
→ proof available for every transition
→ RESET
→ identical result
```

Require repeated successful runs before polish.

## Phase 16 — Final visual implementation

Only after the complete loop is correct and repeatable should the approved cinematic Alexa+/UCII visual direction be fully implemented.

The primary screen must answer three questions immediately:

1. **What does Alexa+ want to do?**
2. **Does Alexa+ have authority?**
3. **What can the human do about it?**

Everything else uses progressive disclosure.

Normal user:

```text
AUTHORIZED
Saved rule
```

Interested user:

```text
View proof ▾
```

Technical user:

```text
Technical evidence ▾
```

Depth exists without clutter.

## Exact implementation order

Follow this sequence unless verified platform constraints require a deliberate change:

1. Freeze final demo acceptance contract.
2. Reinspect current UCII public interfaces and Alexa+ hackathon/platform requirements.
3. Define minimal authority-policy schema.
4. Define canonical-action schema.
5. Build and test policy decision engine.
6. Build one-use temporary delegation.
7. Build persistent/versioned policy changes.
8. Build narrowing, prohibition, and revocation.
9. Build human-verification ceremony.
10. Build protected executor.
11. Build provenance/evidence.
12. Build deterministic demo reset.
13. Build minimal Home, Authority, Activity, and Security/Identity UI.
14. Build reusable authorization/discussion decision card.
15. Add preference memory strictly separate from authority.
16. Integrate MCP/Alexa+ using a harmless tool first.
17. Connect the consequential demo action.
18. Run adversarial validation.
19. Run repeated end-to-end demo cycles.
20. Complete visual polish, genuinely useful AWS integration, documentation, video, and submission.

## Scope discipline

Do not build twenty capability integrations.

Build **one generic authority engine** and demonstrate several materially different behaviors through it.

The product may eventually govern:

- purchases;
- documents;
- smart-home actions;
- infrastructure;
- calendars;
- services and actions not yet anticipated.

The hackathon only needs enough implemented capability to prove that the **same generic authority architecture** can govern consequential actions without Alexa+ becoming its own authority source.

Every proposed implementation task should answer:

> **Does this materially improve the judged demonstration, the correctness of the authority architecture, the simplicity of the human experience, or the reliability/repeatability of the product?**

If not, backlog it.

## Final design principle

> **The technical system can be deep while the human experience remains simple.**

The human interacts with conversation, clear decisions, a small Authority settings space, a readable Activity history, and progressive proof disclosure.

UCII carries the complexity underneath.
