#!/usr/bin/env python3

import csv
import unittest
from pathlib import Path

from build_poem_dates import (
    classify_dating_status,
    classify_lookup_status,
    date_fields,
    find_match,
    request_json,
)


class DatingStatusTest(unittest.TestCase):
    def test_date_shapes_map_to_distinct_statuses(self) -> None:
        self.assertEqual(classify_dating_status("731", "731", "单年系年"), "exact")
        self.assertEqual(classify_dating_status("652", "653", "跨年范围"), "range")
        self.assertEqual(classify_dating_status("755", "759", "争议范围"), "disputed")
        self.assertEqual(classify_dating_status("", "", "未知"), "undated")


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

    def test_date_fields_preserves_documented_disputed_ranges(self) -> None:
        cases = [
            (
                {"Id": 11578, "AuthorYears": [652], "AuthorDate": "652年"},
                ("652", "653", "652年冬—653年春", "跨年范围", "低"),
            ),
            (
                {"Id": 31503, "AuthorYears": [755], "AuthorDate": "755年"},
                ("755", "759", "755年；另有乾元秦州说（约759年）", "争议范围", "低"),
            ),
            (
                {"Id": 31848, "AuthorYears": [767], "AuthorDate": "767年"},
                ("766", "769", "766、767或769年", "争议范围", "低"),
            ),
        ]
        for poem, expected in cases:
            with self.subTest(poem_id=poem["Id"]):
                self.assertEqual(date_fields(poem, "存在异说"), expected)


if __name__ == "__main__":
    unittest.main()
