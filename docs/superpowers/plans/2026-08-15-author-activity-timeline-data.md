# 作者活动期时间轴数据 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为全部唐代主体语料生成可追溯的时间轴展示坐标，使未定年诗可围绕作者活动期或生卒年中点形成确定性的宽星团，同时不篡改作品级系年。

**Architecture:** 新增一个人工维护的 `author_activity_periods.csv` 作为作者层来源。生成器在自动查询和人工作品系年合并之后读取该表，向统一的 `poem_dates.csv` 派生时间轴字段；作品真实日期与艺术时间轴位置保持两套独立字段。验证器和单元测试分别保护来源表、时间轴状态和星团算法。

**Tech Stack:** Python 3.13 标准库、CSV、`unittest`、现有 `certifi` 查询脚本、npm 静态资源烟雾测试。

## Global Constraints

- 不修改 `date_start`、`date_end`、`date_label`、`date_precision` 或 `dating_status` 来存放推定值。
- 保持 100 条记录、既有 `duplicate_of`、`corpus_scope` 和人工作品系年侧车不变。
- 只为 `corpus_scope=唐` 的独立主记录推定位置；重复记录继承主记录，非唐／待核／待剔除记录为 `unavailable`。
- 作者活动期的来源优先级为：年谱或编年笺注 > 连续生平事件推定 > 生卒年兜底 > 无位置。
- 所有推定活动期与生卒期都要记录来源、证据摘要、置信度和复核状态。
- 同一作者的推定诗按 `record_id` 稳定排序，并以中心年为轴对称展开；完整星团宽度介于 12 与 30 年。
- 本阶段不修改 HTML、CSS、JavaScript 或页面入口。
- 不修改未跟踪的 `高频诗人画像/` 和 `docs/superpowers/plans/2026-08-15-maintainability-data-deployment.md`。

---

## File Structure

- `data/author_activity_periods.csv`：53 位唐代主体作者的人工资料、证据和复核状态。
- `scripts/build_poem_dates.py`：作者资料读取、星团位置派生和 CSV 输出。
- `scripts/test_build_poem_dates.py`：作者资料和时间轴位置算法的单元回归测试。
- `scripts/validate_project.py`：作者资料表和新增作品时间轴字段的项目级不变量验证。
- `data/poem_dates.csv`：重新生成后的 100 条统一审计与时间轴位置数据。
- `README.md`：作品作年与展示坐标的区别、再生成命令和证据口径。

### Task 1: 建立作者活动期资料格式与加载校验

**Files:**

- Create: `data/author_activity_periods.csv`
- Modify: `scripts/build_poem_dates.py`
- Modify: `scripts/test_build_poem_dates.py`

**Interfaces:**

- Produces: `AUTHOR_ACTIVITY_FIELDS: tuple[str, ...]`。
- Produces: `load_author_activity_periods(path: Path) -> dict[str, dict[str, str]]`。
- Produces: `validate_author_activity_record(profile: dict[str, str]) -> list[str]`。
- Input schema: `author,birth_year,death_year,activity_start,activity_end,activity_method,source_type,source_1,source_2,evidence_summary,confidence,review_status,research_note`。

- [ ] **Step 1: 写入作者活动期资料的失败测试**

在 `scripts/test_build_poem_dates.py` 导入 `load_author_activity_periods` 与 `validate_author_activity_record`，增加：

~~~python
class AuthorActivityProfileTest(unittest.TestCase):
    def test_profile_requires_complete_ordered_activity_range(self) -> None:
        errors = validate_author_activity_record(
            {
                "author": "王维",
                "activity_start": "759",
                "activity_end": "717",
                "activity_method": "poet_chronology",
            }
        )
        self.assertTrue(any("activity_start" in error for error in errors))

    def test_loader_rejects_duplicate_authors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "authors.csv"
            path.write_text(
                "author,birth_year,death_year,activity_start,activity_end,activity_method,source_type,source_1,source_2,evidence_summary,confidence,review_status,research_note\n"
                "王维,701,761,717,759,poet_chronology,年谱,source,,,中,needs_review,\n"
                "王维,701,761,717,759,poet_chronology,年谱,source,,,中,needs_review,\n",
                encoding="utf-8-sig",
            )
            with self.assertRaisesRegex(ValueError, "王维"):
                load_author_activity_periods(path)
