#!/usr/bin/env python3
"""Build a conservative composition-date audit for the project corpus.

The script queries the non-commercial open API of the Chinese Classical
Literature Knowledge Graph / Tang-Song Literature Chronological Map.  It does
not turn every returned year into an unquestioned fact: matching status,
precision, confidence, duplicate relationships, and corpus-scope warnings are
kept as separate fields for later manual review.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import ssl
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

import certifi


API_ROOT = "https://open.cnkgraph.com"
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
DATASET_NAME = "唐宋文学编年地图（古籍文献知识图谱网）"
DATASET_URL = "https://open.cnkgraph.com/Home/OpenResources"
DATE_SOURCE_URL = "https://open.cnkgraph.com/Writing/{poem_id}"

LEADING_TITLE_LABELS = (
    "横吹曲辞 ",
    "相和歌辞 ",
    "舞曲歌辞 ",
    "杂曲歌辞 ",
    "乐府古题序 ",
)

TRAILING_PART_RE = re.compile(
    r"\s+(?:其)?(?:一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十|二十一|二十二|二十三)$"
)

CONFLICT_MARKERS = (
    "或",
    "约",
    "疑",
    "一说",
    "另有",
    "认为",
    "之前",
    "之后",
    "前后",
    "待考",
    "未详",
)

MIN_MATCH_SCORE = 0.45

LOOKUP_STATUSES = {"matched", "no_result", "endpoint_error", "ambiguous_match", "not_attempted"}
DATING_STATUSES = {"exact", "range", "disputed", "activity_phase", "undated"}

MANUAL_FIELDS = (
    "date_start",
    "date_end",
    "date_label",
    "date_precision",
    "confidence",
    "dating_status",
    "dating_method",
    "source_type",
    "manual_source_1",
    "manual_source_2",
    "evidence_quote_or_summary",
    "review_status",
    "research_note",
)


@dataclass(frozen=True)
class LookupOutcome:
    poem: dict[str, Any] | None
    payload: dict[str, Any] | None
    score: float
    query: str
    status: str
    note: str = ""


def classify_lookup_status(
    successful_queries: int,
    candidate_count: int,
    best_score: float,
    last_error: str,
) -> tuple[str, str]:
    """Separate transport/search outcomes from the poem's dating status."""
    if successful_queries == 0 and last_error:
        return "endpoint_error", last_error
    if candidate_count == 0:
        return "no_result", "开放接口正常响应，但未返回候选作品。"
    if best_score < MIN_MATCH_SCORE:
        return "ambiguous_match", f"候选作品最高匹配分数为 {best_score:.3f}。"
    return "matched", ""


def classify_dating_status(start: str, end: str, precision: str) -> str:
    """Map date shape and precision onto a visualization-safe status."""
    if not start and not end:
        return "undated"
    if "争议" in precision:
        return "disputed"
    if start == end and precision == "单年系年":
        return "exact"
    return "range"


def validate_date_record(row: dict[str, str]) -> list[str]:
    """Return semantic date errors without mutating a generated record."""
    record_id = row.get("record_id", "<unknown>")
    status = row.get("dating_status", "")
    start = row.get("date_start", "").strip()
    end = row.get("date_end", "").strip()
    errors: list[str] = []

    if status not in DATING_STATUSES:
        return [f"{record_id}: unsupported dating_status {status!r}"]
    if status == "undated":
        if start or end:
            errors.append(f"{record_id}: undated records must not contain years")
        return errors
    if not start or not end:
        return [f"{record_id}: {status} records require date_start and date_end"]
    try:
        start_year = int(start)
        end_year = int(end)
    except ValueError:
        return [f"{record_id}: {status} dates must be integer years"]
    if start_year > end_year:
        errors.append(f"{record_id}: date_start must not exceed date_end")
    if status == "exact" and start_year != end_year:
        errors.append(f"{record_id}: exact dates require identical start and end years")
    return errors


def merge_manual_override(
    auto_row: dict[str, str], manual_row: dict[str, str]
) -> dict[str, str]:
    """Merge reviewed dating evidence without rewriting automatic lookup logs."""
    merged = dict(auto_row)
    for field in MANUAL_FIELDS:
        value = manual_row.get(field, "").strip()
        if value:
            merged[field] = value
    if manual_row.get("dating_status", "").strip() not in {"", "undated"}:
        merged["verification_status"] = "人工复核且有系年"
    return merged


