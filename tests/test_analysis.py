from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.analysis import (
    ANALYSIS_SCHEMA,
    AnalysisError,
    analyze_bug_origin,
    deterministic_investigation,
    evidence_digest,
    load_codex_artifact,
    validate_analysis,
)
from app.git_ingest import read_timeline


ROOT = Path(__file__).resolve().parents[1]
ORBITCART = ROOT / ".data" / "orbitcart"


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not ORBITCART.exists():
            subprocess.run([sys.executable, "scripts/create_orbitcart.py"], cwd=ROOT, check=True)
        cls.timeline = read_timeline(ORBITCART)

    def test_fallback_identifies_cache_commit_as_origin(self) -> None:
        analysis = deterministic_investigation(self.timeline)
        origin = next(event for event in self.timeline["events"] if event["id"] == analysis["origin_event_id"])
        self.assertIn("cache product prices", origin["title"].lower())
        self.assertEqual([item["role"] for item in analysis["causal_chain"]], [
            "pressure", "origin", "symptom", "containment", "resolution", "verification"
        ])

    def test_no_key_returns_transparent_fallback(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = analyze_bug_origin(self.timeline)
        self.assertEqual(result["source"], "evidence-fallback")
        self.assertEqual(result["delivery"], "fallback")
        self.assertIsNone(result["model"])

    def test_schema_is_strict_and_requires_evidence_fields(self) -> None:
        self.assertFalse(ANALYSIS_SCHEMA["additionalProperties"])
        self.assertIn("origin_event_id", ANALYSIS_SCHEMA["required"])
        chain = ANALYSIS_SCHEMA["properties"]["causal_chain"]["items"]
        self.assertFalse(chain["additionalProperties"])
        self.assertIn("evidence_refs", chain["required"])

    def test_live_result_is_labeled_and_cached(self) -> None:
        model_result = deterministic_investigation(self.timeline)
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "analysis.json"
            with (
                patch.dict(os.environ, {
                    "OPENAI_API_KEY": "test-key",
                    "OPENAI_MODEL": "gpt-5.6",
                    "AI_TIME_MACHINE_ANALYSIS_MODE": "live",
                }, clear=True),
                patch("app.analysis.request_gpt_analysis", return_value=model_result) as request,
            ):
                result = analyze_bug_origin(self.timeline, cache)
            self.assertEqual(result["source"], "gpt-5.6")
            self.assertEqual(result["delivery"], "live")
            self.assertTrue(cache.exists())
            request.assert_called_once()

    def test_validator_rejects_evidence_from_a_different_event(self) -> None:
        analysis = deterministic_investigation(self.timeline)
        analysis["causal_chain"][0]["evidence_refs"] = ["not-a-real-commit"]
        with self.assertRaises(AnalysisError):
            validate_analysis(analysis, self.timeline)

    def test_valid_codex_artifact_is_loaded_offline(self) -> None:
        analysis = deterministic_investigation(self.timeline)
        envelope = {
            "artifact_version": 1,
            "provenance": {
                "generator": "codex exec",
                "model": "gpt-5.6-sol",
                "generated_at": "2026-07-15T00:00:00+00:00",
                "evidence_sha256": evidence_digest(self.timeline),
            },
            "analysis": analysis,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.json"
            path.write_text(json.dumps(envelope), encoding="utf-8")
            result = load_codex_artifact(self.timeline, path)
        self.assertEqual(result["source"], "codex-gpt-5.6")
        self.assertEqual(result["delivery"], "validated-artifact")

    def test_artifact_with_wrong_evidence_digest_is_rejected(self) -> None:
        envelope = {
            "artifact_version": 1,
            "provenance": {
                "generator": "codex exec",
                "model": "gpt-5.6-sol",
                "evidence_sha256": "wrong",
            },
            "analysis": deterministic_investigation(self.timeline),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.json"
            path.write_text(json.dumps(envelope), encoding="utf-8")
            with self.assertRaises(AnalysisError):
                load_codex_artifact(self.timeline, path)

    def test_incomplete_causal_chain_is_rejected(self) -> None:
        analysis = deterministic_investigation(self.timeline)
        analysis["causal_chain"].pop()
        with self.assertRaises(AnalysisError):
            validate_analysis(analysis, self.timeline)

    def test_committed_codex_artifact_matches_current_evidence(self) -> None:
        artifact = ROOT / "artifacts" / "orbitcart" / "bug-origin.codex.json"
        result = analyze_bug_origin(self.timeline, artifact_path=artifact)
        self.assertEqual(result["source"], "codex-gpt-5.6")
        self.assertEqual(result["model"], "gpt-5.6-sol")
        self.assertEqual(len(result["causal_chain"]), 6)
        self.assertTrue(result["provenance"]["codex_session_id"])


if __name__ == "__main__":
    unittest.main()
