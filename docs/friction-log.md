# Friction Log

Record friction as it occurs. Do not manufacture or retroactively exaggerate issues for judging.

## Judging significance

Amazon's current official rules state that friction-log entries are optional but can contribute a **bonus of up to 10% to the final Stage 2 judging score**. During Stage 1 downselection, Amazon's internal review team assesses submitted friction-log entries and passes a recommended bonus to the Stage 2 judging panel.

Treat this as a first-class build artifact:

- record friction contemporaneously from the first Alexa+/Amazon/AWS development session;
- preserve concrete evidence such as error text, documentation references, setup steps, and workarounds where appropriate;
- keep entries factual, reproducible, and useful to Amazon's developer teams;
- do not manufacture friction or inflate severity;
- review the log before submission, but do not reconstruct it from memory at the end.

## Entry template

### YYYY-MM-DD — Short title

- **Product/tool/API/SDK:**
- **Task attempted:**
- **Steps taken:**
- **Expected:**
- **Actual:**
- **Severity:** low / medium / high / blocking
- **Workaround:**
- **Actionable suggestion:**
- **Evidence/reference:**

---

## Entries

The entries below concern the website implementation inspected on 2026-10-02. They are internal UI/integration issues, not established Amazon/Alexa+/AWS defects. No Amazon/AWS onboarding or API failure was observed in this session; do not present these entries as qualifying platform friction without independent evidence.

### 2026-10-02 — Website service adapter remains disconnected

- **Product/tool/API/SDK:** UCII for Alexa+ website; internal service adapter.
- **Task attempted:** Inspect whether the published UI is ready for real identity, authority and execution integration.
- **Steps taken:** Read lib/authority.ts, app/api/gateway/route.ts and app/page.tsx at website commit 3658f4be252f1ce0f6b69819b844f438b19b820b.
- **Expected:** A documented mapping from controls to verified backend contracts and renderable authoritative responses.
- **Actual:** Server adapter intentionally returns 503 INTEGRATION_NOT_CONFIGURED. Several call sites discard successful responses, and status labels remain fixed placeholders.
- **Severity:** blocking for real end-to-end operation; intentional disconnected behavior is not itself a platform defect.
- **Workaround:** Keep unavailable states truthful and protected execution disabled. Local drafting/review remains usable.
- **Actionable suggestion:** Implement the allowlisted adapter and normalized state rendering together; complete docs/website-ui-integration.md before claiming integration.
- **Evidence/reference:** Website source files above; [integration contract](website-ui-integration.md).
- **Status:** Open; no backend integration attempted or completed here.

### 2026-10-02 — Request text does not determine the drafted operation

- **Product/tool/API/SDK:** UCII for Alexa+ website; local request composer.
- **Task attempted:** Inspect action preparation for the different suggestion texts.
- **Steps taken:** Read operation initialization and propose() in app/page.tsx at the same website commit.
- **Expected:** A GPU discovery request does not silently become an infrastructure deployment action.
- **Actual:** operation initializes to infrastructure.deploy and is reused for every draft until manually edited; proposal preparation does not interpret the request.
- **Severity:** medium in the disconnected UI; must be corrected before real action integration.
- **Workaround:** Review/edit exact operation and resource; backend remains disconnected and no executor exists.
- **Actionable suggestion:** Require validated canonical action preparation or explicit operation selection, and clarify ambiguity before authorization.
- **Evidence/reference:** app/page.tsx operation state and propose(); integration contract section 4.
- **Status:** Open; documented, not fixed by this documentation change.


### 2026-10-07 — Oracle integration inspection lacks ripgrep

- **Product/tool/API/SDK:** Self-hosted Oracle development environment; internal UCII/Alexa+ integration tooling.
- **Task attempted:** Locate existing service-entitlement and enrollment implementations before wiring the website's economic access.
- **Steps taken:** Read live OpenAPI from localhost port 8000; inspect authorization request schemas; run a bounded source search under src, tests and docs.
- **Expected:** Source search returns existing implementation and documentation references.
- **Actual:** Shell reported `Command 'rg' not found`; the entitlement source search did not run. OpenAPI retrieval succeeded.
- **Severity:** low; source inspection is delayed, not a UCII runtime failure.
- **Workaround:** Use Python standard-library source scanning without installing packages. Follow-up execution is pending.
- **Actionable suggestion:** Provide a dependency-free inspection command or explicitly list optional development tools in setup instructions.
- **Evidence/reference:** User-provided Oracle terminal output, 2026-10-07 approximately 14:37–14:41 America/Toronto; UCII checkout dfea543.
- **Status:** Open pending fallback inspection.
- **Classification:** Internal development friction; no Amazon/Alexa+/AWS platform defect or qualifying bonus claim established.

### 2026-10-07 — Alexa+ runtime foundation is not yet deployed

