from __future__ import annotations

import copy
import subprocess
import sys
import unittest
from pathlib import Path

from app.analysis import AnalysisError
from app.ask_repo import (
    QUESTIONS,
    ask_repo,
    deterministic_answers,
    validate_answer_set,
)
from app.git_ingest import read_timeline


ROOT = Path(__file__).resolve().parents[1]
ORBITCART = ROOT / ".data" / "orbitcart"


class AskRepoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not ORBITCART.exists():
            subprocess.run([sys.executable, "scripts/create_orbitcart.py"], cwd=ROOT, check=True)
        cls.timeline = read_timeline(ORBITCART)

    def test_fallback_answers_all_supported_questions(self) -> None:
        payload = validate_answer_set(deterministic_answers(self.timeline), self.timeline)
        self.assertEqual(
            [item["question_id"] for item in payload["answers"]],
            [item["id"] for item in QUESTIONS],
        )

    def test_rejects_unknown_event_reference(self) -> None:
        payload = copy.deepcopy(deterministic_answers(self.timeline))
        payload["answers"][0]["evidence"][0]["event_id"] = "event-invented"
        with self.assertRaises(AnalysisError):
            validate_answer_set(payload, self.timeline)

    def test_rejects_file_from_a_different_event(self) -> None:
        payload = copy.deepcopy(deterministic_answers(self.timeline))
        payload["answers"][0]["evidence"][0]["evidence_refs"][1] = "not/a/real/file.py"
        with self.assertRaises(AnalysisError):
            validate_answer_set(payload, self.timeline)

    def test_rejects_unsupported_question(self) -> None:
        with self.assertRaises(AnalysisError):
            ask_repo(self.timeline, "write-the-fix")

    def test_returns_transparent_fallback_without_artifact(self) -> None:
        result = ask_repo(self.timeline, "change-risk")
        self.assertEqual(result["source"], "evidence-fallback")
        self.assertGreaterEqual(len(result["evidence"]), 2)

    def test_committed_codex_artifact_answers_all_questions(self) -> None:
        artifact = ROOT / "artifacts" / "orbitcart" / "ask-repo.codex.json"
        for question in QUESTIONS:
            result = ask_repo(self.timeline, question["id"], artifact)
            self.assertEqual(result["source"], "codex-gpt-5.6")
            self.assertEqual(result["model"], "gpt-5.6-sol")
            self.assertGreaterEqual(len(result["evidence"]), 2)
            self.assertTrue(result["provenance"]["codex_session_id"])


if __name__ == "__main__":
    unittest.main()
