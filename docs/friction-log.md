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

