from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STYLES = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")


class ResponsiveCssTests(unittest.TestCase):
    def _media_block(self, width: int) -> str:
        marker = f"@media (max-width: {width}px)"
        start = STYLES.index(marker)
        opening = STYLES.index("{", start)
        depth = 0
        for index in range(opening, len(STYLES)):
            if STYLES[index] == "{":
                depth += 1
            elif STYLES[index] == "}":
                depth -= 1
                if depth == 0:
                    return STYLES[opening + 1:index]
        self.fail(f"Unclosed {marker} block")

    def test_tablet_layout_stacks_primary_regions(self) -> None:
        tablet = self._media_block(980)
        self.assertIn(".workspace { grid-template-columns: 1fr;", tablet)
        self.assertIn(".ask-repo { grid-template-columns: 1fr;", tablet)
        self.assertIn(".branch-review-header { grid-template-columns: 1fr;", tablet)
        self.assertIn(".trace-footer-grid { grid-template-columns: 1fr;", tablet)

    def test_mobile_layout_uses_single_column_answers(self) -> None:
        mobile = self._media_block(650)
        self.assertIn(
            ".ask-prompts, .ask-prompts.generic, .ask-evidence-grid { grid-template-columns: 1fr;",
            mobile,
        )
        self.assertIn(".branch-review-form { align-items: stretch; flex-direction: column;", mobile)
        self.assertIn(".context-grid { grid-template-columns: 1fr;", mobile)
        self.assertIn(".evidence-list, .related-list { grid-template-columns: 1fr;", mobile)
        self.assertIn(".repo-card { min-width: 0; }", mobile)
        self.assertIn(".trace-window { width: 100%;", mobile)
        self.assertIn(".trace-map { grid-template-columns: 1fr;", mobile)
        self.assertIn("overflow: visible;", mobile)


if __name__ == "__main__":
    unittest.main()
