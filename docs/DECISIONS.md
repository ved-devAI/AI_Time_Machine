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

