from __future__ import annotations

import unittest

from scripts.evaluate_grounding import run_evaluation


class GroundingEvaluationTests(unittest.TestCase):
    def test_committed_artifacts_achieve_full_grounding_score(self) -> None:
        report = run_evaluation()
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["score"], 100.0)
        self.assertEqual(report["passed"], report["total"])


if __name__ == "__main__":
    unittest.main()
