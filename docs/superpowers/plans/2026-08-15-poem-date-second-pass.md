# 唐代侠义诗第二轮系年 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将开放接口查询状态与作品系年结论分离，合并可持续维护的人工考证侧车，并完成首批 11 位高频诗人 25 首作品的第二轮系年核查。

**Architecture:** 保留当前单脚本生成流程，但把自动查询结果封装为明确的 `LookupOutcome`，再以 `record_id` 将 `data/poem_dates_manual.csv` 合并到自动结果中。最终 `data/poem_dates.csv` 同时保存自动查询日志、作品年代、证据来源和人工复核状态；项目验证器负责检查状态枚举和日期不变量。

**Tech Stack:** Python 3.10+ 标准库、`certifi`、CSV、`unittest`、现有 npm 验证与静态页面烟雾测试。

## Global Constraints

- 不把作者生卒年或朝代中点当作作品写作年份。
- 无充分证据的作品保持 `dating_status=undated`，且 `date_start`、`date_end` 为空。
- 自动接口日志不得被人工考证覆盖；人工结果不得在重新请求接口时丢失。
- 普通网页和搜索摘要只能作为线索，不能单独支撑最终年代。
- 来源冲突必须保留异说，并标记 `dating_status=disputed`。
- 重复诗继承主记录年代时不得计作新增独立系年成果。
- 保持 100 条记录、重复关系和语料边界标记不变。
- 不修改未跟踪的 `高频诗人画像/` 和既有维护性计划文件。

---

## File Structure

- `scripts/build_poem_dates.py`：自动查询、状态分类、人工侧车加载、合并和最终 CSV 输出。
- `scripts/test_build_poem_dates.py`：状态分类、日期不变量、人工合并和现有 API 匹配回归测试。
- `data/poem_dates_manual.csv`：只保存人工判断和人工来源，以 `record_id` 为主键。
- `data/poem_dates.csv`：生成后的统一审计表，供分析和后续可视化使用。
- `scripts/validate_project.py`：验证日期表的字段、枚举、主键、日期不变量和记录数。
- `README.md`：说明两层状态、再生成命令、证据等级和覆盖率口径。

### Task 1: 分离自动查询状态与系年状态

**Files:**
- Modify: `scripts/test_build_poem_dates.py`
- Modify: `scripts/build_poem_dates.py`

**Interfaces:**
- Produces: `LookupOutcome(poem, payload, score, query, status, note)`。
- Produces: `classify_dating_status(date_start, date_end, date_precision) -> str`。
- `find_match(row) -> LookupOutcome`，其中 `status` 只能是 `matched`、`no_result`、`endpoint_error`、`ambiguous_match`。

- [ ] **Step 1: 写入查询状态的失败测试**

在 `scripts/test_build_poem_dates.py` 增加：

```python
from build_poem_dates import classify_lookup_status


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
```

- [ ] **Step 2: 运行测试并确认因函数缺失而失败**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: FAIL with `ImportError: cannot import name 'classify_lookup_status'`。

- [ ] **Step 3: 实现最小查询状态分类和结果对象**

在 `scripts/build_poem_dates.py` 增加：

```python
from dataclasses import dataclass


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
    if successful_queries == 0 and last_error:
        return "endpoint_error", last_error
    if candidate_count == 0:
        return "no_result", "开放接口正常响应，但未返回候选作品。"
    if best_score < MIN_MATCH_SCORE:
        return "ambiguous_match", f"候选作品最高匹配分数为 {best_score:.3f}。"
    return "matched", ""
```

修改 `find_match` 统计候选数量并返回 `LookupOutcome`；修改 `build_rows` 写入 `lookup_status` 和 `lookup_note`，不再把接口错误追加到 `audit_note`。

- [ ] **Step 4: 写入并运行系年状态失败测试**

```python
from build_poem_dates import classify_dating_status


class DatingStatusTest(unittest.TestCase):
    def test_date_shapes_map_to_distinct_statuses(self) -> None:
        self.assertEqual(classify_dating_status("731", "731", "单年系年"), "exact")
        self.assertEqual(classify_dating_status("652", "653", "跨年范围"), "range")
        self.assertEqual(classify_dating_status("755", "759", "争议范围"), "disputed")
        self.assertEqual(classify_dating_status("", "", "未知"), "undated")
```

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: FAIL with missing `classify_dating_status`。

- [ ] **Step 5: 实现系年状态并运行全部脚本测试**

```python
def classify_dating_status(start: str, end: str, precision: str) -> str:
    if not start and not end:
        return "undated"
    if "争议" in precision:
        return "disputed"
    if start == end and precision == "单年系年":
        return "exact"
    return "range"
```

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: all tests PASS。

- [ ] **Step 6: 提交查询与系年状态模型**

```bash
git add scripts/build_poem_dates.py scripts/test_build_poem_dates.py
git commit -m "feat: separate poem lookup and dating status"
```

### Task 2: 增加人工考证侧车与确定性合并

