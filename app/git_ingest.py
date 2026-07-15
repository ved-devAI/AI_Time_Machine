"""Extract an evidence-preserving timeline from a local Git repository."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any


FIELD = "\x1f"
RECORD = "\x1e"


def _git(repository: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _body_value(body: str, label: str, fallback: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", body, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def _event_type(subject: str) -> str:
    prefix = subject.split("(", 1)[0].split(":", 1)[0].lower()
    return {
        "feat": "feature",
        "bug": "bug",
        "fix": "fix",
        "refactor": "refactor",
        "perf": "performance",
        "revert": "rollback",
        "test": "test",
    }.get(prefix, "change")


def _title(subject: str) -> str:
    value = subject.split(":", 1)[1].strip() if ":" in subject else subject
    return value[:1].upper() + value[1:]


def _files(repository: Path, commit_hash: str) -> list[dict[str, str]]:
    output = _git(
        repository,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-status",
        "-r",
        commit_hash,
    )
    files: list[dict[str, str]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        status, path = line.split("\t", 1)
        files.append({"path": path, "status": status[:1]})
    return files


def read_timeline(repository: Path) -> dict[str, Any]:
    repository = repository.resolve()
    if not (repository / ".git").exists():
        raise ValueError(f"Not a Git repository: {repository}")

    raw = _git(
        repository,
        "log",
        "--reverse",
        "--date=iso-strict",
        f"--pretty=format:%H{FIELD}%h{FIELD}%aI{FIELD}%an{FIELD}%s{FIELD}%b{RECORD}",
    )
    events: list[dict[str, Any]] = []
    previous_by_file: dict[str, str] = {}

    for record in raw.split(RECORD):
        record = record.strip()
        if not record:
            continue
        parts = record.split(FIELD)
        if len(parts) < 6:
            continue
        commit_hash, short_hash, date, author, subject = parts[:5]
        body = FIELD.join(parts[5:]).strip()
        files = _files(repository, commit_hash)
        event_id = f"event-{short_hash}"
        related = sorted(
            {
                previous_by_file[item["path"]]
                for item in files
                if item["path"] in previous_by_file
            }
        )[-3:]
        for item in files:
            previous_by_file[item["path"]] = event_id

        event_type = _event_type(subject)
        summary = _body_value(body, "Summary", subject)
        why = _body_value(body, "Why", "The repository does not record a reason.")
        risk = _body_value(body, "Risk", "No explicit risk was recorded.")
        events.append(
            {
                "id": event_id,
                "commit_hash": commit_hash,
                "short_hash": short_hash,
                "occurred_at": date,
                "author": author,
                "type": event_type,
                "title": _title(subject),
                "summary": summary,
                "why": why,
                "certainty": "confirmed",
                "confidence": 0.98,
                "files": files,
                "evidence": [
                    {
                        "kind": "commit",
                        "label": f"Commit {short_hash}",
                        "value": subject,
                    },
                    {
                        "kind": "diff",
                        "label": f"{len(files)} changed file{'s' if len(files) != 1 else ''}",
                        "value": ", ".join(item["path"] for item in files),
                    },
                ],
                "risks": [risk],
                "related_event_ids": related,
            }
        )

    return {
        "project": {
            "id": "orbitcart",
            "name": "OrbitCart",
            "description": "Checkout service with a traceable pricing incident",
            "branch": _git(repository, "branch", "--show-current").strip() or "main",
            "repository_path": str(repository),
        },
        "events": events,
        "stats": {
            "commits": len(events),
            "bugs": sum(event["type"] == "bug" for event in events),
            "files_touched": len({item["path"] for event in events for item in event["files"]}),
            "confirmed": sum(event["certainty"] == "confirmed" for event in events),
        },
    }

