# AI Time Machine repository instructions

## Start every task here

1. Read `CONTEXT.md` completely.
2. Check `git status --short --branch` and `git log -1 --oneline`.
3. Read the specific implementation files named by the current task in
   `CONTEXT.md`.
4. Preserve unrelated user changes.

## Product invariants

- AI Time Machine explains why a codebase evolved using observable repository
  evidence.
- Every causal claim must point to real event IDs, commits, or affected files.
- Clearly distinguish confirmed facts, inference, and missing evidence.
- The default demo must work without an OpenAI API key or paid runtime call.
- Never label fallback or deterministic output as live GPT-5.6 output.
- GPT-5.6 usage through Codex must be documented honestly as build-time analysis,
  implementation, review, and evaluation unless a live API call actually ran.
- Keep OrbitCart deterministic so the three-minute demo remains reliable.

## Verification

Run before committing a milestone:

```bash
python3 -m unittest discover -s tests -v
PYTHONPATH=.data/orbitcart python3 -m unittest discover -s .data/orbitcart/tests -v
python3 scripts/codex_artifact.py validate
python3 scripts/ask_repo_artifact.py validate
node --check frontend/app.js
git diff --check
```

Also verify the affected browser flow for UI changes.

## Handoff maintenance

After each major session, refresh the top snapshot in `CONTEXT.md` with:

- What changed
- What is verified
- What remains incomplete
- The exact next task
- Any new commands, constraints, or risks

Update `ROADMAP.md` milestone statuses and append material architecture choices
to `docs/DECISIONS.md`. Do not place secrets, tokens, API keys, or private key
material in any handoff file.