**Files:**
- Create: `data/poem_dates_manual.csv`
- Modify: `scripts/test_build_poem_dates.py`
- Modify: `scripts/build_poem_dates.py`

**Interfaces:**
- Produces: `load_manual_overrides(path: Path) -> dict[str, dict[str, str]]`。
- Produces: `merge_manual_override(auto_row, manual_row) -> dict[str, str]`。
- CLI consumes: `--manual-input data/poem_dates_manual.csv`。

- [ ] **Step 1: 写入人工合并的失败测试**

```python
from build_poem_dates import merge_manual_override


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
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: FAIL with missing `merge_manual_override`。

- [ ] **Step 3: 实现侧车加载、字段白名单与合并**

人工字段白名单固定为：

```python
MANUAL_FIELDS = (
    "date_start", "date_end", "date_label", "date_precision", "confidence",
    "dating_status", "dating_method", "source_type", "manual_source_1",
    "manual_source_2", "evidence_quote_or_summary", "review_status",
    "research_note",
)
```

`merge_manual_override` 只复制白名单内的非空人工值；如果人工行的 `dating_status` 不是 `undated`，兼容字段设为 `人工复核且有系年`。重复 `record_id` 时 `load_manual_overrides` 必须抛出 `ValueError`。

- [ ] **Step 4: 建立侧车表头并迁移现有三条人工修订**

`data/poem_dates_manual.csv` 使用 UTF-8 BOM，表头为 `record_id` 加 `MANUAL_FIELDS`。将现有 `DOCUMENTED_DATE_OVERRIDES` 对应的 P025《长安古意》、P003《后出塞五首·四》、P062《赠苏四徯》迁入侧车；来源和证据沿用现有 API 证据，`review_status=manual_single_source`，不在脚本常量中继续保存作品特例。

- [ ] **Step 5: 接入 CLI 并验证重新生成不丢失人工结果**

CLI 增加：

```python
parser.add_argument(
    "--manual-input",
    type=Path,
    default=Path("data/poem_dates_manual.csv"),
)
```

在 `build_rows` 完成自动结果后按 `record_id` 合并人工行，再写最终 CSV。

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: all tests PASS。

- [ ] **Step 6: 提交人工侧车功能**

```bash
git add data/poem_dates_manual.csv scripts/build_poem_dates.py scripts/test_build_poem_dates.py
git commit -m "feat: merge manual poem dating evidence"
```

### Task 3: 验证状态枚举与日期不变量

**Files:**
- Modify: `scripts/validate_project.py`
- Modify: `scripts/test_build_poem_dates.py`

**Interfaces:**
- Produces: `validate_date_record(row: dict[str, str]) -> list[str]`。
- Validator requires 100 unique `record_id` values and all new output columns。

- [ ] **Step 1: 写入日期不变量失败测试**

```python
from build_poem_dates import validate_date_record


class DateInvariantTest(unittest.TestCase):
    def test_undated_row_rejects_hidden_years(self) -> None:
        errors = validate_date_record({
            "record_id": "P004",
            "date_start": "684",
            "date_end": "684",
            "dating_status": "undated",
        })
        self.assertTrue(any("undated" in error for error in errors))

    def test_exact_row_requires_equal_years(self) -> None:
        errors = validate_date_record({
            "record_id": "P004",
            "date_start": "684",
            "date_end": "685",
            "dating_status": "exact",
        })
        self.assertTrue(any("exact" in error for error in errors))
