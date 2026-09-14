# UCII Alexa Authority Gateway

Self-hosted MCP authority gateway for Alexa+ that gives AI agents cryptographically verifiable identity and bounded, revocable authority using UCII.

## Project status

This repository is the public engineering workspace for the **Build, Ship, Shape: Amazon Developer Hackathon 2026**. The primary track is **Alexa+**.

The project is intentionally being built as a separate application that integrates with UCII through public interfaces. UCII remains the authoritative identity and authorization infrastructure; this repository does not duplicate or replace the UCII core.

## Core principle

> Capability is not authority.

An Alexa+/MCP agent may have the technical capability to invoke a tool without having permission to perform the underlying consequential action. The gateway will demonstrate independent identity verification, bounded delegated authority, revocation, provenance, and fail-closed execution decisions.

## Planned architecture

```text
Alexa+ / simulated Alexa+ experience
            |
            v
Self-hosted MCP authority gateway
            |
            v
          UCII
 identity -> credentials -> authentication
          -> authorization -> provenance
            |
            v
     protected action/tool
```

## Hackathon scope

The submission is planned for the **Alexa+ track**, with evaluation of the **AWS Builder** and **Open Source** mini challenges where the final implementation genuinely satisfies their requirements.

Detailed engineering and submission contracts live in [`docs/`](docs/).

## License

This project is intended to be open source. See [`LICENSE`](LICENSE) once the repository foundation is complete.
