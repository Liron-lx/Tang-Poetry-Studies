#!/usr/bin/env python3
"""Validate the project's local data files and basic corpus invariants."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

EXPECTED_POETRY_COLUMNS = ["作者", "诗歌名", "诗歌原文", "聚类类别"]
EXPECTED_LOCATION_COLUMNS = ["现今地名", "总频次", "包含历史地名", "地理坐标", "类型说明"]
EXPECTED_POETRY_ROWS = 100
COORDINATE_PATTERN = re.compile(r"^\s*(-?\d+(?:\.\d+)?)°?\s*[NS]?\s*,\s*(-?\d+(?:\.\d+)?)°?\s*[EW]?\s*$", re.I)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_csv(path: Path, expected_columns: list[str], errors: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        fail(errors, f"missing file: {path.relative_to(ROOT)}")
        return []
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != expected_columns:
                fail(errors, f"{path.relative_to(ROOT)} columns: expected {expected_columns}, got {reader.fieldnames}")
            return list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        fail(errors, f"cannot read {path.relative_to(ROOT)}: {exc}")
        return []


def validate() -> list[str]:
    errors: list[str] = []
    poetry = read_csv(DATA / "poetry_with_detailed_clusters_sankey.csv", EXPECTED_POETRY_COLUMNS, errors)
    locations = read_csv(DATA / "地方名称及经纬度.csv", EXPECTED_LOCATION_COLUMNS, errors)

    if len(poetry) != EXPECTED_POETRY_ROWS:
        fail(errors, f"poetry row count: expected {EXPECTED_POETRY_ROWS}, got {len(poetry)}")
    for index, row in enumerate(poetry, start=2):
        if not all(row.get(column, "").strip() for column in EXPECTED_POETRY_COLUMNS):
            fail(errors, f"poetry row {index} contains an empty required field")

    for index, row in enumerate(locations, start=2):
        try:
            frequency = int(row.get("总频次", ""))
            if frequency < 0:
                raise ValueError("negative")
        except ValueError:
            fail(errors, f"location row {index} has invalid 总频次: {row.get('总频次')!r}")
        match = COORDINATE_PATTERN.match(row.get("地理坐标", ""))
        if not match:
            fail(errors, f"location row {index} has invalid 地理坐标: {row.get('地理坐标')!r}")
        elif not (-90 <= float(match.group(1)) <= 90 and -180 <= float(match.group(2)) <= 180):
            fail(errors, f"location row {index} has out-of-range 地理坐标: {row.get('地理坐标')!r}")

    boundary = DATA / "tang_dynasty_detailed_boundary.json"
    if not boundary.exists():
        fail(errors, f"missing file: {boundary.relative_to(ROOT)}")
    else:
        try:
            with boundary.open(encoding="utf-8") as handle:
                parsed = json.load(handle)
            if not isinstance(parsed, dict):
                fail(errors, "tang_dynasty_detailed_boundary.json must contain a JSON object")
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            fail(errors, f"cannot parse {boundary.relative_to(ROOT)}: {exc}")

    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("Project validation failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Project validation passed: {EXPECTED_POETRY_ROWS} poetry rows and local data schemas are valid.")