~~~

- [ ] **Step 2: 运行测试并确认函数尚不存在**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: FAIL with `ImportError: cannot import name 'load_author_activity_periods'`。

- [ ] **Step 3: 实现字段白名单、校验器和 CSV 加载器**

在 `scripts/build_poem_dates.py` 增加：

~~~python
AUTHOR_ACTIVITY_FIELDS = (
    "birth_year", "death_year", "activity_start", "activity_end",
    "activity_method", "source_type", "source_1", "source_2",
    "evidence_summary", "confidence", "review_status", "research_note",
)

def validate_author_activity_record(profile: dict[str, str]) -> list[str]:
    start = profile.get("activity_start", "").strip()
    end = profile.get("activity_end", "").strip()
    if bool(start) != bool(end):
        return [f"{profile.get('author', '')}: activity range must be complete"]
    if start and int(start) > int(end):
        return [f"{profile.get('author', '')}: activity_start must not exceed activity_end"]
    return []

def load_author_activity_periods(path: Path) -> dict[str, dict[str, str]]:
    # Read UTF-8 BOM CSV, reject missing author, duplicate author, and invalid profile.
~~~

同时要求 `activity_method` 只能为 `poet_chronology`、`biography_event_inference`、`lifespan_only`、`unknown`；若活动期为空，方法只能是 `lifespan_only` 或 `unknown`。

- [ ] **Step 4: 建立空表头与可复核示例行**

创建 UTF-8 BOM 的 `data/author_activity_periods.csv`，写入表头与王维一行：

~~~csv
author,birth_year,death_year,activity_start,activity_end,activity_method,source_type,source_1,source_2,evidence_summary,confidence,review_status,research_note
王维,701,761,717,759,poet_chronology,诗人年谱,张清华《王维年谱》,陈铁民《王维年谱》,以科举入仕至安史之乱后仕宦与诗歌活动的可考跨度作为展示活动期,中,needs_review,后续核对年谱原页后再提高置信度
~~~

- [ ] **Step 5: 运行全部脚本测试并提交加载能力**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: PASS。

~~~bash
git add data/author_activity_periods.csv scripts/build_poem_dates.py scripts/test_build_poem_dates.py
git commit -m "feat: add author activity period source data"
~~~

### Task 2: 完成唐代主体作者活动期资料

**Files:**

- Modify: `data/author_activity_periods.csv`
- Modify: `scripts/test_build_poem_dates.py`

**Interfaces:**

- Consumes: `load_author_activity_periods` 和独立唐代主记录的作者集合。
- Produces: 每位主体作者恰好一行资料；活动期资料缺失时仍需填写可用的生卒年或明确 `unknown`。

- [ ] **Step 1: 写入作者覆盖与来源可追溯性的失败测试**

在测试中从 `data/poem_dates.csv` 计算独立唐诗作者集合，并断言：

~~~python
profiles = load_author_activity_periods(
    Path(__file__).parents[1] / "data/author_activity_periods.csv"
)
expected_authors = {
    row["author"] for row in rows
    if not row["duplicate_of"] and row["corpus_scope"] == "唐"
}
self.assertEqual(set(profiles), expected_authors)
for author, profile in profiles.items():
    self.assertTrue(profile["source_1"] or profile["research_note"], author)
~~~

- [ ] **Step 2: 运行测试并确认当前只有王维，覆盖测试失败**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: FAIL，报告缺少其余主体作者。

- [ ] **Step 3: 逐位补齐 53 位作者资料**

按以下作者集合逐一填写一行，并保留来源等级与未决说明：

~~~text
万楚、元稹、冯待征、司空图、吴融、孟浩然、孟郊、崔涂、崔涯、崔颢、张易之、张柬之、张说、戴休珽、戴叔伦、杜甫、李山甫、李白、李益、李商隐、李峤、李贺、李颀、杨凝、杨炯、温庭筠、王昌龄、王维、耿𣲗、蔡孚、薛逢、虞世南、虞羽客、许浑、贺朝、道世、郑鏦、郭震、钱起、陈子良、雍陶、霍总、韦元旦、韩偓、韩翃、顾况、骆宾王、高适、戎昱、刘禹锡、卢照邻、权德舆、马戴
~~~

