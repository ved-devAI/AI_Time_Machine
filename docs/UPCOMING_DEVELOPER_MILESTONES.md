# Upcoming developer-facing milestones

Status: M4.6, M5, and the narrow M5.1 trust hotfix are complete. The July 20
model audit also defined four ordered post-submission milestones. They must
preserve the API-free OrbitCart demo and the evidence rules in
`PRODUCT_CONTRACT.md`.

## M4.6 — Developer Workspace

Implementation status: Complete and verified. The local workspace is available
with `python3 -m app.cli serve --open`.

Objective: make Real Repo Mode feel like a usable local developer product
rather than a generic ingestion proof.

Required scope:

1. Add one-command local launch for the current repository and open the browser
   automatically when requested.
2. Add a visual **Review my branch** workspace backed by the existing change
   context engine. It must show the base and head revisions, changed files,
   range commits, recent history for those files, connected incidents or fixes,
   recorded risks, and missing evidence.
3. Replace OrbitCart-only prompts in generic mode with at least four adaptive,
   deterministic repository questions whose answers cite real events, commits,
   and files. Initial questions:
   - What changed recently?
   - Which files change together?
   - What parts of this branch have caused problems before?
   - Where is engineering rationale missing?
4. Keep OrbitCart's three validated questions and Bug Origin Trace unchanged.
5. Keep repository selection fixed when the local process starts. A browser
   request must not be able to select an arbitrary filesystem path.

The adaptive answers are evidence-engine output, not GPT output. The UI must
label them accordingly.

## M5.1 — Submission trust-integrity hotfix

Implementation status: Complete and verified July 21, 2026.

Objective: correct exposed trust claims and stale-cache behavior without adding
new product scope before the submission.

Required scope:

1. Replace broad `validated` UI wording with `reference-validated`,
   `citation-integrity checked`, or an equally precise term unless the claim's
   semantic entailment was independently checked.
2. Wrap optional live cached analysis in an envelope containing the evidence
   digest, model, generated time, and validated payload. Revalidate the digest
   and payload on every cache read.
3. Reject stale, malformed, or structurally incomplete caches and route to the
   safe fallback or a fresh explicitly enabled live request.
4. Stop assigning generic commits a blanket causal-looking 98% confidence.
   Present commit/diff existence, inferred classification, and missing rationale
   as separate dimensions.
5. Add negative tests for invented cross-field relationships, stale cache
   digests, malformed caches, and generic commits with missing rationale. Add a
   UI-copy regression proving the product claims reference integrity rather than
   textual entailment.

The validator cannot prove natural-language entailment merely by confirming
that an event, commit, and file exist. Until M8 adds evidence excerpts and
entailment evaluation, product copy must describe reference integrity accurately.

Exit criteria:

- No cached model output is returned without validation against current evidence.
- No UI or submission sentence claims that reference integrity proves every
  natural-language claim.
- `python3 scripts/verify.py` and the flagship browser flows remain green.

Completion evidence: 51 application tests, the OrbitCart regression test, both
artifact validators, the 15-check grounding scorecard, desktop OrbitCart and
Real Repo Mode checks, and a 390 × 844 no-overflow Real Repo check all passed.

## M7 — Git history correctness

Implementation status: Post-submission, first product milestone after M6.

Objective: make branch, merge, rename, and historical-scope results match normal
developer expectations before adding live model breadth.

Required scope:

1. Compute branch changes from `merge-base(base, head)..head`. If a user wants a
   tip-to-tip tree comparison, expose it as a distinct, clearly named mode.
2. Ensure `changed_files` and `range_commits` describe the same branch scope.
3. Define merge evidence explicitly. Select and document first-parent,
   combined-diff, or per-parent behavior; never silently label a file-changing
   merge as `0 changed files`.
4. Divide connected problems into evidence before the branch point and events
   inside the selected range. The question "caused problems before" must cite
   only pre-branch history.
5. Follow renames across recent-file history and incident/fix connections, not
   only timeline overlap.
6. Add focused tests for diverged branches, merges, renames, root commits,
   detached heads, and empty branch ranges.

Exit criteria:

- Unrelated base-branch files never appear as feature-branch changes.
- Merge commits expose documented file evidence.
- "Before" and "in this range" cannot be conflated in answers or UI labels.

## M8 — Code-aware semantic grounding

Implementation status: Post-submission, after M7.

Objective: let the model reason from bounded code changes rather than relying
primarily on commit subjects, custom `Why:`/`Risk:` fields, and filenames.

### M8.1 — Stronger evidence contract

- Extract bounded diff hunks or deterministic semantic summaries with stable
  evidence IDs.
- Include old/new paths, line ranges, change type, and safe text excerpts while
  handling binary, generated, vendored, and oversized files explicitly.
