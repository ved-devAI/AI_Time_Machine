#!/usr/bin/env python3
"""Prepare and validate the GPT-5.6-in-Codex Ask the Repo artifact."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORBITCART = ROOT / ".data" / "orbitcart"
ARTIFACT_DIR = ROOT / "artifacts" / "orbitcart"
SCHEMA_PATH = ARTIFACT_DIR / "ask-repo.schema.json"
FINAL_PATH = ARTIFACT_DIR / "ask-repo.codex.json"

sys.path.insert(0, str(ROOT))

from app.analysis import evidence_digest  # noqa: E402
from app.ask_repo import ASK_REPO_SCHEMA, load_answer_artifact, validate_answer_set  # noqa: E402
from app.git_ingest import read_timeline  # noqa: E402


def timeline() -> dict:
    if not ORBITCART.exists():
        subprocess.run([sys.executable, "scripts/create_orbitcart.py"], cwd=ROOT, check=True)
    return read_timeline(ORBITCART)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prepare() -> None:
    write_json(SCHEMA_PATH, ASK_REPO_SCHEMA)
    print(f"Schema: {SCHEMA_PATH.relative_to(ROOT)}")
    print("Evidence: artifacts/orbitcart/evidence.json")


def current_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def finalize(raw_path: Path, session_id: str | None, model: str) -> None:
    data = timeline()
    payload = validate_answer_set(json.loads(raw_path.read_text(encoding="utf-8")), data)
    envelope = {
        "artifact_version": 1,
        "provenance": {
            "generator": "codex exec",
            "model": model,
            "authentication": "ChatGPT-managed Codex access",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_revision": current_revision(),
            "evidence_sha256": evidence_digest(data),
            "codex_session_id": session_id,
            "prompt_path": "artifacts/orbitcart/ask-repo.prompt.md",
            "schema_path": "artifacts/orbitcart/ask-repo.schema.json",
        },
        "payload": payload,
    }
    write_json(FINAL_PATH, envelope)
    print(f"Validated {len(payload['answers'])} answers")
    print(f"Artifact: {FINAL_PATH.relative_to(ROOT)}")


def validate(path: Path) -> None:
    result = load_answer_artifact(timeline(), path)
    print(f"Valid artifact: {path.relative_to(ROOT)} ({len(result['answers'])} answers)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare")
    finalize_parser = subparsers.add_parser("finalize")
    finalize_parser.add_argument("raw_path", type=Path)
    finalize_parser.add_argument("--session-id")
    finalize_parser.add_argument("--model", default="gpt-5.6-sol")
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("path", type=Path, nargs="?", default=FINAL_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "finalize":
        finalize(args.raw_path.resolve(), args.session_id, args.model)
    else:
        validate(args.path.resolve())


if __name__ == "__main__":
    main()