def load_manual_overrides(path: Path) -> dict[str, dict[str, str]]:
    """Load reviewed records by stable corpus id and reject ambiguous duplicates."""
    if not path.exists():
        return {}
    overrides: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8-sig", newline="") as manual_file:
        for row in csv.DictReader(manual_file):
            record_id = (row.get("record_id") or "").strip()
            if not record_id:
                continue
            if record_id in overrides:
                raise ValueError(f"人工系年侧车存在重复 record_id：{record_id}")
            overrides[record_id] = row
    return overrides

# The API's poem endpoint returns traditional characters even when its search
# endpoint is requested in simplified Chinese.  These author-name characters
# cover the corpus and prevent a script difference from becoming a false
# author mismatch.  Text similarity remains the second, independent check.
TRADITIONAL_AUTHOR_TRANSLATION = str.maketrans(
    {
        "維": "维",
        "張": "张",
        "盧": "卢",
        "鄰": "邻",
        "頎": "颀",
        "萬": "万",
        "楊": "杨",
        "嶠": "峤",
        "韋": "韦",
        "駱": "骆",
        "賓": "宾",
        "說": "说",
        "賀": "贺",
        "錢": "钱",
        "韓": "韩",
        "顧": "顾",
        "況": "况",
        "倫": "伦",
        "權": "权",
        "輿": "舆",
        "劉": "刘",
        "錫": "锡",
        "許": "许",
        "渾": "浑",
        "隱": "隐",
        "馬": "马",
        "溫": "温",
        "總": "总",
        "圖": "图",
        "吳": "吴",
        "鄭": "郑",
        "馮": "冯",
        "徵": "征",
        "質": "质",
        "塗": "涂",
    }
)

def han_text(value: str) -> str:
    """Return only CJK characters, normalized for approximate comparison."""
    value = unicodedata.normalize("NFKC", value or "")
    value = value.translate(TRADITIONAL_AUTHOR_TRANSLATION)
    value = value.replace("後", "后").replace("迴", "回").replace("蹔", "暂")
    value = value.replace("餘", "馀").replace("讐", "仇").replace("鬬", "斗")
    return "".join(ch for ch in value if "\u3400" <= ch <= "\u9fff")


def title_queries(author: str, title: str) -> list[str]:
    """Generate precise author-title searches before progressively shortening."""
    titles = [title.strip()]
    stripped = title.strip()
    for label in LEADING_TITLE_LABELS:
        if stripped.startswith(label):
            stripped = stripped[len(label) :].strip()
            titles.append(stripped)
            break
    no_part = TRAILING_PART_RE.sub("", stripped).strip()
    titles.append(no_part)

    seen: set[str] = set()
    queries: list[str] = []
    for candidate in titles:
        if candidate and candidate not in seen:
            seen.add(candidate)
            queries.append(f"{author}《{candidate}》")
    return queries


def request_json(path: str, retries: int = 3) -> dict[str, Any]:
    url = API_ROOT + path
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Accept-Language": "zh-hans",
            "User-Agent": "Tang-Poetry-Studies/1.0 (non-commercial research)",
        },
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=45, context=SSL_CONTEXT) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(0.7 * (attempt + 1))
    raise RuntimeError(f"API request failed: {url}: {last_error}")


def biography_search(query: str) -> dict[str, Any]:
    key = urllib.parse.quote(query, safe="")
    return request_json(f"/api/Biography/Poems/{key}?dynasty=%E5%94%90")


def marker_details(payload: dict[str, Any]) -> Iterable[str]:
    for trace in payload.get("Traces") or []:
        for marker in trace.get("Markers") or []:
            detail = marker.get("Detail")
            if detail:
                yield detail


def poem_ids(payload: dict[str, Any]) -> list[int]:
    ids: set[int] = set()
    for detail in marker_details(payload):
        ids.update(int(value) for value in re.findall(r"id=['\"]poem_(\d+)", detail))
    return sorted(ids)


def poem_content(poem: dict[str, Any]) -> str:
    clauses = poem.get("Clauses") or []
    return "".join((clause.get("Content") or "") for clause in clauses)


