from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.analysis import ANALYSIS_SCHEMA, analyze_bug_origin, deterministic_investigation
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
                patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "gpt-5.6"}, clear=True),
                patch("app.analysis.request_gpt_analysis", return_value=model_result) as request,
            ):
                result = analyze_bug_origin(self.timeline, cache)
            self.assertEqual(result["source"], "gpt-5.6")
            self.assertEqual(result["delivery"], "live")
            self.assertTrue(cache.exists())
            request.assert_called_once()


if __name__ == "__main__":
    unittest.main()
