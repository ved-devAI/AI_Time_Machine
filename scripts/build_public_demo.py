#!/usr/bin/env python3
"""Build an API-free public demo snapshot from validated Git evidence."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.analysis import analyze_bug_origin
from app.ask_repo import QUESTIONS, ask_repo
from app.git_ingest import read_timeline


FRONTEND = ROOT / "frontend"
ORBITCART = ROOT / ".data" / "orbitcart"
DIST = ROOT / "dist"
CLIENT = DIST / "client"
DATA = CLIENT / "demo-data"
BUG_ARTIFACT = ROOT / "artifacts" / "orbitcart" / "bug-origin.codex.json"
ASK_ARTIFACT = ROOT / "artifacts" / "orbitcart" / "ask-repo.codex.json"


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if not (ORBITCART / ".git").exists():
        raise SystemExit("OrbitCart is missing. Run python3 scripts/create_orbitcart.py first.")

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(FRONTEND, CLIENT)
    DATA.mkdir()

    timeline = read_timeline(ORBITCART)
    investigation = analyze_bug_origin(timeline, artifact_path=BUG_ARTIFACT)
    write_json(DATA / "timeline.json", timeline)
    write_json(DATA / "investigation.json", investigation)
    for question in QUESTIONS:
        answer = ask_repo(timeline, question["id"], ASK_ARTIFACT)
        write_json(DATA / f"ask-{question['id']}.json", answer)

    (CLIENT / "runtime-config.js").write_text(
        'window.AI_TIME_MACHINE_RUNTIME = Object.freeze({ mode: "snapshot" });\n',
        encoding="utf-8",
    )
    server = DIST / "server"
    server.mkdir()
    (server / "index.js").write_text(
        """const worker = {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === \"/\") url.pathname = \"/index.html\";
    return env.ASSETS.fetch(new Request(url, request));
  },
};

export default worker;
""",
        encoding="utf-8",
    )
    print(f"Built verified public demo in {DIST}")


if __name__ == "__main__":
    main()
