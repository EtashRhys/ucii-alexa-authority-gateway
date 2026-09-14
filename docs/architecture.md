# Architecture

## Boundary model

The project is an external UCII client and interoperability layer. It must preserve the separation between capability, identity, authority, human policy, approval, execution, and provenance.

```text
+-----------------------------+
| Alexa+ / simulation         |
| agent intent + interaction  |
+--------------+--------------+
               |
               v
+-----------------------------+
| Self-hosted MCP gateway     |
| tools + request validation  |
+--------------+--------------+
               |
               v
+-----------------------------+
| UCII public boundary        |
| identity / credentials      |
| authentication              |
| authorization               |
| provenance / economic       |
+--------------+--------------+
               |
               v
+-----------------------------+
| Local protected executor    |
| exact permitted action only |
+-----------------------------+
```

## Trust rules

1. An inbound MCP request is a request, not authority.
2. Agent/model interpretation may help produce a candidate action but cannot create authoritative permission.
3. UCII identity and credential evidence must be independently verified where required.
4. The executor must consume an authoritative authorization/approval result rather than trusting conversational text.
5. Consequential execution requires a fresh enough authority decision for the action being executed.
6. Revocation changes authority, not identity.
7. Provenance describes established facts and must not manufacture stronger state.

## Integration rule

UCII remains independently deployable and authoritative. The gateway communicates through public UCII SDK/API surfaces. Private database access, private service imports, custody bypasses, or direct secret sharing are prohibited.

## MCP role

MCP provides a standardized capability/interoperability surface. It does not, by itself, establish:

- real-world identity;
- UCII credential validity;
- delegated authority;
- human consent;
- payment authority;
- permission for consequential execution.

## Deployment principle

The MCP gateway is intended to be self-hosted. AWS integrations may support the hackathon application where useful, but no AWS component should silently become the source of UCII authority. Architecture and cost implications of each AWS dependency must be documented.

## Security posture

- fail closed;
- least authority;
- bounded grants;
- explicit revocation;
- no reusable secrets in logs;
- no private keys in the public repository;
- deterministic authorization boundary around consequential execution;
- attributable provenance for materially important transitions.