- **Product/tool/API/SDK:** Internal Alexa+ UCII gateway deployment and website integration.
- **Task attempted:** Identify the existing backend to connect the published website.
- **Steps taken:** Check expected checkout, Alexa-named systemd services, live UCII API and gateway repository tree.
- **Expected:** Locate runtime implementation and supported contracts if already provisioned.
- **Actual:** /opt/ucii/ucii-alexa-authority-gateway was absent; no Alexa-named service was listed. Gateway repository main at 26a963508c501e128f54466a57378bdd880ceaee contained documentation/assets but no backend implementation. UCII service was active; supported public authorization routes were present.
- **Severity:** blocking for end-to-end website operation; missing implementation is not a platform defect.
- **Workaround:** Inspect reusable UCII and related-project implementations, then implement the gateway against verified public contracts. Keep disconnected website states truthful meanwhile.
- **Actionable suggestion:** Track gateway setup, website integration and runtime acceptance separately so a completed UI is not mistaken for a deployed backend.
- **Evidence/reference:** Oracle terminal inspection on 2026-10-07 approximately 14:35 America/Toronto; live OpenAPI and repository inspection; [website integration contract](website-ui-integration.md).
- **Status:** Open. No deployed gateway or completed lifecycle is claimed.
- **Classification:** Internal build/deployment gap; no Amazon/Alexa+/AWS platform defect or qualifying bonus claim established.

#### Session requirements recorded with these findings

Brad confirmed ownership of UCII and requires Alexa+-scoped entitlement usage to satisfy the economic gate without paying ourselves. Authentication, HUMAN governance, delegation and execution permission remain separate. Reuse relevant existing repositories and documentation rather than recreating established mechanisms. The grant request schema currently exposes identity_id, allowed_operations and granted_by; expiry, use limits and exact-action enforcement require source inspection before conclusions or changes.

### 2026-10-07 — Website health integration used the wrong hostname and unsupported redirect mode

- **Product/tool/API/SDK:** Sites-hosted website / Cloudflare Worker fetch; internal UCII connection adapter.
- **Task attempted:** Wire Connection details / Check connection to real UCII health.
- **Steps taken:** Publish a server-side health probe; compare Oracle local health and nginx routing; correct the URL to https://api.ucii.sportgen-ai.com/health; expose the caught error after the hosted check continued to fail.
- **Expected:** Render healthy UCII independently of unconfigured Alexa+, authority gateway and executor.
- **Actual:** The original ucii.sportgen-ai.com/health returned nginx 404; api.ucii.sportgen-ai.com/health returned 200 and {"service":"UCII","status":"healthy","version":"1.0.0"}. Hosted fetch then failed immediately with TypeError: Invalid redirect value, must be one of "follow" or "manual"; "error" is unsupported at the edge. Generic exception handling initially hid the cause.
- **Severity:** medium; blocked the first live website connection check.
- **Workaround:** Use the verified API hostname and redirect:"manual"; existing response validation rejects redirects as unhealthy. Record safe exception details instead of only a generic retry message.
- **Actionable suggestion:** Validate runtime-specific fetch options and surface diagnostic causes before repeating user tests.
- **Evidence/reference:** Oracle nginx/health output and user-rendered website error on 2026-10-07 around 14:59–15:05 America/Toronto. Website fix source commit 876fd5f93fddb8474918dcc0f22ed8c9d737cca4.
- **Status:** Fix built; publication and hosted user confirmation tracked separately. UCII runtime itself answered healthy; no end-to-end authority integration is claimed.
- **Classification:** Internal implementation / hosting-runtime compatibility friction, not an established Amazon/Alexa+/AWS defect.


## 2026-10-07 — Verified connection and identity enrollment

- Website health recovery confirmed by the operator: UCII online, then real MCP initialize/list/call succeeded through the public HTTPS gateway.
- Immediate HTTPS test after Nginx reload returned 404; subsequent local and public initialization both returned HTTP 200. No further routing change was required.
- No HUMAN or Alexa integration agent existed in the identity listing. Separate one-use, root-controlled product enrollment authorizations covered POST /v1/identity for product ucii-alexa without payment.
- HUMAN and integration AI_AGENT creation and subsequent retrieval succeeded. Full provisioning responses were retained using systemd encrypted credentials; controller material was not printed.
- systemd-creds reported that the host credential secret is on unencrypted media. Custody currently uses host encryption; this warning does not establish hardware-backed or encrypted-disk protection.
- Identity records alone do not establish credential possession, human authentication, delegated authority, or execution permission.
- Added a read-only MCP identity tool with server-configured bindings and explicit UNVERIFIED status. Oracle deployment and website identity wiring subsequently confirmed by the operator.
- These are internal integration observations, not claimed Amazon product defects.


## 2026-10-07 — Live identity cards and protected credential proof

