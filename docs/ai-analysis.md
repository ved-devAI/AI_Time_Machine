# GPT-5.6 causal analysis

## Purpose

The model is used for a narrow task: reconstructing a causal chain for an
engineering incident from evidence already extracted from Git. It does not
invent timeline events or replace the evidence layer.

## Default: validated Codex artifact

The default demo does not call a paid API. `scripts/codex_artifact.py prepare`
exports a compact evidence package and the strict schema. A read-only
`codex exec -m gpt-5.6-sol` run uses ChatGPT-managed Codex authentication to
generate the analysis. The finalizer rejects unknown event IDs and any commit
or file reference that does not belong to the cited event.

The completed envelope records the model identifier, evidence digest, source
revision, prompt, schema, generation time, and Codex session ID. At runtime the
artifact is accepted only if its digest still matches the current Git timeline.

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

After generation, the backend validates that every returned event ID exists in
the extracted timeline. Invalid or unavailable model output is never displayed
as live analysis.

## Reliability and credit control

- The validated Codex artifact is the default analysis source.
- No API key or paid runtime request is required.
- Live API analysis requires both `OPENAI_API_KEY` and the explicit setting
  `AI_TIME_MACHINE_ANALYSIS_MODE=live`.
- Successful live results are cached in `.data/orbitcart-analysis.json`.
- Reopening the trace reuses the in-memory result.
- If the API is unavailable, the app uses a deterministic investigation built
  from the same Git evidence.
- The interface labels fallback output as `Evidence fallback · demo safe` and
  never presents it as GPT output.

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
