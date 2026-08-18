import unittest

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


if __name__ == "__main__":
    unittest.main()
