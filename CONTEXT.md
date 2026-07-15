# AI Time Machine — Current Handoff

Last refreshed: July 15, 2026 (Asia/Kolkata)

## Start here

AI Time Machine is an OpenAI Build Week Developer Tools submission. It turns
real Git history into an evidence-backed timeline explaining why a codebase
evolved. The judge-facing story uses the OrbitCart stale-price incident to show
how a performance optimization introduced a correctness bug.

Current branch: `main`, tracking `origin/main`

Remote: `git@github.com:ved-devAI/AI_Time_Machine.git`

Repository: <https://github.com/ved-devAI/AI_Time_Machine>

The repository uses a local author identity and a repository-specific SSH key
for `ved-devAI`; it does not depend on the user's other GitHub accounts.

## Current product state

Working and verified:

- Deterministic generator creates a genuine 12-commit OrbitCart repository.
- Python Git ingestion reads commits, changed files, reasons, risks, and file
  overlap connections.
- Browser UI renders the full timeline, filters, event detail, evidence,
  confidence, and connected history.
- Bug Origin Trace visualizes six causal stages: pressure, origin, symptom,
  containment, resolution, and verification.
- The likely origin node links back to the exact timeline event.
- The default trace replays a committed GPT-5.6 Sol analysis generated through
  ChatGPT-authenticated Codex, with no runtime API key or paid API call.
- Artifact validation checks its evidence digest, exact six-stage sequence,
  event IDs, commits, and file references before anything reaches the UI.
- The trace shows honest source provenance, the evidence digest, and the Codex
  session ID `019f662f-d32a-7db2-9977-560867fef985`.
- A strict GPT-5.6 Responses API adapter exists but is optional.
- If the artifact is missing or invalid, the app uses a clearly labeled
  evidence fallback.
- Successful optional model responses are cached to control cost.
- The full trace and origin-node navigation are browser verified with no
  console errors.
- Ask the Repo presents three judge-ready questions covering pricing
  complexity, stale-price origin, and current change risk.
- The three answers replay a validated GPT-5.6 Sol Codex artifact and cite only
  real timeline events, commits, and same-event files.
- Every citation opens the exact supporting timeline event; fabricated events
  and cross-event file references are rejected by tests.
- Ask the Repo records Codex session
  `019f6643-741f-7c31-a967-6efae9af01b1` and the current evidence digest.
- Eighteen application tests and the OrbitCart regression test pass.
- The local app runs at `http://127.0.0.1:8765`.

## Financial and hackathon constraint

Do not require the user to buy OpenAI API credits. The user has ChatGPT Plus and
$100 in Codex credits. Plus usage is consumed first and Codex credits extend
Codex work after the included allowance. These are not assumed to be Platform
API credits.

The submission story must say that GPT-5.6 in Codex materially helped design,
build, test, review, and evaluate the causal workflow. Do not imply that the
runtime called GPT-5.6 unless a real live call occurred.

## Exact next task

Implement **M3 — Evaluation and reliability**:

1. Add a compact grounding evaluation fixture for all three questions and the
   Bug Origin Trace.
2. Cover missing, stale, and deliberately invalid artifact cases.
3. Verify desktop and mobile layouts.
4. Make the setup path clean and repeatable for judges.

## Important implementation paths

- `PRODUCT_CONTRACT.md` — fixed MVP promise and evidence rules
- `scripts/create_orbitcart.py` — deterministic 12-commit demo repository
- `app/git_ingest.py` — Git-to-timeline evidence extraction
- `app/analysis.py` — strict causal-analysis schema, optional API adapter, fallback
- `app/ask_repo.py` — fixed questions, answer validation, artifact replay, fallback
- `scripts/codex_artifact.py` — evidence export and artifact validation CLI
- `scripts/ask_repo_artifact.py` — Ask the Repo schema and artifact CLI
- `artifacts/orbitcart/` — prompt, schema, evidence, and validated Codex result
- `app/server.py` — local HTTP and JSON endpoints
- `frontend/index.html` — application shell
- `frontend/app.js` — timeline, detail, and Bug Origin Trace behavior
- `frontend/styles.css` — responsive developer-tool visual system
- `tests/test_git_ingest.py` — ingestion and evidence tests
- `tests/test_analysis.py` — causal grounding and fallback tests
- `docs/ai-analysis.md` — current analysis architecture
- `docs/DECISIONS.md` — durable architecture decisions
- `ROADMAP.md` — milestone plan through submission

## Run and verify

```bash
python3 scripts/create_orbitcart.py
python3 -m app.server
```

Open <http://127.0.0.1:8765>.

```bash
python3 -m unittest discover -s tests -v
PYTHONPATH=.data/orbitcart python3 -m unittest discover -s .data/orbitcart/tests -v
python3 scripts/codex_artifact.py validate
python3 scripts/ask_repo_artifact.py validate
node --check frontend/app.js
git diff --check
```

## Known gaps

- Automated grounding evaluation and invalid-artifact fixtures are pending.
- Mobile browser verification is pending.
- Deployment, thumbnail, demo video, and Devpost submission copy are pending.
- The required `/feedback` Codex session ID still needs to be captured for the
  final submission.

## Handoff rule

Treat this file as a living snapshot. Refresh the sections above after every
major milestone, preserve useful architecture history in `docs/DECISIONS.md`,
and make the next action explicit enough that a new Codex task can begin without
reconstructing this conversation.
