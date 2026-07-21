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

### M5 — Trust semantics

Status: Complete — July 20, 2026

Target: July 20

Execution guide: `docs/M5.md`

- Rename the generic-mode `Evidence coverage` metric to the precise
  `Commit + diff verified` label; do not imply rationale or risk coverage
- Expand branch `missing_evidence` for non-empty ranges with absent rationale,
  structured risks, incident/fix history, and external operational evidence
- Add focused regression tests for both trust semantics
- Run the full verification suite and browser-check OrbitCart plus Real Repo Mode
- Freeze broad feature work after the milestone passes

### M5.1 — Submission trust-integrity hotfix

Status: Complete and verified — July 21, 2026

Target: Before M6 recording and final release verification

This is the only approved exception to the M5 product freeze. It is limited to
trust claims and validation behavior already exposed by the current product.

- Bind optional live-cache entries to the current evidence digest and validate
  their complete analysis payload before returning cached output
- Reject malformed or stale caches and fall back safely without labeling them as
  current GPT output
- Replace broad `validated` wording with precise `reference-validated` or
  `citation-integrity checked` wording unless semantic entailment was verified
- Separate commit/diff verification from rationale, classification, and causal
  confidence in generic event cards; do not show blanket 98% confidence for
  commits whose rationale is `not recorded`
- Add negative tests for stale caches and invalid cross-field relationships,
  plus UI-copy tests for reference-integrity and generic-confidence semantics
- Re-run the full zero-key verification and OrbitCart browser flow

Exit condition: the submission makes no claim that reference integrity proves
textual entailment, and no cached live result can cross an evidence snapshot.

Completion: passed with 51 application tests, the OrbitCart regression test,
both artifact validators, the 15-check grounding scorecard, and desktop plus
390 × 844 browser verification for OrbitCart and Real Repo Mode.

### M6 — Demo and submission

Status: Pending

Target: July 21 before 5:00 PM PT

Execution guide: `docs/M5.md`

- Record public YouTube demo under three minutes
- Explain how Codex and GPT-5.6 were used
- Capture required `/feedback` session ID
- Add supported platforms, judge testing, and Codex collaboration details to README
- Finalize Devpost description and testing instructions
- Verify repository, deployment, video, and links

July 21 is reserved only for submission verification and emergencies.

### M7 — Git history correctness

Status: Post-submission

- Use merge-base semantics so diverged base-branch changes are not presented as
  feature-branch changes
- Define merge-commit evidence semantics instead of reporting zero changed files
- Separate pre-branch problem history from incidents and fixes inside the range
- Preserve rename history in timeline, file history, and incident/fix connections
- Add divergent-branch, merge, rename, and before-vs-in-range tests

### M8 — Code-aware semantic grounding

Status: Post-submission, after M7

- Extract bounded diff hunks or semantic summaries with stable evidence IDs
- Bind every model claim to exact evidence excerpts rather than only a commit
  and same-event filename
- Enforce the complete schema and cross-field invariants at runtime
- Add entailment-oriented adversarial evaluations
- Add optional local-server BYOK questions only after the stronger evidence
  contract passes; keep keys server-side and the zero-key path complete

### M9 — Large-repository performance

Status: Post-submission, after M7 foundations

- Add visible history, file-count, diff-size, and co-change-pair limits
- Batch Git extraction instead of launching one process per commit and one
  history process per changed file
- Cache immutable evidence by repository and revision with safe invalidation
- Exclude or down-weight generated files, vendor trees, and mass-format commits
- Add performance fixtures with latency and memory budgets

### M10 — Repository connectivity and hosted boundaries

Status: Post-submission, after M7-M9

- First reuse existing local Git, SSH, credential-manager, or `gh` authentication
- Later evaluate a read-only, selected-repository GitHub App
- Keep Git authentication separate from model authentication
- Do not put Platform API keys in browser code or assume broad token custody

Detailed scope, ordering, security constraints, and acceptance criteria are in
`docs/UPCOMING_DEVELOPER_MILESTONES.md`.
