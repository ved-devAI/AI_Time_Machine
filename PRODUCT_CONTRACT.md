# AI Time Machine — Product Contract

## Demo promise

AI Time Machine analyzes real Git history and reconstructs an evidence-backed
timeline explaining why a codebase evolved. Its flagship experience traces a
bug back to the change that likely introduced it.

## Judge-facing proof

The first demo repository is OrbitCart, a small but genuine Git repository with
a deliberately authored engineering history. The app reads its commits and
diffs at runtime. Timeline cards are not hard-coded into the interface.

The headline investigation follows a stale-price bug caused by an earlier
checkout caching optimization. AI Time Machine will show the optimization, the
later failure, the rollback, and the eventual safe fix as a causal chain.

## MVP boundary

Included:

- Real Git ingestion
- Interactive chronological timeline
- Event details and affected files
- Evidence, certainty, and confidence labels
- Ask the Repo using GPT-5.6
- Bug Origin Trace

Deferred:

- GitHub OAuth and private repository access
- Team accounts and enterprise indexing
- Multiple source-control providers
- Autonomous code modification

## Evidence rules

Every claim must be attached to observable repository evidence. The interface
must distinguish confirmed facts from inferences. Missing evidence must never
be silently converted into certainty.

## Planned M4.5 developer proof

Real Repo Mode will add a local-only workflow for arbitrary Git repositories.
It will reuse the evidence and certainty rules above, keep OrbitCart as the
flagship demo, and prove genericity by analyzing AI Time Machine's own history.

Required scope is local repository selection, generic timeline ingestion,
browser serving, and branch or commit-range context. An opt-in
ChatGPT-authenticated Codex artifact may be added only after the evidence-only
workflow passes. GitHub OAuth, hosted private repositories, editor extensions,
team features, and autonomous modification remain deferred.
