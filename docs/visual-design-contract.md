# UCII Alexa+ — Visual Design Contract

Status: **LOCKED VISUAL DIRECTION**

Date locked: 2026-09-18

This document preserves the approved visual concepts for the Alexa+ competition build. The original generated PNG masters must be committed unchanged when binary transfer is available. Do not replace them with approximate redraws.

## Asset 1 — Competition thumbnail / hero

Planned source asset:

`assets/ucii-alexa-authority-gateway-thumbnail.png`

Visual description:

A cinematic, high-tech promotional banner for **UCII for Alexa+** using a dark blue-and-gold palette, glossy depth, neon accents, and layered voice-wave/UI graphics. UCII branding and the primary Alexa+ message occupy the left side. A glowing Alexa+ smart-speaker sphere is the central product object. Floating conversational command bubbles communicate natural-language action. A glass authority panel on the right makes the security model immediately legible.

Locked messaging and concepts include:

- **A MORE CAPABLE ALEXA. A MORE SECURE YOU.**
- **THE POWER OF CONVERSATION. THE PROTECTION OF HUMAN AUTHORITY.**
- **HUMAN AUTHORITY ALWAYS WINS**
- **AUTHENTICATE — It's really you.**
- **AUTHORIZE — Only what you allow.**
- **EXECUTE — Secure and auditable.**
- **REVOKE — You stay in control.**
- Natural conversation
- Granular authority
- Real-world actions
- Full audit trail
- Productivity without compromise

The image establishes the product's premium visual identity: sophisticated, modern, cinematic, trustworthy, human-controlled, and technically serious.

## Asset 2 — Final judge-facing application UI

Planned source asset:

`assets/ucii-alexa-authority-gateway-demo-ui.png`

Visual description:

A cinematic widescreen dashboard for **UCII Alexa+** using the same dark navy/glassmorphic visual system, electric-blue illumination, restrained status colors, glowing panel borders, premium depth, and a central Alexa sphere. It is the reference design for the final working judge-facing application, not merely decorative concept art.

The UI must expose real build state and real UCII evidence wherever technically applicable.

### Primary screen regions

**Conversation panel**

- live/listening state;
- natural Alexa+ request;
- assistant response;
- waveform / microphone state;
- clear indication of finalized conversational input.

**Capability / action navigation**

Representative product surfaces:

- Chat
- Calendar
- Smart Home
- Development
- Infrastructure
- Web Search
- Knowledge
- UCII Actions

Only functions actually implemented in the final product may be represented as working capabilities. Decorative/example surfaces must never imply functionality that does not exist.

**Central product experience**

- Alexa+ as the conversational/action interface;
- premium visual focal point;
- message: **Do more (within my permissions).**

**UCII Authority Status**

The authority panel must be driven by real state and make the security boundary immediately understandable:

- authenticated/verified principal;
- identity context;
- controller/governance context where applicable;
- active delegated authority;
- exact scope/resource/expiry where applicable;
- recent authorization;
- ALLOW / DENY / PENDING / REVOKED state;
- grant/review/revoke controls only where backed by real protected lifecycle behavior.

**Four permanent pillars**

### AUTHENTICATE
Prove it is really the principal.

Reference functions:
- authentication;
- identity verification/binding;
- session/context binding.

### AUTHORIZE
Only what the principal actually allows.

Reference functions:
- action analysis/canonicalization;
- UCII policy enforcement;
- exact bounded authority;
- protected grant ceremony / step-up where required.

### EXECUTE
Take action only after genuine authorization.

Reference functions:
- fresh verified context;
- executor structurally gated behind UCII ALLOW;
- protected/deterministic execution;
- provenance / audit trail.

### REVOKE
The human remains in control.

Reference functions:
- exact delegated-authority revocation;
- immediate effect;
- no residual/stale authority;
- fresh post-revocation authorization returning DENY for the same now-unauthorized request.

## Locked judge-facing lifecycle

The strongest final demonstration remains:

```text
NATURAL ALEXA+ REQUEST
        |
        v
AUTHENTICATED PRINCIPAL
        |
        v
CANONICAL PROPOSED ACTION
        |
        v
NO APPLICABLE AUTHORITY
        |
        v
DENY
        |
        v
PROTECTED STEP-UP / BOUNDED GRANT
        |
        v
FRESH AUTHORIZATION
        |
        v
ALLOW -> EXECUTE
        |
        v
REVOKE
        |
        v
SAME REQUEST
        |
        v
FRESH DENY
```

The visual experience must make every transition obvious to a judge without requiring them to inspect raw JSON.

## Visual-state language

Preserve the visual language established by the approved concepts:

- dark navy / near-black base;
- glassmorphic panels;
- electric blue for the UCII/Alexa authority path and active interaction;
- green only for genuinely established/verified/success state;
- amber for pending, challenge, step-up, or review state;
- unmistakable high-contrast DENY / REVOKED state;
- premium restrained glow rather than visual clutter;
- strong typography and generous spacing;
- conversational experience remains visually central;
- technical evidence is available without turning the product into a developer-console wall of JSON.

## Product truthfulness rule

The final UI must never fabricate security state for visual effect.

If a panel says:

- VERIFIED — verification must be real;
- AUTHORITY ACTIVE — the exact delegation must exist;
- ALLOW — a fresh UCII authorization must have established it;
- EXECUTED — the protected executor must actually have run;
- REVOKED — the exact authority must actually be revoked;
- DENY AFTER REVOKE — it must be a fresh authorization result, not a replayed UI state;
- PROVENANCE — the displayed evidence must correspond to the actual lifecycle.

Mock/stub/demo-only components must be explicitly disclosed and must never impersonate UCII identity, authority, revocation, or judge-facing security state.

## Core product language

**Conversation is the interface. UCII is the control plane.**

**Alexa+ can understand what you want and invoke powerful tools. UCII determines whether the person, agent, or service actually has authority to make the requested action happen.**

**Understanding != authority.**

**Capability != authority.**

**Human authority always wins.**

## Asset preservation rule

The two approved generated images are source-of-truth visual references.

When the PNG masters are committed:

1. preserve the original bytes unchanged;
2. do not overwrite them with optimized, traced, compressed, or regenerated versions;
3. derive SVG/web/thumbnail variants separately;
4. keep this design contract alongside the masters;
5. implementation may refine responsive layout and accessibility, but must preserve the approved visual identity and authority semantics.