def poem_title(poem: dict[str, Any]) -> str:
    title = poem.get("Title") or {}
    parts = [title.get("Content") or ""]
    subtitle = poem.get("SubTitle")
    if isinstance(subtitle, dict):
        parts.append(subtitle.get("Content") or "")
    elif subtitle:
        parts.append(str(subtitle))
    return " ".join(part for part in parts if part).strip()


def match_score(row: dict[str, str], poem: dict[str, Any]) -> float:
    if han_text(row["作者"]) != han_text(poem.get("Author") or ""):
        return 0.0
    source_text = han_text(row["诗歌原文"])
    candidate_text = han_text(poem_content(poem))
    if not source_text or not candidate_text:
        return 0.0
    text_score = SequenceMatcher(None, source_text, candidate_text).ratio()
    source_title = han_text(TRAILING_PART_RE.sub("", row["诗歌名"]))
    candidate_title = han_text(poem_title(poem))
    title_score = SequenceMatcher(None, source_title, candidate_title).ratio()
    return 0.88 * text_score + 0.12 * title_score


def strip_html(fragment: str) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def evidence_for(payload: dict[str, Any], target_id: int) -> tuple[str, str]:
    target = f"id='poem_{target_id}'"
    for detail in marker_details(payload):
        if target not in detail and f'id="poem_{target_id}"' not in detail:
            continue
        position = detail.find(target)
        if position < 0:
            position = detail.find(f'id="poem_{target_id}"')
        prior = detail[:position]
        event_start = max(prior.rfind("class='label1'"), prior.rfind('class="label1"'))
        event_fragment = prior[event_start:] if event_start >= 0 else prior
        plain = strip_html(event_fragment)
        sources = re.findall(r"出处[：:]\s*([^<]+)", event_fragment)
        source_basis = "；".join(strip_html(value) for value in sources[-2:])
        if not source_basis:
            source_basis = DATASET_NAME
        return plain[-700:], source_basis
    return "", DATASET_NAME


def date_fields(poem: dict[str, Any], evidence: str) -> tuple[str, str, str, str, str]:
    years = sorted({int(year) for year in (poem.get("AuthorYears") or [])})
    label = str(poem.get("AuthorDate") or "").strip()
    if not years:
        return "", "", label, "未知", "低"
    start, end = years[0], years[-1]
    if len(years) > 1 or start != end:
        precision = "年份范围"
    elif any(marker in label for marker in ("前", "后", "约", "至", "间")):
        precision = "约年/范围"
    else:
        precision = "单年系年"
    confidence = "低" if any(marker in evidence for marker in CONFLICT_MARKERS) else "中"
    return str(start), str(end), label or str(start), precision, confidence


def duplicate_map(rows: list[dict[str, str]], threshold: float = 0.90) -> dict[int, int]:
    duplicates: dict[int, int] = {}
    for index, row in enumerate(rows):
        for prior_index in range(index):
            prior = rows[prior_index]
            if han_text(row["作者"]) != han_text(prior["作者"]):
                continue
            score = SequenceMatcher(
                None, han_text(row["诗歌原文"]), han_text(prior["诗歌原文"])
            ).ratio()
            if score >= threshold:
                duplicates[index + 1] = prior_index + 1
                break
    return duplicates


def corpus_warning(row_number: int, row: dict[str, str]) -> tuple[str, str]:
    if row["作者"] == "范质":
        return "非唐", "作者为五代后周至北宋人物；不应直接计入唐诗时间轴。"
    if row_number == 100 and row["作者"] == "李峤" and row["诗歌名"] == "筝":
        return "待剔除", "诗歌正文不含“侠”；疑因附带校勘说明中的《弹》条目误命中。"
    if row["作者"] in {"寒山", "李行言"}:
        return "待核", "作者或作品年代边界较宽，单首作品通常难以精确系年。"
    return "唐", ""


