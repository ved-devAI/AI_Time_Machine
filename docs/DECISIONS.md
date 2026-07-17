# Architecture decision log

## ADR-001 — Use a real curated repository

Status: Accepted — July 15, 2026

OrbitCart is generated as a genuine 12-commit Git repository rather than a
hard-coded UI fixture. This provides reliable demo storytelling while proving
that the product reads real commit and diff evidence.

## ADR-002 — Preserve evidence before interpretation

Status: Accepted — July 15, 2026

Git ingestion produces a stable event contract before any causal reasoning.
Interpretations reference existing event IDs, commits, and files. Model output
cannot create new evidence records.

## ADR-003 — Make the demo API-free by default

Status: Accepted — July 15, 2026

The user will not purchase Platform API usage for the hackathon. The primary
demo must therefore work offline after setup. An optional Responses API adapter
may remain, but the UI must identify whether an investigation came from a live
model, a validated Codex artifact, or the local evidence engine.

## ADR-004 — Use GPT-5.6 through Codex as a build-time collaborator

Status: Accepted — July 15, 2026

GPT-5.6 usage will be demonstrated through Codex-assisted architecture,
implementation, causal analysis, testing, review, and evaluation. The README
and video will document material contributions and the required Codex session
ID without claiming an API call that did not happen.

## ADR-005 — Optimize for one unforgettable investigation

Status: Accepted — July 15, 2026

The stale-price caching incident is the flagship flow. A polished causal rewind
with uncertainty and evidence is more valuable for judging than broad but
shallow repository features.

## ADR-006 — Commit a validated Codex analysis artifact

Status: Accepted — July 15, 2026

The primary investigation is generated at build time by GPT-5.6 Sol through
ChatGPT-authenticated `codex exec`, then committed as a versioned artifact. The
app accepts it only when its evidence digest matches the current OrbitCart
timeline and every causal stage cites the referenced event's real commit or
files. This makes GPT-5.6's contribution reproducible and visible without
requiring a Platform API key during judging.

The ChatGPT-authenticated Codex CLI rejected the generic `gpt-5.6` identifier in
this environment, so the reproducible command records the supported exact model
identifier `gpt-5.6-sol`. The UI and documentation retain that distinction.

## ADR-007 — Constrain Ask the Repo to three validated questions

Status: Accepted — July 15, 2026

The hackathon slice exposes three high-value repository questions instead of an
unbounded chat box. GPT-5.6 Sol generates the answer set through Codex at build
time. Runtime validation requires the exact question IDs and text, known event
IDs, each cited event's short commit, and at least one file changed by that same
event. This produces a reliable three-minute demo while preventing unsupported
prompts or attractive but fabricated citations from entering the interface.

The stale-price answer is labeled inferred at 98% rather than confirmed at
100%. Git proves which cache change preceded the incident and records its
missing invalidation path, but it does not prove deployment timing or identify
the first affected production checkout.

## ADR-008 — Make grounding quality executable

Status: Accepted — July 15, 2026

Artifact validation proves that references exist, while a deterministic
evaluation fixture proves that the flagship conclusions remain useful. The
scorecard locks the expected bug origin, trigger, causal order, calibrated
certainty, and required evidence events for all three repository questions. It
also runs negative cases for invented evidence, incomplete chains, unknown
events, and cross-event file citations.

The judge workflow must score 100% and exit non-zero on any regression. Stale or
malformed artifacts do not fail open: the runtime switches to a clearly labeled
local evidence fallback and never presents it as GPT output.

## ADR-009 — Deploy a validated evidence snapshot to static hosting

Status: Accepted — July 16, 2026

The local application continues to ingest the generated OrbitCart Git repository
at request time. The public hosting build runs that same ingestion during
deployment, validates the committed GPT-5.6 Sol artifacts against the resulting
evidence digest, and publishes only the validated JSON payloads with the frontend.

