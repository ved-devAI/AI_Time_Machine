# AI Time Machine — Current Handoff

Last refreshed: July 16, 2026 (Asia/Kolkata)

## Start here

AI Time Machine is an OpenAI Build Week Developer Tools submission. It turns
real Git history into an evidence-backed timeline explaining why a codebase
evolved. The judge-facing story uses the OrbitCart stale-price incident to show
how a performance optimization introduced a correctness bug.

Current branch: `main`, tracking `origin/main`

Remote: `git@github.com:ved-devAI/AI_Time_Machine.git`

Repository: <https://github.com/ved-devAI/AI_Time_Machine>

Public demo: <https://ai-time-machine-demo.vedheshvit.chatgpt.site>

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
- The deterministic grounding scorecard passes all 15 checks with a 100% score.
- Stale, malformed, incomplete, invented-event, and cross-event citation cases
  are rejected or routed to a transparently labeled fallback.
- `python3 scripts/verify.py` regenerates the demo repository and runs the full
  judge workflow without third-party packages.
- Desktop flows are browser verified with no console errors. The 980px and
  650px responsive contracts are automated in the test suite.
- The required 390 × 844 release pass is complete. The mobile Bug Origin Trace
  uses a vertical six-stage chain with no page or dialog horizontal overflow.
- Dialogs reopen at the top, return keyboard focus to their launcher, and expose
  visible focus states.
- The public deployment serves a validated, API-free Git evidence snapshot and
  clearly labels it `Git snapshot verified`.
- The production timeline, stale-price answer, citation navigation, and six-stage
  Bug Origin Trace are browser verified with no console errors.
- Final desktop, trace, and mobile screenshots plus the project thumbnail are
  committed under `docs/screenshots/` and `frontend/project-thumbnail.png`.
- Twenty-nine application tests and the OrbitCart regression test pass.
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

Implement **M4.5 — Real Repo Mode** in a fresh Codex task, following
`docs/M4.5_REAL_REPO_MODE.md`:

1. Add a local CLI that analyzes and serves an arbitrary Git repository.
2. Generalize ingestion for repositories without structured `Summary:`, `Why:`,
   and `Risk:` commit bodies; missing rationale must remain `not recorded`.
3. Add branch or commit-range context for files changed between `base` and
   `head`.
4. Dogfood the workflow on the AI Time Machine repository itself.
5. Keep OrbitCart, the public demo, and the complete judge verification green.
6. Only after the required workflow passes, consider the optional validated
   Codex question-artifact command described in the M4.5 brief.

## Important implementation paths

- `PRODUCT_CONTRACT.md` — fixed MVP promise and evidence rules
- `scripts/create_orbitcart.py` — deterministic 12-commit demo repository
- `app/git_ingest.py` — Git-to-timeline evidence extraction
- `app/analysis.py` — strict causal-analysis schema, optional API adapter, fallback
- `app/ask_repo.py` — fixed questions, answer validation, artifact replay, fallback
- `scripts/codex_artifact.py` — evidence export and artifact validation CLI
- `scripts/ask_repo_artifact.py` — Ask the Repo schema and artifact CLI
- `scripts/evaluate_grounding.py` — deterministic grounding scorecard
- `scripts/verify.py` — complete zero-dependency judge verification
- `evaluations/orbitcart_grounding.json` — expected causal and citation evidence
- `docs/EVALUATION.md` — reliability design and manual visual checklist
- `docs/M4.5_REAL_REPO_MODE.md` — required scope, proof, tests, and non-goals
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
python3 scripts/verify.py
# Or run the individual checks:
python3 -m unittest discover -s tests -v
PYTHONPATH=.data/orbitcart python3 -m unittest discover -s .data/orbitcart/tests -v
python3 scripts/codex_artifact.py validate
python3 scripts/ask_repo_artifact.py validate
python3 scripts/evaluate_grounding.py
node --check frontend/app.js
git diff --check
```

## Known gaps

- Real Repo Mode is specified but not implemented.
- The public YouTube demo and Devpost submission copy are pending.
- The required `/feedback` Codex session ID still needs to be captured for the
  final submission.

## Handoff rule

Treat this file as a living snapshot. Refresh the sections above after every
major milestone, preserve useful architecture history in `docs/DECISIONS.md`,
and make the next action explicit enough that a new Codex task can begin without
reconstructing this conversation.