```

- [ ] **Step 2: 运行测试并确认失败，再实现验证函数**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: FAIL with missing `validate_date_record`。

实现规则：`undated` 不得有年份；`exact` 必须有相同整数年份；`range`、`disputed`、`activity_phase` 必须有整数起止值且 `start <= end`；所有状态必须来自允许枚举。

- [ ] **Step 3: 扩展项目验证器**

在 `scripts/validate_project.py` 检查：

- `poem_dates.csv` 为 100 行且 `record_id` 唯一。
- 必需字段包含 `lookup_status`、`lookup_note`、`dating_status`、`dating_method`、`source_type`、`manual_source_1`、`manual_source_2`、`evidence_quote_or_summary`、`review_status`、`research_note`。
- `lookup_status` 和 `dating_status` 均在允许枚举中。
- 每行通过 `validate_date_record`。
- `duplicate_of` 指向现有且更早的主记录。

- [ ] **Step 4: 运行单元测试和项目验证**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: all tests PASS。

Run: `python3 scripts/validate_project.py`

Expected: `Validation passed`，100 条日期记录满足不变量。

- [ ] **Step 5: 提交验证规则**

```bash
git add scripts/build_poem_dates.py scripts/test_build_poem_dates.py scripts/validate_project.py
git commit -m "test: validate poem dating invariants"
```

### Task 4: 完成首批 25 首人工系年核查

**Files:**
- Modify: `data/poem_dates_manual.csv`

**Interfaces:**
- Consumes: `record_id` 与 Task 2 的人工字段。
- Produces: 每个优先记录一行人工审核结果；有可靠年代则填写日期，无可靠年代则填写 `dating_status=undated`、`review_status=needs_review` 和已检索范围。

- [ ] **Step 1: 建立精确的 25 首核查清单**

按以下记录逐条加入侧车，不得遗漏或用重复项替代：

```text
P004 P007 P009 P010 P012 P013 P014 P015 P016 P017
P026 P027 P028 P029 P035 P036 P041 P048 P049 P050
P056 P058 P070 P084 P085
```

- [ ] **Step 2: 核查李白、王维、高适 9 首**

检索组合固定为“作者 + 规范题名 + 编年笺注／年谱／系年”，并检查题名异体。优先使用《李白全集编年笺注》、王维年谱或编年笺注、高适年谱及其学术整理本。每条记录填写来源书目信息、证据摘要、方法和复核状态；只有阶段证据时使用 `activity_phase`。

- [ ] **Step 3: 核查王昌龄、李颀、李益 6 首**

对边塞诗优先检查可对应的任职、出塞、军镇和交游事件。若不同年谱对李益军旅阶段有冲突，使用 `disputed` 并在 `research_note` 并列主要异说。

- [ ] **Step 4: 核查卢照邻、杨炯、骆宾王 6 首**

先确认乐府旧题是否为独立作品题名，再检查初唐诗人年谱和编年集。题名只能指向传统母题、无法约束具体创作时间时保持 `undated`。

- [ ] **Step 5: 核查李峤、马戴 4 首**

检查咏物诗题名歧义、卷次和异题；材料只能支持诗人活动阶段时可写 `activity_phase`，但不得仅凭作者生卒年生成范围。

- [ ] **Step 6: 对每个非空年代执行来源复核**

至少验证来源实体真实存在、作者与版本信息一致、来源确实支持该作品或历史锚点。一个可靠来源为 `manual_single_source`；两个独立可靠来源一致才是 `manual_cross_checked`。普通网页线索必须继续追溯至出版物、论文或一手史料。

- [ ] **Step 7: 运行侧车与日期不变量验证并提交**

Run: `python3 scripts/validate_project.py`

Expected: all 25 priority records appear exactly once in the manual sidecar; all non-empty dates pass invariants。

```bash
git add data/poem_dates_manual.csv
git commit -m "data: add first-pass manual poem dating evidence"
```

### Task 5: 重新生成审计表并更新说明

**Files:**
- Modify: `data/poem_dates.csv`
- Modify: `README.md`

**Interfaces:**
- Consumes: automatic API lookup + `data/poem_dates_manual.csv`。
- Produces: unified 100-row `data/poem_dates.csv` and documented coverage counts。

- [ ] **Step 1: 运行生成脚本**

Run: `python3 scripts/build_poem_dates.py`

Expected: 写出 100 行；接口错误只出现在 `lookup_status`/`lookup_note`，不再出现在 `audit_note`。

- [ ] **Step 2: 计算三层覆盖率**

运行一个只读 Python 汇总，报告：

- 100 条记录中的 `dating_status` 分布。
- 去除 `duplicate_of`、`corpus_scope!=唐` 后的独立作品分布。
- `exact`、`range`、`disputed`、`activity_phase` 分开计数。
- 首批 25 首中得到年代、仍未知和存在争议的数量。

- [ ] **Step 3: 更新 README**

说明 `lookup_status` 与 `dating_status` 的区别、人工侧车不会被自动生成覆盖、第二轮证据层级、重新生成命令和最新覆盖率。明确覆盖率是当前核查进度，不代表未系年作品不存在可考年代。

- [ ] **Step 4: 提交统一数据与文档**

```bash
git add data/poem_dates.csv README.md
git commit -m "docs: report second-pass poem dating coverage"
```

### Task 6: 完整回归验证与交付审计

**Files:**
- Verify only: all files changed in Tasks 1-5

**Interfaces:**
- Produces: verification evidence and a clean scoped diff。

- [ ] **Step 1: 运行日期单元测试**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: all tests PASS，无跳过和意外网络错误。

- [ ] **Step 2: 运行项目验证与页面烟雾测试**

Run: `python3 scripts/validate_project.py`

Expected: validation PASS。

Run: `npm test`

Expected: 100-row validation PASS；9 个页面和 5 个资源全部可访问。

- [ ] **Step 3: 检查格式和工作区边界**

Run: `git diff --check HEAD~5..HEAD`

Expected: no whitespace errors。

Run: `git status --short`

Expected: 只剩明确未纳入本任务的 `高频诗人画像/` 和既有未跟踪文件；不得误提交它们。

- [ ] **Step 4: 审计输出语义**

确认任何 `endpoint_error` 记录都没有被解释为“无可靠系年”；任何 `dating_status=undated` 记录都没有隐藏年份；所有人工非空年代都有来源与证据摘要；重复作品未被计作新增独立成果。

- [ ] **Step 5: 汇报结果**

向用户报告修改文件、记录级与独立作品级覆盖率、新增确切／区间／争议／阶段结果、仍未知数量、首批人工核查的来源局限，以及后续是否继续核查剩余单例诗人。