填写规则：年谱／编年笺注有明确跨度时填 `activity_start/end` 与 `poet_chronology`；连续任官或游历能形成跨度时填 `biography_event_inference`；只有生卒年时活动期留空并填 `lifespan_only`；无法稳定确定时填 `unknown` 并在 `research_note` 说明。不得将作者生卒年复制进活动期字段。

- [ ] **Step 4: 运行覆盖测试与 CSV 校验**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: PASS，且每个独立唐诗作者都有一条资料行。

~~~bash
git add data/author_activity_periods.csv scripts/test_build_poem_dates.py
git commit -m "data: add author activity period profiles"
~~~

### Task 3: 派生作品时间轴位置与宽星团偏移

**Files:**

- Modify: `scripts/build_poem_dates.py`
- Modify: `scripts/test_build_poem_dates.py`
- Modify: `data/poem_dates.csv` (generated)

**Interfaces:**

- Produces: `apply_timeline_positions(rows: list[dict[str, str]], profiles: dict[str, dict[str, str]]) -> list[dict[str, str]]`。
- Produces: 新字段 `timeline_year,timeline_status,timeline_basis,timeline_anchor_start,timeline_anchor_end,timeline_center_year,timeline_offset,timeline_confidence,timeline_note`。
- CLI consumes: `--activity-input data/author_activity_periods.csv`。

- [ ] **Step 1: 写入真实日期、范围中点、活动期星团、生卒年兜底和重复继承的失败测试**

增加以下最小断言：

~~~python
profiles = {
    "甲": {"author": "甲", "activity_start": "700", "activity_end": "760", "confidence": "中"},
    "乙": {"author": "乙", "birth_year": "701", "death_year": "761", "activity_start": "", "activity_end": "", "confidence": "低"},
}
rows = [
    {"record_id": "P001", "author": "甲", "corpus_scope": "唐", "duplicate_of": "", "dating_status": "exact", "date_start": "720", "date_end": "720"},
    {"record_id": "P002", "author": "甲", "corpus_scope": "唐", "duplicate_of": "", "dating_status": "range", "date_start": "652", "date_end": "653"},
    {"record_id": "P003", "author": "甲", "corpus_scope": "唐", "duplicate_of": "", "dating_status": "undated", "date_start": "", "date_end": ""},
    {"record_id": "P004", "author": "乙", "corpus_scope": "唐", "duplicate_of": "", "dating_status": "undated", "date_start": "", "date_end": ""},
    {"record_id": "P005", "author": "甲", "corpus_scope": "唐", "duplicate_of": "P003", "dating_status": "undated", "date_start": "", "date_end": ""},
]
positioned = {row["record_id"]: row for row in apply_timeline_positions(rows, profiles)}
self.assertEqual(positioned["P001"]["timeline_year"], "720")
self.assertEqual(positioned["P002"]["timeline_year"], "652.5")
self.assertEqual(positioned["P003"]["timeline_status"], "inferred_activity_cluster")
self.assertEqual(positioned["P004"]["timeline_year"], "731")
self.assertEqual(positioned["P005"]["timeline_status"], "duplicate_inherited")
self.assertEqual(positioned["P005"]["timeline_year"], positioned["P003"]["timeline_year"])
~~~

另加三首同作者未定年样本，断言偏移为 `-10,0,10`：活动跨度 60 年时，半展开宽度为 `60 / 6 = 10`。

- [ ] **Step 2: 运行测试并确认函数尚不存在**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: FAIL with `ImportError: cannot import name 'apply_timeline_positions'`。

- [ ] **Step 3: 实现位置派生和稳定星团算法**

实现顺序：

