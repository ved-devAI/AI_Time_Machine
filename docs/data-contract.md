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
  "title": "human-readable commit title",
  "summary": "what changed",
  "why": "why it mattered",
  "certainty": "confirmed | inferred | missing-evidence",
  "confidence": 0.0,
  "files": [{"path": "src/file.py", "status": "M"}],
  "evidence": [{"kind": "commit", "label": "...", "value": "..."}],
  "risks": ["possible consequence"],
  "related_event_ids": ["event-..."]
}
```

During the first vertical slice, summaries and reasons are extracted from the
commit evidence itself. GPT-5.6 enrichment will use this same contract and add
inferred causal explanations without replacing the underlying evidence.

