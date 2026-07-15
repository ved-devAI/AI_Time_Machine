#!/usr/bin/env python3
"""Run the complete judge-facing verification workflow with no extra packages."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    ("Generate deterministic OrbitCart history", [sys.executable, "scripts/create_orbitcart.py"]),
    ("Run application tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
    (
        "Run OrbitCart regression test",
        [sys.executable, "-m", "unittest", "discover", "-s", ".data/orbitcart/tests", "-v"],
    ),
    ("Validate Bug Origin artifact", [sys.executable, "scripts/codex_artifact.py", "validate"]),
    ("Validate Ask the Repo artifact", [sys.executable, "scripts/ask_repo_artifact.py", "validate"]),
    (
        "Run grounding scorecard",
        [
            sys.executable,
            "scripts/evaluate_grounding.py",
            "--write",
            "artifacts/orbitcart/evaluation-report.json",
        ],
    ),
    ("Check browser JavaScript", ["node", "--check", "frontend/app.js"]),
    ("Check repository whitespace", ["git", "diff", "--check"]),
]


def main() -> None:
    print("AI Time Machine — judge verification\n")
    for index, (label, command) in enumerate(COMMANDS, start=1):
        print(f"[{index}/{len(COMMANDS)}] {label}", flush=True)
        environment = None
        if label == "Run OrbitCart regression test":
            environment = {"PYTHONPATH": str(ROOT / ".data" / "orbitcart")}
        subprocess.run(command, cwd=ROOT, env=environment, check=True)
        print()
    print("Verification complete: all checks passed.")


if __name__ == "__main__":
    main()