1. 为全部行预置新增字段为空和 `timeline_status=unavailable`。
2. 对独立唐诗的 `exact` 写入原年份和 `observed_exact`；对 `range/disputed` 写入以 `.5` 保留的算术中点和 `observed_range_center`。
3. 将其余独立唐诗按 `author` 分组，优先以活动期、否则以生卒期生成中心与锚点。
4. 用 `half_spread = min(15, max(6, (anchor_end - anchor_start) / 6))`，按 `record_id` 等距写入偏移，并将结果限制在锚点闭区间内。
5. 复制 `duplicate_of` 主记录的时间轴字段，覆盖其状态为 `duplicate_inherited`、依据为主记录 ID。
6. 在 CLI 加入：

~~~python
parser.add_argument(
    "--activity-input",
    type=Path,
    default=Path("data/author_activity_periods.csv"),
)
~~~

并在人工作品侧车合并之后调用：

~~~python
profiles = load_author_activity_periods(args.activity_input)
results = apply_timeline_positions(results, profiles)
~~~

- [ ] **Step 4: 运行单元测试并重新生成统一表**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: PASS。

Run: `python3 scripts/build_poem_dates.py --activity-input data/author_activity_periods.csv`

Expected: `Wrote 100 rows to data/poem_dates.csv`。

- [ ] **Step 5: 审计生成结果并提交**

Run:

~~~bash
python3 - <<'PY'
import csv
from collections import Counter
with open("data/poem_dates.csv", encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
print(Counter(row["timeline_status"] for row in rows))
assert len(rows) == 100
assert all(row["date_start"] == "" for row in rows if row["dating_status"] == "undated")
PY
~~~

~~~bash
git add scripts/build_poem_dates.py scripts/test_build_poem_dates.py data/poem_dates.csv
git commit -m "feat: derive artistic poem timeline positions"
~~~

### Task 4: 项目验证器与使用说明

**Files:**

- Modify: `scripts/validate_project.py`
- Modify: `scripts/test_build_poem_dates.py`
- Modify: `README.md`

**Interfaces:**

- `EXPECTED_DATE_COLUMNS` 包含九个 `timeline_*` 字段。
- `validate_timeline_record(row: dict[str, str]) -> list[str]` 验证时间轴状态与字段一致性。

- [ ] **Step 1: 写入项目级时间轴不变量失败测试**

增加：

~~~python
errors = validate_timeline_record(
    {
        "record_id": "P004",
        "timeline_status": "inferred_activity_cluster",
        "timeline_year": "",
        "timeline_anchor_start": "700",
        "timeline_anchor_end": "760",
    }
)
self.assertTrue(any("timeline_year" in error for error in errors))
~~~

并为 `unavailable` 携带年份、`duplicate_inherited` 缺少主记录依据、以及 `observed_exact` 与作品日期不一致分别增加失败断言。

- [ ] **Step 2: 运行测试并确认验证函数尚不存在**

Run: `python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: FAIL with `ImportError: cannot import name 'validate_timeline_record'`。

- [ ] **Step 3: 实现时间轴验证和 README 说明**

`validate_timeline_record` 必须执行：

- `timeline_status` 只能为设计中定义的六种状态；
- `observed_exact` 的 `timeline_year` 与 `date_start` 相同，偏移为 `0`；
- `observed_range_center` 有有效锚点，且年份为两端算术中点；
- 两种 `inferred_*_cluster` 有年份、中心、锚点、非空依据和锚点内的位置；
- `duplicate_inherited` 具有 `P` 开头的主记录依据和非空年份；
- `unavailable` 不得拥有 `timeline_year` 或偏移。

README 新增“艺术时间轴位置”小节，说明该字段为后续排版坐标，绝不等于未定年诗的确切作年；保留重新生成命令：

~~~bash
python3 scripts/build_poem_dates.py \
  --manual-input data/poem_dates_manual.csv \
  --activity-input data/author_activity_periods.csv
~~~

- [ ] **Step 4: 执行完整验证并提交**

Run:

~~~bash
python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v
python3 scripts/validate_project.py
npm test
git diff --check
~~~

Expected: 所有单元测试通过、项目数据校验通过、9 个页面与 5 个资源烟雾测试通过、无空白错误。

~~~bash
git add scripts/validate_project.py scripts/test_build_poem_dates.py README.md
git commit -m "docs: document artistic timeline data provenance"
~~~
