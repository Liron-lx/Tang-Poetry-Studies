import unittest
from pathlib import Path

from smoke_test import PAGES


class FormalRouteTest(unittest.TestCase):
    def test_smoke_test_covers_only_formal_pages(self) -> None:
        self.assertEqual(
            PAGES,
            [
                "index.html",
                "xiayi-scroll.html",
                "interactive.html",
                "poets.html",
                "emotions.html",
                "keyword-river.html",
            ],
        )


class PrologueMarkupTest(unittest.TestCase):
    def test_index_contains_the_selected_two_stage_intro_and_scene(self) -> None:
        index = (Path(__file__).parents[1] / "index.html").read_text(encoding="utf-8")
        for control_id in ("cover-stage", "序章-stage", "startExplore", "unfurlBtn", "scene-stage"):
            self.assertIn(f'id="{control_id}"', index)
        self.assertIn('data-scene-state="locked"', index)
        self.assertIn('class="scene-directory"', index)


if __name__ == "__main__":
    unittest.main()
