# AI Time Machine — Current Handoff

Last refreshed: July 19, 2026 (Asia/Kolkata)

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
- Real Repo Mode analyzes and serves an arbitrary local Git worktree through
  `python3 -m app.cli` without GitHub OAuth or an OpenAI API key.
- Generic ingestion preserves subjects, authors, dates, commits, changed files,
  rename-aware overlap history, and the normalized browser timeline contract.
- Missing rationale and risk are labeled exactly `not recorded`; types derived
  from conventional-commit prefixes carry inferred classification metadata.
- Branch or commit-range context reports changed files, range commits, recent
  history for those files, connected incidents or fixes, and recorded risks.
- Repository selection is fixed at local server startup, so HTTP requests cannot
  expose arbitrary filesystem paths. OrbitCart-only artifacts are disabled in
  generic mode.
- The workflow is dogfooded on AI Time Machine: all nine committed milestones
  rendered chronologically, and `d79beca..HEAD` produced an evidence-grounded
  43-file, eight-commit context report at verification time.
- Developer Workspace launches the current repository with
  `python3 -m app.cli serve --open`; browser opening remains opt-in.
- Generic mode now shows a visual **Review my branch** report with base/head,
  changed files, range commits, per-file history, incidents/fixes, recorded
  risks, and missing evidence. Evidence items navigate to timeline events.
- Four adaptive deterministic questions cover recent changes, co-changing
  files, branch problem history, and missing rationale. Their answers validate
  every cited event, commit, and same-event file before rendering.
- Generic onboarding labels the source `Local evidence engine · deterministic`,
  states that no model call runs, and explains that the selected repository is
  fixed to the local process.
- M4.6 is browser verified on desktop and 390 × 844 with no page overflow or
  console errors. OrbitCart still exposes only its original three questions and
  validated six-stage trace.
- Desktop timeline and detail panels now own independent scroll regions, so
  long affected-file and connected-history content remains reachable instead of
  being clipped by the workspace boundary.
- A site-wide readability pass raises all interface text to at least 10px,
  increases body and evidence copy to 11–15px, and strengthens muted-text
  contrast. Desktop and 390 × 844 layouts remain free of horizontal overflow,
  and answer/detail panels retain their vertical scrolling.
- Timeline filters use fixed 36px inline-flex controls with centered labels;
  they remain aligned on desktop and horizontally scrollable at 390 × 844.
- The production timeline, stale-price answer, citation navigation, and six-stage
  Bug Origin Trace are browser verified with no console errors.
- Final desktop, trace, and mobile screenshots plus the project thumbnail are
  committed under `docs/screenshots/` and `frontend/project-thumbnail.png`.
- Forty-two application tests and the OrbitCart regression test pass.
- The local app runs at `http://127.0.0.1:8765` and currently serves the
  bundled OrbitCart repository via
  `python3 -m app.cli serve .data/orbitcart`.

## Financial and hackathon constraint

Do not require the user to buy OpenAI API credits. The user has ChatGPT Plus and
$100 in Codex credits. Plus usage is consumed first and Codex credits extend
Codex work after the included allowance. These are not assumed to be Platform
API credits.

The submission story must say that GPT-5.6 in Codex materially helped design,
build, test, review, and evaluate the causal workflow. Do not imply that the
runtime called GPT-5.6 unless a real live call occurred.

## Approved upcoming product milestones

- **M4.6 Developer Workspace:** complete; one-command local launch, visual
  **Review my branch**, and four adaptive deterministic questions with clickable
  evidence are verified.
- **M6 Optional BYOK analysis:** a disabled-by-default local question endpoint
  that reads a user-owned Platform API key from the server environment. Never
  accept or store the key in the public browser UI.
- **M7 GitHub connection:** first reuse existing local Git/SSH/credential-manager
  or `gh` authentication; evaluate a read-only selected-repository GitHub App
  only as a later hosted integration.

Detailed requirements and security boundaries are in
`docs/UPCOMING_DEVELOPER_MILESTONES.md`.

## Exact next task

Begin **M5 — Demo and submission**:

1. Record the public YouTube demo under three minutes, leading with OrbitCart's
   stale-price investigation and briefly proving Real Repo Mode on this repo.
2. Explain GPT-5.6 Sol in Codex honestly as build-time analysis, implementation,
   review, and validated artifact generation—not a live runtime call.
3. Capture the required `/feedback` Codex session ID.
4. Finalize the Devpost description and testing instructions.
5. Re-run `python3 scripts/verify.py` and verify every public link before submit.

## Important implementation paths

- `PRODUCT_CONTRACT.md` — fixed MVP promise and evidence rules
- `scripts/create_orbitcart.py` — deterministic 12-commit demo repository
- `app/git_ingest.py` — Git-to-timeline evidence extraction
- `app/cli.py` — local analyze, serve, and context commands
- `app/repo_questions.py` — deterministic generic questions and citation validation
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
- `tests/test_real_repo_mode.py` — generic repository and range failure cases
- `tests/test_analysis.py` — causal grounding and fallback tests
- `docs/ai-analysis.md` — current analysis architecture
- `docs/DECISIONS.md` — durable architecture decisions
- `ROADMAP.md` — milestone plan through submission

## Run and verify

```bash
python3 scripts/create_orbitcart.py
python3 -m app.server
python3 -m app.cli analyze .
python3 -m app.cli serve .
python3 -m app.cli serve --open
python3 -m app.cli context . --base d79beca --head HEAD
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

- The optional validated Codex question artifact for arbitrary repositories was
  intentionally deferred after completing the required API-free workflow.
- The BYOK endpoint and GitHub connection are post-submission and not
  implemented. M6 and M7 must not delay submission.
- The public YouTube demo and Devpost submission copy are pending.
- The required `/feedback` Codex session ID still needs to be captured for the
  final submission.

## Handoff rule

Treat this file as a living snapshot. Refresh the sections above after every
major milestone, preserve useful architecture history in `docs/DECISIONS.md`,
and make the next action explicit enough that a new Codex task can begin without
reconstructing this conversation.
