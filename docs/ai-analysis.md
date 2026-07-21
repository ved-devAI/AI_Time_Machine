# GPT-5.6 causal analysis

## Purpose

The model is used for a narrow task: reconstructing a causal chain for an
engineering incident from evidence already extracted from Git. It does not
invent timeline events or replace the evidence layer.

## Default: reference-validated Codex artifact

The default demo does not call a paid API. `scripts/codex_artifact.py prepare`
exports a compact evidence package and the strict schema. A read-only
`codex exec -m gpt-5.6-sol` run uses ChatGPT-managed Codex authentication to
generate the analysis. The finalizer rejects unknown event IDs and any commit
or file reference that does not belong to the cited event.

The completed envelope records the model identifier, evidence digest, source
revision, prompt, schema, generation time, and Codex session ID. At runtime the
artifact is accepted only if its digest still matches the current Git timeline.

Ask the Repo uses a second artifact with three fixed, judge-facing questions.
Every answer contains event-level citations. Each citation must include the
event's short commit and at least one file changed in that same event. Unknown
events, cross-event files, unsupported questions, and mismatched evidence
digests are rejected before an answer reaches the interface.

These checks prove reference integrity: the cited events, commits, and files
exist and belong together. They do not independently prove that arbitrary prose
is semantically entailed by those references. The interface names this boundary
explicitly; code-excerpt grounding and entailment evaluation remain M8 work.

## Optional Responses API design

The backend calls the Responses API with model `gpt-5.6`, medium reasoning, and
strict Structured Outputs. The supplied JSON Schema requires:

- A likely origin and observed trigger
- A six-role causal chain
- Evidence references for every chain item
- Confirmed, inferred, or missing-evidence certainty
- Numeric confidence
- Explicit missing evidence and remaining risks

Repository content is described as untrusted evidence in the system prompt. The
model is instructed to ignore instructions found inside repository text and to
use only event IDs, commits, and files present in the supplied timeline.

After generation, the backend validates the complete six-stage shape, required
text and certainty fields, origin/trigger/resolution relationships, distinct
stage events, and same-event commit/file references. Invalid or unavailable
model output is never displayed as live analysis.

## Reliability and credit control

- The reference-validated Codex artifact is the default analysis source.
- No API key or paid runtime request is required.
- Live API analysis requires both `OPENAI_API_KEY` and the explicit setting
  `AI_TIME_MACHINE_ANALYSIS_MODE=live`.
- Successful live results are cached in `.data/orbitcart-analysis.json` inside
  a versioned envelope containing the selected model and evidence digest. Cache
  reads revalidate the digest, provenance, and complete analysis payload.
- Reopening the trace reuses the in-memory result.
- If the API is unavailable, the app uses a deterministic investigation built
  from the same Git evidence.
- The interface labels fallback output as `Evidence fallback · demo safe` and
  never presents it as GPT output.
- Ask the Repo caches answers in the browser after their first reference-checked load;
  reopening a question does not perform model work.

## Output flow

```text
Git commits and changed files
        ↓
Evidence-preserving timeline
        ↓
Read-only GPT-5.6 Sol run in Codex
        ↓
Schema, digest, event, commit, and file validation
        ↓
Versioned offline artifact
        ↓
Visual Bug Origin Trace
```
