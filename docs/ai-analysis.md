# GPT-5.6 causal analysis

## Purpose

The model is used for a narrow task: reconstructing a causal chain for an
engineering incident from evidence already extracted from Git. It does not
invent timeline events or replace the evidence layer.

## Request design

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

- Live analysis is used when `OPENAI_API_KEY` is configured.
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
Strict GPT-5.6 causal-analysis schema
        ↓
Event-ID and confidence validation
        ↓
Visual Bug Origin Trace
```

