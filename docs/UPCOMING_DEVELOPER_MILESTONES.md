# Upcoming developer-facing milestones

Status: M4.6 complete on July 17, 2026. M6 and M7 remain post-submission. These
milestones must preserve the API-free OrbitCart demo and the evidence rules in
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

## M6 — Optional BYOK analysis

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
  local server, validates every cited event, commit, and file, and rejects or
  clearly labels unsupported claims.
- The endpoint is disabled unless the user explicitly starts the server with
  optional AI enabled.
- Rate limits, request-size limits, timeouts, cancellation, caching, and a clear
  cost notice are required.
- Failure falls back to deterministic repository actions; it must never make
  the core timeline unavailable.

Do not add a key field to the public hosted UI. A static browser application
cannot keep a Platform API key secret. A hosted proxy would transfer abuse,
billing, authentication, and secret-management responsibility to this project
and is outside the hackathon scope.

## M7 — GitHub connection

Objective: reduce setup friction for remote repositories without weakening the
local-first privacy model.

### First step: reuse developer-owned Git authentication

Support a repository URL in the local CLI and delegate cloning to the user's
existing Git credential manager, SSH configuration, or authenticated GitHub CLI.
AI Time Machine must not read, print, or persist the user's token. Public
repositories need no authentication.

### Later hosted step: GitHub App

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

1. Finish and verify M4.6 before attempting BYOK or GitHub authentication.
2. Do not delay the M5 submission for M6 or M7.
3. Do not change the default public demo from deterministic OrbitCart.
4. Do not claim a live model call unless one ran successfully and the UI labels
   its source and model honestly.
5. Preserve strict evidence validation for deterministic and model-generated
   answers.
