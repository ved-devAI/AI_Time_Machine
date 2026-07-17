from __future__ import annotations

import json
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from app.git_ingest import (
    GitRepositoryError,
    NOT_RECORDED,
    read_change_context,
    read_timeline,
)
from app.analysis import AnalysisError
from app.cli import parse_args
from app.repo_questions import QUESTIONS, answer_question, validate_answer


ROOT = Path(__file__).resolve().parents[1]


class RealRepoModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        # A directory name alone must never opt a repository into OrbitCart's
        # committed analysis artifacts.
        self.repository = Path(self.temporary.name) / "orbitcart"
        self.repository.mkdir()
        self.git("init")
        self.git("config", "user.name", "Test Developer")
        self.git("config", "user.email", "developer@example.com")
        self.git("branch", "-M", "main")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ("git", *args),
            cwd=self.repository,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def commit_file(self, path: str, content: str, subject: str) -> str:
        target = self.repository / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.git("add", path)
        self.git("commit", "-m", subject)
        return self.git("rev-parse", "HEAD")

    def commit_files(self, files: dict[str, str], subject: str) -> str:
        for path, content in files.items():
            target = self.repository / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        self.git("add", *files)
        self.git("commit", "-m", subject)
        return self.git("rev-parse", "HEAD")

    def test_unstructured_commits_keep_missing_rationale_explicit(self) -> None:
        self.commit_file("src/widget.py", "value = 1\n", "feat: add widget")

        timeline = read_timeline(self.repository)
        event = timeline["events"][0]

        self.assertEqual(event["summary"], "feat: add widget")
        self.assertEqual(event["why"], NOT_RECORDED)
        self.assertEqual(event["risks"], [NOT_RECORDED])
        self.assertEqual(event["rationale_certainty"], "missing-evidence")
        self.assertEqual(event["type"], "feature")
        self.assertEqual(event["type_certainty"], "inferred")
        self.assertEqual(timeline["project"]["mode"], "real-repo")

    def test_context_reports_changed_files_history_fixes_and_range_commits(self) -> None:
        base = self.commit_file("src/widget.py", "value = 1\n", "Add widget")
        head = self.commit_file("src/widget.py", "value = 2\n", "fix: correct widget")

        context = read_change_context(self.repository, base, head)

        self.assertEqual(context["changed_files"], [{"path": "src/widget.py", "status": "M"}])
        self.assertEqual(len(context["range_commits"]), 1)
        self.assertEqual(context["range_commits"][0]["commit"], head[:7])
        self.assertEqual(len(context["recent_commits_by_file"]["src/widget.py"]), 2)
        self.assertEqual(context["connected_incidents_and_fixes"][0]["type"], "fix")
        self.assertEqual(context["recorded_risks"], [])

    def test_analyze_cli_emits_normalized_json(self) -> None:
        self.commit_file("README.md", "proof\n", "Document proof")
        result = subprocess.run(
            (sys.executable, "-m", "app.cli", "analyze", str(self.repository)),
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["stats"]["commits"], 1)
        self.assertEqual(payload["project"]["name"], "orbitcart")
        self.assertEqual(payload["project"]["mode"], "real-repo")

    def test_serve_defaults_to_current_repository_and_can_open_browser(self) -> None:
        args = parse_args(["serve", "--open"])
        self.assertEqual(args.repository, Path("."))
        self.assertTrue(args.open)

    def test_adaptive_questions_are_deterministic_and_event_grounded(self) -> None:
        base = self.commit_files(
            {"src/widget.py": "value = 1\n", "config/widget.json": "{}\n"},
            "feat: add widget",
        )
        self.commit_file("src/widget.py", "value = 0\n", "bug: record widget failure")
        head = self.commit_file("src/widget.py", "value = 2\n", "fix: correct widget")
        timeline = read_timeline(self.repository)
        context = read_change_context(self.repository, base, head)

        answers = [answer_question(timeline, item["id"], context) for item in QUESTIONS]

        self.assertEqual([item["question_id"] for item in answers], [item["id"] for item in QUESTIONS])
        self.assertTrue(all(item["source"] == "local-evidence-engine" for item in answers))
        self.assertTrue(all(item["model"] is None for item in answers))
        self.assertTrue(all(item["evidence"] for item in answers))
        self.assertIn("src/widget.py", answers[2]["evidence"][0]["evidence_refs"])

    def test_adaptive_question_rejects_cross_event_file_reference(self) -> None:
        self.commit_files(
            {"src/widget.py": "value = 1\n", "config/widget.json": "{}\n"},
            "Add widget",
        )
        timeline = read_timeline(self.repository)
        answer = copy.deepcopy(answer_question(timeline, "recent-changes"))
        answer["evidence"][0]["evidence_refs"].append("invented/file.py")

        with self.assertRaisesRegex(AnalysisError, "not grounded"):
            validate_answer(answer, timeline)

    def test_invalid_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(GitRepositoryError, "does not exist"):
            read_timeline(self.repository / "missing")

    def test_non_git_directory_is_rejected(self) -> None:
        directory = Path(self.temporary.name) / "not-git"
        directory.mkdir()
        with self.assertRaisesRegex(GitRepositoryError, "Not a Git repository"):
            read_timeline(directory)

    def test_empty_history_is_rejected(self) -> None:
        with self.assertRaisesRegex(GitRepositoryError, "has no commits"):
            read_timeline(self.repository)

    def test_unknown_branch_and_range_are_rejected(self) -> None:
        self.commit_file("README.md", "proof\n", "Document proof")
        with self.assertRaisesRegex(GitRepositoryError, "Unknown branch or commit"):
            read_timeline(self.repository, "missing-branch")
        with self.assertRaisesRegex(GitRepositoryError, "Unknown base revision"):
            read_change_context(self.repository, "missing-base", "HEAD")
        with self.assertRaisesRegex(GitRepositoryError, "Unknown head revision"):
            read_change_context(self.repository, "HEAD", "missing-head")


if __name__ == "__main__":
    unittest.main()
