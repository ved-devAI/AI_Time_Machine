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

Status: Proposed — July 16, 2026

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