The hosted UI labels this mode `Git snapshot verified`. It does not claim live Git
ingestion or a live GPT-5.6 call. The public release is hosted at
`ai-time-machine-demo.vedheshvit.chatgpt.site`. This preserves an API-free,
zero-dependency judge experience while keeping every causal claim tied to real
event IDs, commits, and files.

## ADR-010 — Prove genericity with a local-first Real Repo Mode

Status: Accepted — July 16, 2026

M4.5 will add a local CLI that analyzes and serves an arbitrary Git repository,
plus branch or commit-range context for files a developer is about to change.
The proof case will be AI Time Machine analyzing its own history. OrbitCart
remains the deterministic flagship narrative and must not be weakened or
replaced.

The required workflow uses only Python and Git. Generic ingestion must not
assume structured rationale in commit bodies; absent reasoning is labeled `not
recorded`. An opt-in ChatGPT-authenticated Codex artifact is a stretch goal and
must retain strict event, commit, file, certainty, digest, and provenance
validation. GitHub OAuth, hosted repository access, editor integrations, and
autonomous modification remain outside the hackathon scope.

The selected repository and revision are fixed when the local server process
starts; HTTP requests cannot select arbitrary filesystem paths. Generic mode
reuses the normalized timeline UI but disables OrbitCart's committed Ask the
Repo and Bug Origin artifacts so validated evidence can never cross repository
boundaries. Conventional-commit classifications are stored as inferred
metadata, while the commit, subject, author, date, and diff-derived files remain
confirmed facts. Missing `Why:` and `Risk:` fields use the literal value `not
recorded`.

The range context engine resolves both endpoints to commits, diffs base against
head, and reports only history that touches the resulting changed files. The
required workflow was verified on an unstructured temporary repository and on
AI Time Machine's own M0-M4 history. The optional Codex question artifact was
not attempted because the API-free core satisfies M4.5 and the timebox reserves
remaining work for M5.

## ADR-011 — Productize Real Repo Mode before adding integrations

Status: Accepted — July 17, 2026

The next developer-facing slice is M4.6: one-command local launch, a visual
branch-review workspace using the existing range context engine, and adaptive
deterministic questions for ordinary repositories. This turns already-built
evidence capabilities into a coherent workflow without introducing a new
credential boundary. OrbitCart remains unchanged as the deterministic flagship.

The implemented workspace reuses the existing timeline and answer modal. Its
four supported questions are generated by a deterministic local evidence engine
and validated so every citation contains the referenced event's real commit and
at least one same-event file. The visual branch review accepts only base and head
Git revisions; the repository path remains fixed in the server handler created
at process startup. Generic mode explicitly says that no model call runs and no
repository text is uploaded.

`python3 -m app.cli serve --open` defaults to the current worktree and may open
the browser after the local server binds. Automatic opening is opt-in, keeping
headless and scripted use reliable.

## ADR-012 — Keep user-supplied model credentials server-side and optional

Status: Proposed — July 17, 2026

An optional BYOK mode may read `OPENAI_API_KEY` in the local server environment
and expose a bounded repository-question endpoint. The browser may learn only
whether AI is configured; it must never receive, store, or submit the key. The
question endpoint is explicitly enabled, rate-limited, validates citations
against the fixed repository, and falls back without affecting the zero-key
timeline.

The public static deployment will not include a key-entry form. Browser-held
keys are secrets exposed to client code, while a hosted proxy would make this
project responsible for authentication, abuse prevention, billing controls,
and secret custody.

## ADR-013 — Reuse local Git auth first; prefer a GitHub App if hosted later

Status: Proposed — July 17, 2026

The first remote-repository convenience path will delegate cloning to the
developer's existing Git credential manager, SSH configuration, or authenticated
GitHub CLI. AI Time Machine will not extract or persist those credentials.

If hosted repository selection is later required, use a GitHub App with
read-only metadata and contents permissions for explicitly selected repositories.
This is deferred because it introduces callback hosting, app credentials,
short-lived token handling, organization approval, private-code isolation and
deletion, rate limits, auditability, and a larger security and privacy surface.
