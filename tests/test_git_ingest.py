from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from app.git_ingest import read_timeline


ROOT = Path(__file__).resolve().parents[1]
ORBITCART = ROOT / ".data" / "orbitcart"


class GitIngestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not ORBITCART.exists():
            subprocess.run([sys.executable, "scripts/create_orbitcart.py"], cwd=ROOT, check=True)

    def test_reads_all_curated_commits(self) -> None:
        timeline = read_timeline(ORBITCART)
        self.assertEqual(timeline["stats"]["commits"], 12)
        self.assertEqual(len(timeline["events"]), 12)

    def test_stale_price_incident_has_git_evidence(self) -> None:
        events = read_timeline(ORBITCART)["events"]
        incident = next(event for event in events if "stale checkout" in event["title"].lower())
        self.assertEqual(incident["type"], "bug")
        self.assertEqual(incident["certainty"], "confirmed")
        self.assertTrue(any(item["path"] == "history/issues/OC-52.md" for item in incident["files"]))

    def test_file_overlap_builds_history_connections(self) -> None:
        events = read_timeline(ORBITCART)["events"]
        cache_fix = next(event for event in events if "catalog version" in event["title"].lower())
        self.assertGreaterEqual(len(cache_fix["related_event_ids"]), 1)


if __name__ == "__main__":
    unittest.main()

