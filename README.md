# AI Time Machine

AI Time Machine turns real Git history into an interactive, evidence-backed
timeline explaining why a codebase evolved.

This repository contains a working OpenAI Build Week project slice: a generated
OrbitCart Git repository, Git ingestion, an evidence timeline, constrained
GPT-5.6 causal analysis, and a visual Bug Origin Trace.

## Run locally

Requirements: Python 3.11+ and Git. No third-party packages are required for the
current slice.

```bash
python3 scripts/create_orbitcart.py
cp .env.example .env
# Add a project-scoped OPENAI_API_KEY to .env for live GPT-5.6 analysis.
python3 -m app.server
```

Open <http://127.0.0.1:8765>.

## Verify

```bash
python3 -m unittest discover -s tests -v
PYTHONPATH=.data/orbitcart python3 -m unittest discover -s .data/orbitcart/tests -v
```

## How it works

1. `scripts/create_orbitcart.py` creates a genuine 12-commit demo repository.
2. `app/git_ingest.py` reads commit metadata and changed files using Git.
3. `app/analysis.py` sends only extracted evidence to GPT-5.6 using a strict JSON
   Schema and validates every returned timeline reference.
4. `app/server.py` exposes the timeline and investigation endpoints.
5. `frontend/` renders the timeline and a six-stage visual Bug Origin Trace.

If no API key is configured or a live call fails, the investigation remains
runnable using an explicitly labeled evidence fallback. Successful GPT-5.6
analysis is cached to avoid spending credits on repeated demo clicks.

See [the analysis design](docs/ai-analysis.md) for grounding, validation, and
fallback details.
