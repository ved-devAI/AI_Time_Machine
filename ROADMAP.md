# AI Time Machine — Build Week Roadmap

Submission deadline: July 21, 2026 at 5:00 PM PT

Internal deadline: July 20, 2026

## Milestones

### M0 — Evidence timeline foundation

Status: Complete

- Real OrbitCart Git history
- Git ingestion and evidence contract
- Interactive timeline and event details
- Bug Origin Trace
- Tests, README, license, and public GitHub repository

### M1 — API-free Codex analysis artifact

Status: Complete

Target: July 16

- Export compact repository evidence
- Define a reproducible GPT-5.6-in-Codex analysis prompt
- Validate the generated artifact against the strict schema
- Store provenance without secrets or unsupported claims
- Make offline artifact replay the primary demo path

### M2 — Ask the Repo

Status: Complete

Target: July 17

- Three judge-ready questions
- Evidence-linked answers
- Answer panel integrated with timeline navigation
- Tests for unknown or fabricated evidence references

### M3 — Evaluation and reliability

Status: Complete

Target: July 18

- Grounding evaluation fixture
- Failure and missing-evidence cases
- Responsive browser verification
- Clean setup path for judges

### M4 — Product polish and deployment

Status: Complete

Target: July 19

- Final visual polish
- Public runnable deployment
- Repository cleanup and installation instructions
- Project thumbnail and submission screenshots

### M4.5 — Real Repo Mode

Status: Complete

Target: July 17

- Local CLI for analyzing and serving an arbitrary Git repository
- Generic evidence extraction when rationale is not recorded
- Branch or commit-range change context
- Self-analysis using the AI Time Machine repository
- Tests for invalid repositories, empty history, and range errors
- Optional validated Codex question artifact deferred; the required local
  evidence workflow is complete and M5 remains the priority

### M4.6 — Developer Workspace

Status: Complete

Target: timeboxed before M5 only if the release stays green

- One-command local launch with optional automatic browser opening
- Visual **Review my branch** workspace using the existing context engine
- Four adaptive deterministic repository questions with clickable evidence
- Generic-mode onboarding and privacy/source labels
- OrbitCart questions, trace, and zero-key verification remain unchanged

### M5 — Demo and submission

Status: Pending

Target: July 20

- Record public YouTube demo under three minutes
- Explain how Codex and GPT-5.6 were used
- Capture required `/feedback` session ID
- Finalize Devpost description and testing instructions
- Verify repository, deployment, video, and links

July 21 is reserved only for submission verification and emergencies.

### M6 — Optional BYOK analysis

Status: Post-submission

- User supplies `OPENAI_API_KEY` to the local server environment
- Local question endpoint builds a bounded evidence bundle
- Strict citation validation, cost notice, caching, timeouts, and fallback
- No API key fields or secrets in the public browser application

### M7 — GitHub connection

Status: Post-submission

- First reuse existing local Git, SSH, credential-manager, or `gh` authentication
- Later evaluate a read-only, selected-repository GitHub App
- Do not implement broad OAuth access, hosted private-repository storage, or
  token custody inside the hackathon timebox

See `docs/UPCOMING_DEVELOPER_MILESTONES.md` for the scope and security boundaries.
