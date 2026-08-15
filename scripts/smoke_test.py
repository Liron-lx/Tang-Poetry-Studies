#!/usr/bin/env python3
"""Smoke-test the static server's formal pages and local resources."""

from __future__ import annotations

import argparse
import sys
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import urlopen


PAGES = [
    "index.html",
    "interactive.html",
    "geography.html",
    "poetry-emotion.html",
    "word-association.html",
    "keyword-river.html",
    "circular_sankey.html",
    "可行情感1.html",
    "词频可视化.html",
    "xiayi-scroll.html",
]
RESOURCES = [
    "assets/css/common.css",
    "assets/js/navigation.js",
    "data/poetry_with_detailed_clusters_sankey.csv",
    "data/地方名称及经纬度.csv",
    "data/tang_dynasty_detailed_boundary.json",
]


def check(base_url: str) -> list[str]:
    errors: list[str] = []
    for relative_path in PAGES + RESOURCES:
        url = f"{base_url.rstrip('/')}/{quote(relative_path, safe='/')}"
        try:
            with urlopen(url, timeout=5) as response:
                if response.status != 200:
                    errors.append(f"{relative_path}: HTTP {response.status}")
        except (OSError, URLError) as exc:
            errors.append(f"{relative_path}: {exc}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    problems = check(args.base_url)
    if problems:
        print("Smoke test failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Smoke test passed: {len(PAGES)} pages and {len(RESOURCES)} resources reachable.")
