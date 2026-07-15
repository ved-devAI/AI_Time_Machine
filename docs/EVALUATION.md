# Grounding evaluation

AI Time Machine ships a deterministic scorecard for its committed GPT-5.6 Sol
artifacts. Run the complete judge workflow with:

```bash
python3 scripts/verify.py
```

The grounding fixture checks:

- The exact stale-price origin, trigger, causal roles, and event sequence
- Calibrated certainty and minimum confidence
- Required evidence events for all three Ask the Repo answers
- Rejection of invented trace evidence and incomplete causal chains
- Rejection of invented answer events and cross-event file citations

The report is written to `artifacts/orbitcart/evaluation-report.json`. A passing
report must score 100%; any failed check exits non-zero.

The test suite separately verifies transparent fallback behavior for missing,
malformed, and stale-digest artifacts. Fallback output is never labeled as GPT.

## Visual checks

Desktop flows are browser verified for the timeline, Bug Origin Trace, all three
questions, and citation navigation. Automated CSS tests assert that the actual
980px and 650px media blocks stack the workspace, prompt list, evidence cards,
and trace content without fixed-width repository cards.

Before recording the demo, perform one manual narrow-viewport pass at 390 × 844
in browser responsive mode. Confirm the three prompt buttons and evidence cards
stack to one column and that both dialogs scroll vertically without horizontal
overflow.
