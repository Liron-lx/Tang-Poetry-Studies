# 唐代侠义诗作者活动期时间轴数据设计

**状态：** 已获方向确认，待用户审阅本规格后进入实现计划。

## 目标

为后续竖版时间长图提供连续但可追溯的时间位置。作品真实作年、作者活动期推定和生卒年兜底必须在数据中清楚区分；前台可将它们呈现为一条统一的艺术时间叙事，仅以轻微透明度或虚实区别证据强弱。

本阶段只新增和生成数据，不修改 HTML、CSS、JavaScript 或现有图形。

## 范围与口径

- 输出仍覆盖 `data/poem_dates.csv` 的全部 100 条记录。
- 作者活动期资料优先覆盖 86 首独立、`corpus_scope=唐` 的作品所涉及的 53 位作者。
- 非唐、待核、待剔除记录不生成推定时间位置。
- 重复记录继承其主记录的时间轴位置和证据状态，不生成新的作者星团成员。
- `date_start`、`date_end`、`dating_status` 继续只表示作品级系年，绝不写入推定年份。

## 数据架构

### 作者活动期资料：`data/author_activity_periods.csv`

一位作者一行；人工维护并可独立复核。字段为：

| 字段 | 含义 |
| --- | --- |
| `author` | 与诗歌语料一致的作者名，唯一键 |
| `birth_year` / `death_year` | 可确定时记录的生卒年；允许为空 |
| `activity_start` / `activity_end` | 主要创作活动期；允许为空，但必须同时存在或同时为空 |
| `activity_method` | `poet_chronology`、`biography_event_inference`、`lifespan_only` 或 `unknown` |
| `source_type` | 年谱、编年笺注、传记／任官游历资料等 |
| `source_1` / `source_2` | 可追溯的书目或稳定链接 |
| `evidence_summary` | 活动期取值依据的简短说明 |
| `confidence` | 高／中／低 |
| `review_status` | `manual_cross_checked`、`manual_single_source`、`needs_review` 或 `not_attempted` |
| `research_note` | 缺口、异说和后续核对方向 |

活动期资料的来源优先级：

1. 诗人年谱、作品编年笺注明确给出的创作或行迹跨度；
2. 任官、游历、入幕、交游等连续生平事件所支持的推定区间；
3. 无法得到活动期资料时，保留生卒年作为 `lifespan_only` 兜底；
4. 连生卒年也无法稳妥确定时，保留空值，不制造位置。

### 作品展示坐标：`data/poem_dates.csv`

生成器在现有审计字段之后增加以下只供时间轴使用的字段：

| 字段 | 含义 |
| --- | --- |
| `timeline_year` | 最终绘图横／纵轴位置；允许小数年 |
| `timeline_status` | `observed_exact`、`observed_range_center`、`inferred_activity_cluster`、`inferred_lifespan_cluster`、`duplicate_inherited`、`unavailable` |
| `timeline_basis` | 对应的作品日期、活动期、生卒期或主记录 ID |
| `timeline_anchor_start` / `timeline_anchor_end` | 真实日期范围，或推定所依据的活动期／生卒期 |
| `timeline_center_year` | 未展开前的中心年；真实精确年份与其相同 |
| `timeline_offset` | 同一作者星团中的偏移年数；真实作年为 `0` |
| `timeline_confidence` | 时间轴位置的置信度，继承或降级自来源 |
| `timeline_note` | 面向后续 tooltip／图例的简短解释 |

## 位置计算规则

1. `dating_status=exact`：`timeline_year=date_start`，`timeline_status=observed_exact`。
2. `dating_status=range` 或 `disputed`：保留原始范围，`timeline_year=(date_start + date_end) / 2`，`timeline_status=observed_range_center`。
3. 独立唐诗为未定年，且作者具有 `activity_start/activity_end`：中心年为活动期中点，`timeline_status=inferred_activity_cluster`。
4. 无活动期资料但具有生卒年：中心年为生卒年中点，`timeline_status=inferred_lifespan_cluster`。
5. 作者与基础年份均无法确定，或记录不在唐代主体范围：`timeline_status=unavailable`，所有 `timeline_*year` 字段为空。
6. 重复记录复制主记录全部 `timeline_*` 值，`timeline_status=duplicate_inherited`，并在 `timeline_basis` 标明主记录 ID。

## 作者星团展开

同一作者的多首独立未定年诗不全部压在同一中点，而是在中心前后对称展开。

- 先按 `record_id` 固定排序，确保再生成得到相同位置。
- 基础区间为活动期；若使用生卒年兜底，则基础区间为生卒期。
- 半展开宽度为 `clamp((anchor_end - anchor_start) / 6, 6, 15)` 年，即完整星团宽度约为基础区间的三分之一，且介于 12 与 30 年之间。
- 将同一作者的 `n` 首推定诗均匀置于 `[-half_spread, +half_spread]`，单首取 `0`；结果限制在基础区间内。
- `timeline_year = timeline_center_year + timeline_offset`。这只是艺术排版坐标，不回写作品创作日期。

## 生成与验证

- 新增作者活动期资料读取、主键与年份范围校验。
- 作品日期生成后再计算时间轴字段，使重新查询开放接口不会丢失人工活动期资料。
- 为活动期资料和输出字段建立单元测试：唯一作者、完整区间、合法方法和状态、真实日期不被覆盖、范围中点正确、星团偏移对称且确定、重复记录继承、非唐边界不生成估算。
- 更新项目验证器：要求新增输出列、100 条唯一记录、所有时间轴状态合法，并检查状态与字段组合的一致性。
- 更新 README：区分“作品系年审计”与“艺术时间轴位置”，明确推定位置不等于作品确切作年。

## 交付边界

本阶段的交付为可再生成的数据文件、来源记录、生成脚本、测试和文档。竖版长图的版式、颜色、节点样式、导出和交互在整体视觉方案确认后另行设计。
