from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STYLES = (ROOT / "frontend" / "styles.css").read_text(encoding="utf-8")


class ResponsiveCssTests(unittest.TestCase):
    def test_interface_text_has_a_ten_pixel_minimum(self) -> None:
        undersized = re.findall(
            r"(?:font-size|font)\s*:[^;{}]*?(?<!\d)([6-9])px",
            STYLES,
        )
        self.assertEqual([], undersized)
        self.assertIn("--muted: #a6b6c6;", STYLES)
        self.assertIn("--muted-strong: #c0cfdd;", STYLES)

    def test_desktop_workspace_panels_own_their_scroll_regions(self) -> None:
        self.assertIn(".workspace { display: grid;", STYLES)
        self.assertIn("height: calc(100vh - 320px);", STYLES)
        self.assertIn(".timeline-panel { border-right: 1px solid var(--line); min-width: 0; min-height: 0;", STYLES)
        self.assertIn(".detail-panel { min-width: 0; min-height: 0; overflow-y: auto;", STYLES)

    def test_filter_labels_are_centered_inside_fixed_height_controls(self) -> None:
        self.assertIn(
            ".filter { flex: none; height: 36px; display: inline-flex; align-items: center; justify-content: center;",
            STYLES,
        )
        self.assertIn("font-size: 11px; line-height: 1;", STYLES)

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
        self.assertIn(".workspace { grid-template-columns: 1fr; height: auto; max-height: none;", tablet)
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
