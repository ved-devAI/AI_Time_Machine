"""Local developer workflow for analyzing and serving a Git repository."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from app.git_ingest import GitRepositoryError, read_change_context, read_timeline
from app.server import run_server


def _write_json(payload: Any, output: Path | None) -> None:
    content = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if output is None:
        print(content, end="")
        return
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"Wrote {output}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python3 -m app.cli",
        description="Analyze local Git history without an API key.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser("analyze", help="Print a normalized Git timeline")
    analyze.add_argument("repository", type=Path)
    analyze.add_argument("--branch", default="HEAD", help="Branch, tag, or commit to analyze")
    analyze.add_argument("--output", type=Path, help="Write JSON to this local path")

    serve = commands.add_parser("serve", help="Serve a repository in the browser UI")
    serve.add_argument("repository", type=Path, nargs="?", default=Path("."))
    serve.add_argument("--branch", default="HEAD", help="Branch, tag, or commit to serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--open", action="store_true", help="Open the local workspace in a browser")

    context = commands.add_parser("context", help="Report evidence for a commit range")
    context.add_argument("repository", type=Path)
    context.add_argument("--base", required=True, help="Base branch or commit")
    context.add_argument("--head", default="HEAD", help="Head branch or commit")
    context.add_argument("--recent-limit", type=int, default=5)
    context.add_argument("--output", type=Path, help="Write JSON to this local path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "analyze":
            _write_json(read_timeline(args.repository, args.branch), args.output)
        elif args.command == "context":
            if args.recent_limit < 1:
                raise GitRepositoryError("--recent-limit must be at least 1.")
            _write_json(
                read_change_context(
                    args.repository,
                    args.base,
                    args.head,
                    args.recent_limit,
                ),
                args.output,
            )
        else:
            if not 1 <= args.port <= 65535:
                raise GitRepositoryError("--port must be between 1 and 65535.")
            run_server(args.repository, args.branch, args.host, args.port, args.open)
        return 0
    except (GitRepositoryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
