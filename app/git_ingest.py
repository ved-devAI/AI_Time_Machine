"""Extract evidence-preserving timelines and change context from local Git."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Iterable


FIELD = "\x1f"
RECORD = "\x1e"
NOT_RECORDED = "not recorded"
DEFAULT_ORBITCART = Path(__file__).resolve().parents[1] / ".data" / "orbitcart"


class GitRepositoryError(ValueError):
    """Raised when a repository or requested revision cannot be analyzed."""


def _git(repository: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ("git", *args),
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise GitRepositoryError("Git is required but was not found on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or "Git command failed."
        raise GitRepositoryError(message) from exc
    return result.stdout


def validate_repository(repository: Path) -> Path:
    """Return a canonical worktree root or raise a user-facing validation error."""

    repository = repository.expanduser().resolve()
    if not repository.exists():
        raise GitRepositoryError(f"Repository path does not exist: {repository}")
    if not repository.is_dir():
        raise GitRepositoryError(f"Repository path is not a directory: {repository}")
    try:
        inside = _git(repository, "rev-parse", "--is-inside-work-tree").strip()
    except GitRepositoryError as exc:
        raise GitRepositoryError(f"Not a Git repository: {repository}") from exc
    if inside != "true":
        raise GitRepositoryError(f"Not a Git worktree: {repository}")
    root = Path(_git(repository, "rev-parse", "--show-toplevel").strip()).resolve()
    return root


def _validate_revision(repository: Path, revision: str, label: str) -> str:
    if not revision or revision.startswith("-") or any(char.isspace() for char in revision):
        raise GitRepositoryError(f"Invalid {label} revision: {revision!r}")
    try:
        return _git(repository, "rev-parse", "--verify", f"{revision}^{{commit}}").strip()
    except GitRepositoryError as exc:
        raise GitRepositoryError(f"Unknown {label} revision: {revision}") from exc


def _body_value(body: str, label: str, fallback: str = NOT_RECORDED) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", body, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else fallback


def _event_type(subject: str, body: str) -> tuple[str, str]:
    known_types = {
        "feat": "feature",
        "feature": "feature",
        "bug": "bug",
        "fix": "fix",
        "refactor": "refactor",
        "perf": "performance",
        "performance": "performance",
        "revert": "rollback",
        "rollback": "rollback",
        "test": "test",
        "change": "change",
    }
    explicit = _body_value(body, "Type", "").lower()
    if explicit in known_types:
        return known_types[explicit], "confirmed"
    prefix = subject.split("(", 1)[0].split(":", 1)[0].lower()
    if prefix in known_types and ":" in subject:
        return known_types[prefix], "inferred"
    return "change", "confirmed"


def _title(subject: str) -> str:
    value = subject.split(":", 1)[1].strip() if ":" in subject else subject
    return value[:1].upper() + value[1:]


def _parse_name_status(output: str) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        status = fields[0]
        if status.startswith(("R", "C")) and len(fields) >= 3:
            files.append(
                {"path": fields[2], "status": status[:1], "previous_path": fields[1]}
            )
        elif len(fields) >= 2:
            files.append({"path": fields[1], "status": status[:1]})
    return files


def _files(repository: Path, commit_hash: str) -> list[dict[str, str]]:
    return _parse_name_status(
        _git(
            repository,
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-status",
            "-r",
            "-M",
            commit_hash,
        )
    )


def _project(repository: Path, branch: str) -> dict[str, str]:
    # Only the bundled deterministic repository may use committed OrbitCart
    # artifacts. A generic repository with the same directory name stays generic.
    if repository == DEFAULT_ORBITCART.resolve():
        return {
            "id": "orbitcart",
            "name": "OrbitCart",
            "description": "Checkout service with a traceable pricing incident",
            "branch": branch,
            "repository_path": str(repository),
            "mode": "orbitcart",
        }
    name = repository.name or "repository"
    project_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "repository"
    return {
        "id": project_id,
        "name": name,
        "description": "Local repository timeline grounded in Git evidence",
        "branch": branch,
        "repository_path": str(repository),
        "mode": "real-repo",
    }


def _suggest_base(repository: Path, revision: str, head_hash: str) -> str:
    for candidate in ("main", "master", "origin/main", "origin/master"):
        try:
            candidate_hash = _validate_revision(repository, candidate, "base")
        except GitRepositoryError:
            continue
        if candidate_hash != head_hash:
            return candidate
    try:
        _validate_revision(repository, f"{revision}~1", "base")
        return f"{revision}~1"
    except GitRepositoryError:
        return revision


def _timeline_records(repository: Path, revision: str) -> Iterable[list[str]]:
    raw = _git(
        repository,
        "log",
        "--reverse",
        "--date=iso-strict",
        f"--pretty=format:%H{FIELD}%h{FIELD}%aI{FIELD}%an{FIELD}%s{FIELD}%b{RECORD}",
        revision,
    )
    for record in raw.split(RECORD):
        # Unit and record separators are valid delimiters here and are treated as
        # whitespace by ``str.strip()``, so trim line endings only.
        record = record.strip("\r\n")
        if record:
            yield record.split(FIELD)


def read_timeline(repository: Path, revision: str = "HEAD") -> dict[str, Any]:
    """Read commits reachable from ``revision`` into the normalized UI contract."""

    repository = validate_repository(repository)
    if _git(repository, "rev-list", "--all", "--count").strip() == "0":
        raise GitRepositoryError(f"Repository has no commits: {repository}")
    head_hash = _validate_revision(repository, revision, "branch or commit")
    is_orbitcart = repository == DEFAULT_ORBITCART.resolve()
    events: list[dict[str, Any]] = []
    previous_by_file: dict[str, str] = {}

    for parts in _timeline_records(repository, revision):
        if len(parts) < 6:
            continue
        commit_hash, short_hash, date, author, subject = parts[:5]
        body = FIELD.join(parts[5:]).strip()
        files = _files(repository, commit_hash)
        event_id = f"event-{short_hash}"
        overlap_paths = {
            path
            for item in files
            for path in (item["path"], item.get("previous_path"))
            if path
        }
        related = sorted(
            {previous_by_file[path] for path in overlap_paths if path in previous_by_file}
        )[-3:]
        for path in overlap_paths:
            previous_by_file[path] = event_id

        event_type, type_certainty = _event_type(subject, body)
        why = _body_value(body, "Why")
        risk = _body_value(body, "Risk")
        events.append(
            {
                "id": event_id,
                "commit_hash": commit_hash,
                "short_hash": short_hash,
                "occurred_at": date,
                "author": author,
                "type": event_type,
                "type_certainty": type_certainty,
                "title": _title(subject),
                "summary": _body_value(body, "Summary", subject),
                "why": why,
                "rationale_certainty": "missing-evidence" if why == NOT_RECORDED else "confirmed",
                "certainty": "confirmed",
                "confidence": 0.98 if is_orbitcart else None,
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

    if not events:
        raise GitRepositoryError(f"Repository has no commits reachable from {revision}: {repository}")
    current_branch = _git(repository, "branch", "--show-current").strip()
    branch = current_branch if revision == "HEAD" and current_branch else revision
    project = _project(repository, branch)
    project["suggested_base"] = _suggest_base(repository, revision, head_hash)
    return {
        "project": project,
        "events": events,
        "stats": {
            "commits": len(events),
            "bugs": sum(event["type"] == "bug" for event in events),
            "files_touched": len(
                {item["path"] for event in events for item in event["files"]}
            ),
            "confirmed": sum(event["certainty"] == "confirmed" for event in events),
        },
    }


def read_change_context(
    repository: Path,
    base: str,
    head: str = "HEAD",
    recent_limit: int = 5,
) -> dict[str, Any]:
    """Build evidence-only context for files changed between two revisions."""

    repository = validate_repository(repository)
    base_hash = _validate_revision(repository, base, "base")
    head_hash = _validate_revision(repository, head, "head")
    changed_files = _parse_name_status(
        _git(repository, "diff", "--name-status", "-M", base_hash, head_hash)
    )
    timeline = read_timeline(repository, head_hash)
    events = timeline["events"]
    event_by_hash = {event["commit_hash"]: event for event in events}
    range_hashes = _git(repository, "rev-list", "--reverse", f"{base_hash}..{head_hash}").splitlines()
    range_commits = [event_by_hash[item] for item in range_hashes if item in event_by_hash]

    recent_by_file: dict[str, list[dict[str, str]]] = {}
    for changed in changed_files:
        path = changed["path"]
        raw_hashes = _git(
            repository,
            "log",
            f"-{recent_limit}",
            "--pretty=format:%H",
            head_hash,
            "--",
            path,
        ).splitlines()
        recent_by_file[path] = [
            {
                "event_id": event_by_hash[item]["id"],
                "commit": event_by_hash[item]["short_hash"],
                "title": event_by_hash[item]["title"],
                "type": event_by_hash[item]["type"],
            }
            for item in raw_hashes
            if item in event_by_hash
        ]

    changed_paths = {item["path"] for item in changed_files}
    touching_events = [
        event
        for event in events
        if changed_paths.intersection(item["path"] for item in event["files"])
    ]
    incidents_and_fixes = [
        {
            "event_id": event["id"],
            "commit": event["short_hash"],
            "type": event["type"],
            "title": event["title"],
            "files": [
                item["path"] for item in event["files"] if item["path"] in changed_paths
            ],
        }
        for event in touching_events
        if event["type"] in {"bug", "fix", "rollback"}
    ]
    recorded_risks = [
        {
            "event_id": event["id"],
            "commit": event["short_hash"],
            "risk": risk,
        }
        for event in touching_events
        for risk in event["risks"]
        if risk != NOT_RECORDED
    ]
    missing_rationale = [
        event for event in range_commits if event["why"] == NOT_RECORDED
    ]
    incident_or_fix_paths = {
        path
        for item in incidents_and_fixes
        for path in item["files"]
    }
    paths_without_incident_or_fix = sorted(changed_paths - incident_or_fix_paths)
    missing_evidence: list[str] = []
    if not changed_files:
        missing_evidence.append(
            "No changed files were found between the selected revisions."
        )
    else:
        if missing_rationale:
            missing_evidence.append(
                f"{len(missing_rationale)} of {len(range_commits)} range commits do not "
                "record rationale in Git commit metadata."
            )
        if not recorded_risks:
            missing_evidence.append(
                "No structured risk is recorded in Git history for the changed files."
            )
        if paths_without_incident_or_fix:
            missing_evidence.append(
                "No connected incident or fix history was found for: "
                + ", ".join(paths_without_incident_or_fix)
                + "."
            )
        missing_evidence.append(
            "Deployment records, issue and review systems, and production telemetry "
            "are outside this local Git-only evidence boundary."
        )
    return {
        "repository": {
            "name": timeline["project"]["name"],
            "path": str(repository),
        },
        "range": {
            "base": base,
            "base_commit": base_hash,
            "head": head,
            "head_commit": head_hash,
        },
        "changed_files": changed_files,
        "range_commits": [
            {
                "event_id": event["id"],
                "commit": event["short_hash"],
                "title": event["title"],
                "files": [item["path"] for item in event["files"]],
            }
            for event in range_commits
        ],
        "recent_commits_by_file": recent_by_file,
        "connected_incidents_and_fixes": incidents_and_fixes,
        "recorded_risks": recorded_risks,
        "missing_evidence": missing_evidence,
    }
