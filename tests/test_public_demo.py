from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class PublicDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, "scripts/build_public_demo.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_snapshot_contains_all_runtime_payloads(self) -> None:
        data = DIST / "demo-data"
        expected = {
            "timeline.json",
            "investigation.json",
            "ask-pricing-complexity.json",
            "ask-stale-price-origin.json",
            "ask-change-risk.json",
        }
        self.assertEqual(expected, {path.name for path in data.glob("*.json")})

    def test_snapshot_preserves_verified_codex_provenance(self) -> None:
        investigation = json.loads((DIST / "demo-data" / "investigation.json").read_text())
        answer = json.loads((DIST / "demo-data" / "ask-stale-price-origin.json").read_text())
        self.assertEqual("codex-gpt-5.6", investigation["source"])
        self.assertEqual("validated-artifact", investigation["delivery"])
        self.assertEqual("codex-gpt-5.6", answer["source"])
        self.assertTrue(investigation["provenance"]["evidence_sha256"])

    def test_snapshot_uses_relative_assets_and_explicit_mode(self) -> None:
        index = (DIST / "index.html").read_text()
        config = (DIST / "runtime-config.js").read_text()
        self.assertIn('href="./styles.css"', index)
        self.assertIn('src="./app.js"', index)
        self.assertIn('mode: "snapshot"', config)


if __name__ == "__main__":
    unittest.main()
