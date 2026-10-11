# Project concept — current build

Updated 2026-10-11.

**UCII for Alexa+** demonstrates personal control over agent tools through a compact conversation interface.

**Conversation is the interface. UCII is the control plane. Human authority always wins.**

## What the user experiences

Public requests return a real UCII health result, a clearly labeled sample recipe or a link to an external destination. Personal shopping-list requests require sign-in. Creating or changing a list additionally requires the agent's current shopping.list.edit permission.

The HUMAN can Allow or Block that permission. The same agent and request then succeed or are blocked according to fresh UCII evidence. Saved Activity records what happened. A second fixed staging artifact tool demonstrates the same control without deploying infrastructure.

## What is real

Self-hosted Streamable HTTP MCP, UCII HUMAN authentication, agent identity and protected ML-DSA-65 signing, delegated permission changes, independent checks, persistent named lists and Activity are implemented. Owner acceptance covers the working signed-out and signed-in flows.

## What is simulated or external

The Alexa+ conversation is a bounded frontend simulation using deterministic supported requests. It is not live Alexa hardware or a general LLM. Recipes are local samples. Maps and Amazon.ca requests open links; the application neither navigates nor purchases on the user's behalf.

## Delivery scope

The application is public with the existing single-owner login supplied privately to judges after an app-specific password change. Email registration and multi-user enrollment are outside this submission.

The earlier infrastructure-deployment and exact-action approval workflow is preserved as engineering history and backend capability, but is no longer the main product or required demo.

## Relationship to UCII

UCII means Universal Cryptographic Identity Infrastructure. It is pre-existing infrastructure. This repository contributes the Alexa-focused gateway, protected application services, tools, frontend integration and tests created or significantly updated during the hackathon. UCII remains authoritative for its identity, credential and permission facts. The agent cannot mint its own authority.

See [current plan](implementation-plan.md), [architecture](architecture.md) and [build breakdown](build-review-2026-10-11.md).