- Bind each causal explanation and answer claim to exact evidence IDs.
- Validate the full schema locally, including field types, required text,
  certainty values, role order, origin/trigger/chain consistency, duplicates,
  and evidence ownership.
- Add adversarial tests where invented prose cites a real event and file.
- Add an entailment-oriented evaluation set separate from the curated OrbitCart
  expected-answer regression.

### M8.2 — Optional BYOK analysis

Objective: let a developer opt into a custom OpenAI-powered repository question
using their own Platform API key while keeping the zero-key experience complete.

Proposed local contract:

```bash
OPENAI_API_KEY=... python3 -m app.cli serve . --enable-ai
```

- The local server reads the key from `OPENAI_API_KEY` or a supported local
  secret store.
- The key is never committed, written to a repository file, returned by an API,
  inserted into browser JavaScript, logged, or included in an artifact.
- `GET /api/ai/status` may return only whether optional AI is configured, the
  selected model identifier, and whether the feature is enabled.
- `POST /api/questions` accepts the user's question, never an API key. It builds
  a compact evidence bundle on the fixed repository, calls the model from the
  local server, validates every cited evidence ID, and rejects or clearly labels
  unsupported claims.
- The endpoint is disabled unless the user explicitly starts the server with
  optional AI enabled.
- Rate limits, request-size limits, timeouts, cancellation, caching, and a clear
  cost notice are required.
- Cache entries include the evidence digest and are revalidated before reuse.
- Free-form questions remain bounded by the supported evidence schema.
- Failure falls back to deterministic repository actions; it must never make
  the core timeline unavailable.

Do not add a key field to the public hosted UI. A static browser application
cannot keep a Platform API key secret. A hosted proxy would transfer abuse,
billing, authentication, and secret-management responsibility to this project.

## M9 — Large-repository performance

Implementation status: Post-submission, after M7 foundations.

Objective: keep Real Repo Mode responsive and bounded on repositories much
larger and noisier than OrbitCart or AI Time Machine.

Required scope:

1. Add visible defaults for maximum commits, changed files, recent history,
   diff bytes, and co-change pairs.
2. Replace per-commit and per-file Git subprocess loops with batched extraction
   where Git supports it.
3. Cache immutable ingestion results by canonical repository, revision, and
   evidence-contract version.
4. Detect or configure generated files, vendored directories, lockfiles, and
   mass-format commits so they cannot dominate co-change results.
5. Stream or paginate the browser timeline instead of requiring complete
   reachable history in one response.
6. Add representative small, medium, and large fixtures with latency and memory
   budgets.

Exit criteria:

- Limits are visible rather than silently truncating evidence.
- A mass-change commit cannot cause unbounded pair generation.
- Repeated requests for an unchanged revision avoid redundant full ingestion.

## M10 — Repository connectivity and hosted boundaries

Implementation status: Post-submission, after the local evidence path is
correct, semantically stronger, and bounded.

### M10.1 — Reuse developer-owned Git authentication

Support a repository URL in the local CLI and delegate cloning to the user's
existing Git credential manager, SSH configuration, or authenticated GitHub CLI.
AI Time Machine must not read, print, or persist the user's token. Public
repositories need no authentication. Cloned repositories must have explicit
location, size, cleanup, and failure behavior.

### M10.2 — Later hosted GitHub App

If a hosted repository picker becomes necessary, prefer a GitHub App over a
broad OAuth app. Request only read-only metadata and repository contents for
repositories the user explicitly selects. Use short-lived installation tokens.

This hosted path requires work that is intentionally deferred:

- registering and operating a GitHub App;
- HTTPS callback and installation flows;
- CSRF state, sessions, token refresh, revocation, and secure secret storage;
- organization-owner approval and enterprise installation restrictions;
- safely cloning, isolating, limiting, and deleting private repository data;
- rate-limit handling, auditability, privacy terms, and incident response;
- preventing repository content from becoming instructions to the model.

GitHub authentication grants access to repository data; it does not replace an
OpenAI Platform API key and must remain a separate opt-in boundary.

## Priority and stop rules

1. Complete only the narrow M5.1 trust hotfix, then finish M6 submission.
2. Execute post-submission product work in this order: M7 Git correctness, M8
   semantic grounding, M9 performance, then M10 connectivity.
3. Do not delay the Build Week submission for BYOK or GitHub authentication.
4. Do not change the default public demo from deterministic OrbitCart.
5. Do not claim a live model call unless one ran successfully and the UI labels
   its source and model honestly.
6. Describe current validation as reference integrity, not proof of textual
   entailment.
7. Preserve strict evidence validation for deterministic and model-generated
   answers.
