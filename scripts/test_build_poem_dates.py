#!/usr/bin/env python3

import csv
import tempfile
import unittest
from pathlib import Path

from build_poem_dates import (
    classify_dating_status,
    classify_lookup_status,
    find_match,
    load_manual_overrides,
    merge_manual_override,
    request_json,
)


class DatingStatusTest(unittest.TestCase):
    def test_date_shapes_map_to_distinct_statuses(self) -> None:
        self.assertEqual(classify_dating_status("731", "731", "单年系年"), "exact")
        self.assertEqual(classify_dating_status("652", "653", "跨年范围"), "range")
        self.assertEqual(classify_dating_status("755", "759", "争议范围"), "disputed")
        self.assertEqual(classify_dating_status("", "", "未知"), "undated")


class ManualOverrideTest(unittest.TestCase):
    def test_manual_date_overrides_date_but_preserves_lookup_log(self) -> None:
        auto = {
            "record_id": "P004",
            "lookup_status": "endpoint_error",
            "lookup_note": "empty JSON response",
            "date_start": "",
            "date_end": "",
            "dating_status": "undated",
            "verification_status": "未匹配",
        }
        manual = {
            "record_id": "P004",
            "date_start": "684",
            "date_end": "684",
            "date_label": "684年",
            "date_precision": "单年系年",
            "dating_status": "exact",
            "review_status": "manual_single_source",
        }

        merged = merge_manual_override(auto, manual)

        self.assertEqual(merged["lookup_status"], "endpoint_error")
        self.assertEqual(merged["lookup_note"], "empty JSON response")
        self.assertEqual(merged["date_start"], "684")
        self.assertEqual(merged["verification_status"], "人工复核且有系年")

    def test_manual_loader_rejects_duplicate_record_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "manual.csv"
            path.write_text(
                "record_id,date_start\nP004,684\nP004,685\n",
                encoding="utf-8-sig",
            )

            with self.assertRaisesRegex(ValueError, "P004"):
                load_manual_overrides(path)


class LookupStatusTest(unittest.TestCase):
    def test_endpoint_error_is_not_reported_as_undated_evidence(self) -> None:
        status, note = classify_lookup_status(
            successful_queries=0,
            candidate_count=0,
            best_score=0.0,
            last_error="empty JSON response",
        )
        self.assertEqual(status, "endpoint_error")
        self.assertIn("empty JSON response", note)

    def test_successful_empty_search_is_no_result(self) -> None:
        status, _note = classify_lookup_status(1, 0, 0.0, "")
        self.assertEqual(status, "no_result")

    def test_low_scoring_candidate_is_ambiguous(self) -> None:
        status, _note = classify_lookup_status(1, 2, 0.30, "")
        self.assertEqual(status, "ambiguous_match")


class ApiCertificateTest(unittest.TestCase):
    def test_request_json_uses_a_working_certificate_store(self) -> None:
        """Catch regressions to a Python install with no usable default CA file."""
        poem = request_json("/api/Poem/31503?includeLinks=false", retries=1)
        self.assertEqual(poem["Id"], 31503)
        self.assertEqual(poem["Author"], "杜甫")

    def test_find_match_uses_normalized_title_and_accepts_script_variants(self) -> None:
        row = {
            "作者": "杜甫",
            "诗歌名": "横吹曲辞 后出塞五首 四",
            "诗歌原文": (
                "献凯日继踵，两蕃静无虞。渔阳豪侠地，击鼓吹笙竽。"
                "云帆转辽海，粳稻来东吴。越罗与楚练，照耀舆台躯。"
                "主将位益崇，气骄陵上都。边人不敢议，议者死路衢。"
            ),
        }
        outcome = find_match(row)
        self.assertEqual(outcome.poem["Id"], 31503)
        self.assertGreater(outcome.score, 0.45)
        self.assertEqual(outcome.query, "杜甫《后出塞五首 四》")
        self.assertEqual(outcome.status, "matched")

    def test_find_match_normalizes_traditional_author_characters(self) -> None:
        corpus = Path(__file__).parents[1] / "data/poetry_with_detailed_clusters_sankey.csv"
        with corpus.open(encoding="utf-8-sig", newline="") as source_file:
            row = list(csv.DictReader(source_file))[24]
        outcome = find_match(row)
        self.assertEqual(outcome.poem["Id"], 11578)
        self.assertEqual(outcome.poem["AuthorDate"], "652年")
        self.assertEqual(outcome.status, "matched")

    def test_manual_sidecar_preserves_documented_disputed_ranges(self) -> None:
        manual_path = Path(__file__).parents[1] / "data/poem_dates_manual.csv"
        overrides = load_manual_overrides(manual_path)
        cases = [
            (
                "P025",
                ("652", "653", "652年冬—653年春", "range"),
            ),
            (
                "P003",
                ("755", "759", "755年；另有乾元秦州说（约759年）", "disputed"),
            ),
            (
                "P062",
                ("766", "769", "766、767或769年", "disputed"),
            ),
        ]
        for record_id, expected in cases:
            with self.subTest(record_id=record_id):
                row = overrides[record_id]
                actual = (
                    row["date_start"],
                    row["date_end"],
                    row["date_label"],
                    row["dating_status"],
                )
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
