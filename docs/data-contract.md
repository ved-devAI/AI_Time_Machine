# Timeline data contract

Each timeline event uses the following stable shape:

```json
{
  "id": "event-<commit hash>",
  "commit_hash": "full Git SHA",
  "short_hash": "short Git SHA",
  "occurred_at": "ISO-8601 timestamp",
  "author": "commit author",
  "type": "feature | bug | fix | refactor | performance | rollback | test | change",
  "type_certainty": "confirmed | inferred",
  "title": "human-readable commit title",
  "summary": "what changed",
  "why": "why it mattered",
  "rationale_certainty": "confirmed | missing-evidence",
  "certainty": "confirmed | inferred | missing-evidence",
  "confidence": 0.0,
  "files": [{"path": "src/file.py", "status": "M"}],
  "evidence": [{"kind": "commit", "label": "...", "value": "..."}],
  "risks": ["possible consequence"],
  "related_event_ids": ["event-..."]
}
```

Summaries and reasons are extracted from commit evidence itself. In generic
repositories, a conventional-commit prefix may infer the event type but does not
turn that classification into a confirmed fact. Missing `Why:` and `Risk:`
fields use the literal value `not recorded`. GPT-5.6 enrichment uses this same
contract and may add inferred causal explanations without replacing the
underlying evidence.
