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
    def test_index_contains_the_five_figma_prologue_states(self) -> None:
        index = (Path(__file__).parents[1] / "index.html").read_text(encoding="utf-8")
        for phase in ("splash", "cover", "poem", "preface", "unfurled"):
            self.assertIn(f'data-prologue-phase="{phase}"', index)
        for control_id in ("beginBtn", "openBookBtn", "prefaceBtn", "unfurlBtn"):
            self.assertIn(f'id="{control_id}"', index)


if __name__ == "__main__":
    unittest.main()