- Operator confirmed both website identity cards retrieve active public records through MCP.
- Gateway restart initially produced HTTPS 502. Journal showed startup completed nine seconds after restart; later local identity call returned HTTP 200. Future deployment tests should wait for readiness.
- Agent first ML-DSA-65 credential and verification/execution economic entitlement provisioned using the existing UCII operator workflow. This grants no underlying action authority.
- Dedicated Alexa signer service and IPC group installed, with encrypted systemd credential delivery. Socket confirmed mode 660. Initial socket check at 492 ms was premature; startup completed after approximately five seconds.
- A fresh agent credential signature and separate request-bound entitlement proof were sent to POST /v1/credentials/verify. UCII returned HTTP 200, verified true, matching identity and fingerprint, status ACTIVE.
- Gateway live verification tool deployed; Oracle invocation and hosted website verification subsequently confirmed by the operator.
- Website publish packaging initially produced an empty archive; regenerated unchanged build packaging and deployment succeeded.


## 2026-10-07 — Hosted verification acceptance and card layout correction

- **Task:** Test the live Verify agent credential control and inspect its rendered card.
- **Expected:** Matching agent proof, fingerprint and time displayed without overlapping controls.
- **Actual:** Operator confirmed VERIFIED and matching fingerprint. Retrieve identity and Verify agent credential initially competed for horizontal space on the card.
- **Severity:** Low; visible layout defect, verification itself worked.
- **Fix:** Full-width vertically stacked card buttons, explicit spacing and wrapping; build passed, publication succeeded, operator confirmed the result.
- **Evidence:** Operator's rendered website text and visual feedback at approximately 16:17–16:22 America/Toronto; Site fix commit 1a3655a0b734757db2121575c13b3bb027455a20.
- **Status:** Resolved and user confirmed.
- **Classification:** Internal website layout friction.

## 2026-10-07 — Alexa developer-tool availability clarified

- **Task:** Determine whether Alexa+ device/console setup was needed before wiring.
- **Finding:** Official FAQ says gated add-on tools are unavailable to hackathon participants; a website acting as a real Streamable HTTP MCP client is an accepted simulated-experience path.
- **Resolution:** Build and test the actual MCP client/server integration now; label the future conversational surface accurately as a simulator. Do not claim an actual Alexa device connection.
- **Source:** https://amazonappdev2026.devpost.com/details/faqs (rechecked October 7).
- **Classification:** Documented platform access constraint and setup clarification, not an observed failed Alexa API call or fabricated Amazon defect.

## 2026-10-07 — Publication archive retry

- A layout publication archive was rejected as invalid/incomplete. Repackaging the unchanged successful build produced an accepted archive and successful deployment.
- Earlier identity publication similarly yielded a zero-byte archive. Preserve archive-size/contents verification in deployment workflow rather than retrying an empty artifact.
- Classification: Internal build/publication tooling friction; resolved for today's deployments.


## 2026-10-08 — HUMAN authentication integration

- Confirmed existing active HUMAN identity had no authentication account.
- Initial terminal prompt opened /dev/tty with r+ and failed because the device is non-seekable. Switched to read-only terminal input; failure occurred before enrollment mutation.
- Initial script imposed a 16-character password minimum beyond UCII's existing eight-character contract. Operator requested eight; corrected the script to match UCII.
- Registration HTTP request timed out after 30 seconds. Read-only reconciliation confirmed exactly one active linked account and healthy UCII. Registration was not repeated.
- Existing session validation took a token query parameter, creating URL/access-log exposure risk. Added a header-only /v1/auth/session endpoint in UCII, preserving compatibility routes. Five focused tests passed on Oracle; live unauthenticated request returned 401.
- Real login and header-based session resolution matched the existing HUMAN identity. No password or token was printed.
- Gateway browser login routes use a separate HTTP adapter, not MCP tools. UCII bearer tokens stay in server memory behind opaque 15-minute handles. Dedicated service entitlement coverage added for login economic access; no action authority granted.
- Gateway login/session/sign-out round-trip passed. Signed-out session returned 401.
- Nginx exact HTTPS login/session routes installed and validated. Public session request without authentication returned 401.
- Website login form, HttpOnly Secure SameSite cookie, session display and sign-out implemented. Hosted browser acceptance remains pending.
- These are internal implementation/runtime observations, not claimed Amazon product defects.


### 2026-10-08 — Hosted HUMAN session acceptance and authority-check scope
- Owner confirmed hosted login displays AUTHENTICATED on Security / Identity and Home, and sign-out returns SIGNED OUT. Password authentication is explicitly separate from cryptographic device proof and action approval.
- Reviewed UCII delegated authority router, request/response schemas and evaluator. The existing check verifies the bound agent credential and exact logical operation; resource and environment constraints are not evaluated by this endpoint.
- Added read-only MCP tool `ucii_authority_check`: internally generates and signs an operation challenge, verifies the returned identity/credential/operation and authority state, and always reports execution blocked. No authority grants, payments or execution are performed.
- Python compilation passed. Oracle live acceptance and website button wiring remain pending; no live authority outcome has been asserted.