def find_match(row: dict[str, str]) -> LookupOutcome:
    best_poem: dict[str, Any] | None = None
    best_payload: dict[str, Any] | None = None
    best_score = 0.0
    used_query = ""
    fetched: dict[int, dict[str, Any]] = {}
    candidate_ids: set[int] = set()
    successful_queries = 0
    last_query_error: RuntimeError | None = None

    for query in title_queries(row["作者"], row["诗歌名"]):
        try:
            payload = biography_search(query)
            successful_queries += 1
        except RuntimeError as exc:
            last_query_error = exc
            continue
        ids = poem_ids(payload)
        candidate_ids.update(ids)
        for poem_id in ids:
            poem = fetched.get(poem_id)
            if poem is None:
                poem = request_json(f"/api/Poem/{poem_id}?includeLinks=false")
                fetched[poem_id] = poem
            score = match_score(row, poem)
            if score > best_score:
                best_poem = poem
                best_payload = payload
                best_score = score
                used_query = query
        if best_score >= 0.86:
            break
    status, note = classify_lookup_status(
        successful_queries=successful_queries,
        candidate_count=len(candidate_ids),
        best_score=best_score,
        last_error=str(last_query_error or ""),
    )
    return LookupOutcome(
        poem=best_poem,
        payload=best_payload,
        score=best_score,
        query=used_query,
        status=status,
        note=note,
    )


def build_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    duplicates = duplicate_map(source_rows)
    results: list[dict[str, str]] = []

    for row_number, row in enumerate(source_rows, start=1):
        scope, warning = corpus_warning(row_number, row)
        print(f"[{row_number:03d}/{len(source_rows)}] {row['作者']}《{row['诗歌名']}》", flush=True)
        try:
            outcome = find_match(row)
        except Exception as exc:  # keep the audit usable if one lookup fails
            outcome = LookupOutcome(None, None, 0.0, "", "endpoint_error", str(exc))

        result = {
            "record_id": f"P{row_number:03d}",
            "author": row["作者"],
            "title_original": row["诗歌名"],
            "title_normalized": TRAILING_PART_RE.sub("", row["诗歌名"]).strip(),
            "cluster": row["聚类类别"],
            "duplicate_of": f"P{duplicates[row_number]:03d}" if row_number in duplicates else "",
            "corpus_scope": scope,
            "date_start": "",
            "date_end": "",
            "date_label": "",
            "date_precision": "未知",
            "dating_status": "undated",
            "dating_method": "unknown",
            "source_type": "开放知识图谱",
            "manual_source_1": "",
            "manual_source_2": "",
            "evidence_quote_or_summary": "",
            "review_status": "auto_only",
            "research_note": "",
            "confidence": "低",
            "verification_status": "未匹配",
            "lookup_status": outcome.status,
            "lookup_note": outcome.note,
            "match_score": f"{outcome.score:.3f}" if outcome.score else "",
            "source_dataset": DATASET_NAME,
            "source_basis": "",
            "source_url": DATASET_URL,
            "evidence_note": "",
            "audit_note": warning,
            "search_query": outcome.query,
        }

        if outcome.status == "matched" and outcome.poem is not None and outcome.payload is not None:
            evidence, basis = evidence_for(outcome.payload, int(outcome.poem["Id"]))
            start, end, label, precision, confidence = date_fields(outcome.poem, evidence)
            result.update(
                {
                    "date_start": start,
                    "date_end": end,
                    "date_label": label,
                    "date_precision": precision,
                    "dating_status": classify_dating_status(start, end, precision),
                    "dating_method": "chronological_edition" if start else "unknown",
                    "confidence": confidence,
                    "verification_status": "已匹配且有系年" if start else "已匹配但无系年",
                    "source_basis": basis,
                    "source_url": DATE_SOURCE_URL.format(poem_id=outcome.poem["Id"]),
                    "evidence_note": evidence,
                }
            )
        results.append(result)
        time.sleep(0.08)
    return results


def write_results(path: Path, results: list[dict[str, str]]) -> None:
    """Write a reproducible UTF-8 CSV with repository-standard LF endings."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=list(results[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(results)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/poetry_with_detailed_clusters_sankey.csv"),
    )
    parser.add_argument("--output", type=Path, default=Path("data/poem_dates.csv"))
    parser.add_argument(
        "--manual-input",
        type=Path,
        default=Path("data/poem_dates_manual.csv"),
    )
    args = parser.parse_args()

    with args.input.open(encoding="utf-8-sig", newline="") as source_file:
        source_rows = list(csv.DictReader(source_file))
    results = build_rows(source_rows)
    manual_overrides = load_manual_overrides(args.manual_input)
    results = [
        merge_manual_override(row, manual_overrides.get(row["record_id"], {}))
        for row in results
    ]
    write_results(args.output, results)
    print(f"Wrote {len(results)} rows to {args.output}")


if __name__ == "__main__":
    main()
