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

## Real Repo Mode developer proof

Real Repo Mode will add a local-only workflow for arbitrary Git repositories.
It will reuse the evidence and certainty rules above, keep OrbitCart as the
flagship demo, and prove genericity by analyzing AI Time Machine's own history.

Required scope is local repository selection, generic timeline ingestion,
browser serving, and branch or commit-range context. An opt-in
ChatGPT-authenticated Codex artifact may be added only after the evidence-only
workflow passes. GitHub OAuth, hosted private repositories, editor extensions,
team features, and autonomous modification remain deferred.

## Developer workspace and planned opt-in integrations

M4.6 exposes the existing branch context engine in the browser, makes local
startup one command, and adds adaptive deterministic questions for ordinary
repositories. These answers remain evidence-engine output and are never labeled
as GPT output. Browser requests may select Git revisions for review but cannot
change the repository path fixed at server startup.

Optional custom AI analysis is BYOK and local-server-only. A user may configure
their own Platform API key outside the browser process, but the public client
must never receive, persist, or transmit that key. The zero-key workflow remains
complete and is always the default.

Remote Git authentication remains separate from model authentication. The first
integration should reuse a developer's existing local Git or GitHub CLI login.
A future hosted connection should use a fine-grained, read-only GitHub App for
selected repositories rather than broad OAuth access. See
`docs/UPCOMING_DEVELOPER_MILESTONES.md`.
