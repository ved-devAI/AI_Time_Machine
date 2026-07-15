#!/usr/bin/env python3
"""Prepare and validate the reproducible GPT-5.6-in-Codex analysis artifact."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ORBITCART = ROOT / ".data" / "orbitcart"
ARTIFACT_DIR = ROOT / "artifacts" / "orbitcart"
EVIDENCE_PATH = ARTIFACT_DIR / "evidence.json"
SCHEMA_PATH = ARTIFACT_DIR / "analysis.schema.json"
FINAL_PATH = ARTIFACT_DIR / "bug-origin.codex.json"

sys.path.insert(0, str(ROOT))

from app.analysis import (  # noqa: E402
    ANALYSIS_SCHEMA,
    evidence_digest,
    timeline_evidence,
    validate_analysis,
)
from app.git_ingest import read_timeline  # noqa: E402


def timeline() -> dict[str, Any]:
    if not ORBITCART.exists():
        subprocess.run([sys.executable, "scripts/create_orbitcart.py"], cwd=ROOT, check=True)
    return read_timeline(ORBITCART)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prepare() -> None:
    data = timeline()
    project = {key: value for key, value in data["project"].items() if key != "repository_path"}
    evidence = {
        "artifact_version": 1,
        "project": project,
        "evidence_sha256": evidence_digest(data),
        "events": timeline_evidence(data),
    }
    write_json(EVIDENCE_PATH, evidence)
    write_json(SCHEMA_PATH, ANALYSIS_SCHEMA)
    print(f"Prepared {len(evidence['events'])} events")
    print(f"Evidence: {EVIDENCE_PATH.relative_to(ROOT)}")
    print(f"Schema: {SCHEMA_PATH.relative_to(ROOT)}")


def current_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def finalize(raw_path: Path, session_id: str | None, model: str) -> None:
    data = timeline()
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    analysis = validate_analysis(raw, data)
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
            "prompt_path": "artifacts/orbitcart/analysis.prompt.md",
            "schema_path": "artifacts/orbitcart/analysis.schema.json",
        },
        "analysis": analysis,
    }
    write_json(FINAL_PATH, envelope)
    print(f"Validated {len(analysis['causal_chain'])} causal stages")
    print(f"Artifact: {FINAL_PATH.relative_to(ROOT)}")


def validate_artifact(path: Path) -> None:
    data = timeline()
    envelope = json.loads(path.read_text(encoding="utf-8"))
    if envelope.get("artifact_version") != 1:
        raise ValueError("Unsupported artifact version.")
    provenance = envelope.get("provenance", {})
    if provenance.get("evidence_sha256") != evidence_digest(data):
        raise ValueError("Artifact evidence digest does not match the current timeline.")
    validate_analysis(envelope["analysis"], data)
    print(f"Valid artifact: {path.relative_to(ROOT)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare", help="Export evidence and the strict output schema")
    finalize_parser = subparsers.add_parser("finalize", help="Validate raw Codex JSON and create artifact")
    finalize_parser.add_argument("raw_path", type=Path)
    finalize_parser.add_argument("--session-id")
    finalize_parser.add_argument("--model", default="gpt-5.6-sol")
    validate_parser = subparsers.add_parser("validate", help="Validate a completed Codex artifact")
    validate_parser.add_argument("path", type=Path, nargs="?", default=FINAL_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "finalize":
        finalize(args.raw_path.resolve(), args.session_id, args.model)
    else:
        validate_artifact(args.path.resolve())


if __name__ == "__main__":
    main()
