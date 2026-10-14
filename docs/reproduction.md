# Reproducing and inspecting UCII for Alexa+

Updated 2026-10-13. This guide distinguishes **source availability**, **local inspection**, and **full deployment reproducibility**. The frontend import is complete; full deployment reproduction has **not** been independently verified.

## Source inventory

- `frontend/ucii-alexa-control/`: exported ChatGPT Sites v36 web frontend, committed to `main` at `fbd697e` on 2026-10-13. Includes `app/`, `components/`, `lib/`, `public/`, `tests/`, package manifest and lockfile. The exported starter README and INTEGRATION.md include generic/historical scaffolding guidance; consult the current gateway documentation before interpreting the live application.
- `gateway/`: Python MCP, auth, lifecycle, executor, permissions, shopping lists and activity code.
- `tests/`: backend tests; `scripts/smoke_mcp.py`: MCP diagnostic.
- `deploy/`: selected service units and historical install helpers, **not** a complete deployment manifest.
- `docs/architecture.md` and `docs/website-ui-integration.md`: current documented integration model.

The live site is https://ucii-alexa-control.sportgen-ai.chatgpt.site/ . The public frontend is a bounded Alexa+ simulation; UCII-backed protected functions require independently deployed infrastructure.

## Safe source checkout and inspection

Prerequisites: Git; Node.js >=22.13.0 for the exported frontend; Python 3.11+ recommended for the backend; an isolated environment for dependencies. Do **not** copy live secrets or controller/signer credentials into the checkout.

```sh
git clone https://github.com/EtashRhys/ucii-alexa-authority-gateway.git
cd ucii-alexa-authority-gateway
git status --short
ls frontend/ucii-alexa-control/app
ls gateway tests deploy
```

### Frontend dependency and build inspection

The frontend's package manifest specifies `pnpm@11.25.0` and includes `pnpm-lock.yaml`. On a disposable machine with a compatible Node.js installation, use the package manager and commands from the exported manifest, for example:

```sh
cd frontend/ucii-alexa-control
corepack enable
pnpm install --frozen-lockfile
pnpm run build
```

**Not verified here:** these commands have not been executed against a clean environment in this review. The exported Sites/Vinext application may depend on hosting-specific configuration, generated artifacts or service bindings; a successful local build would not by itself demonstrate parity with the published site. Inspect `package.json`, `.openai/hosting.json`, and `scripts/` for platform-specific requirements before deployment. No claim is made that the site can be moved to independent hosting without adaptation.

### Backend dependency and test inspection

The tracked `requirements.txt` lists `mcp>=1.30.0,<2` and `httpx>=0.28,<1`. The gateway also integrates with an **existing UCII runtime** and protected service custody not bundled in this repository. On a disposable environment, dependency inspection and unit-test attempts can start with:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt pytest
python -m pytest tests -q
```

**Not verified here:** the commands may require additional UCII/runtime dependencies, configuration or fixtures. Prior documented results include 61 passing tests on Oracle at an earlier commit and later local checkpoints of 68/71 tests; those are historical results, not a fresh test run on the imported tree.

## Live deployment prerequisites not included

A faithful full-system reproduction requires a separately provisioned UCII identity/authentication/authority service; registered HUMAN and AI_AGENT identities; protected signer and controller custody; separately managed executor/lifecycle processes; private storage and migration state; reverse-proxy/TLS configuration; trusted service settings; and appropriately scoped test credentials. None of these should be reconstructed from guesses or committed as live secrets.

`deploy/` contains partial service units and historical installers. **Do not run installers, enrollment, custody or database migration scripts against a production host to test reproducibility.** Use an isolated environment and sanitized configuration samples once they have been prepared.

## Verification status

| Check | Status as of 2026-10-13 |
| --- | --- |
| Exported v36 frontend tracked in same public repository as backend | **Verified** (GitHub `main`, import `fbd697e`) |
| Gateway, tests and selected deployment artifacts present | **Verified** (repository inventory) |
| Signed-out and signed-in live flows | **Owner accepted** 2026-10-11; not rerun in this documentation pass |
| Fresh clean-machine frontend build | **Not verified** |
| Fresh backend test run against current tree | **Not verified** |
| Full self-hosted gateway + signer + UCII + frontend deployment | **Not verified** |
| Sanitized live nginx, signer and controller setup inventory | **Incomplete** |
| Complete source-package secret review after import | **Not verified** |

This guide is a factual starting point for reviewers, not a certification that a one-command install reproduces the deployed system. For the current supported demonstration, see [judge walkthrough](judging-strategy.md); for remaining work, see [submission checklist](submission-checklist.md).
