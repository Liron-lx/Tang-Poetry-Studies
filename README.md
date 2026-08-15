# 唐代侠义诗可视化

这是一个以唐代咏侠诗为对象的静态数字人文可视化项目，包含地理分布、词频、情感强度和作者—聚类关系等页面。

## 本地运行

项目使用浏览器端 HTML、D3、ECharts 和 p5.js，不需要构建步骤。由于页面需要通过 `fetch`、`d3.csv` 和 JSON 请求加载资源，请通过静态服务器访问：

```bash
npm run dev
```

或直接使用 Python：

```bash
python3 -m http.server 8000
```

然后打开 <http://127.0.0.1:8000/index.html>。

## 页面入口

- `index.html`：项目首页
- `interactive.html`：唐代咏侠诗地理分布（p5.js）
- `poetry-emotion.html`：词频类别可视化
- `word-association.html`：诗词情感强度可视化
- `keyword-river.html`：作者与聚类类别关系图
- `circular_sankey.html`：关系弦图备用页面
- `geography.html`：ECharts 地理分布备用页面

## 数据

权威数据位于 `data/`：

- `poetry_with_detailed_clusters_sankey.csv`：100 条诗歌记录及聚类类别
- `poem_dates.csv`：自动查询日志与人工考证合并后的逐条创作年代审计
- `poem_dates_manual.csv`：以 `record_id` 为主键的人工系年证据、来源和复核状态
- `author_activity_periods.csv`：53 位唐代主体作者的活动期、生卒期和来源复核记录
- `地方名称及经纬度.csv`：地点、频次、坐标和类型
- `tang_dynasty_detailed_boundary.json`：唐代边界、城市和路线数据

当前项目以 CSV 中的 100 条诗歌记录作为样本量口径。运行数据校验：

```bash
npm run validate
```

页面依赖的 D3、ECharts、p5.js 和 Google Fonts 当前通过 CDN 加载；如果需要离线部署，下一阶段可以再将这些依赖本地化。

## 创作年代数据

`data/poem_dates.csv` 是两轮作品系年审计的统一结果，不是把作者生卒年当作作品写作年。当前 100 条记录中有 33 条得到作品级系年；扣除重复收录和语料边界异常后，86 首可纳入唐代主体分析的独立作品中有 30 首得到系年。第二轮优先复核了 25 首作品，其中 5 首得到低置信度候选年份，20 首在记录检索来源和未决原因后仍保持未定年，避免用推测年份填充时间轴。

自动查询的主要数据源为[唐宋文学编年地图开放资源](https://open.cnkgraph.com/Home/OpenResources)，人工侧车则记录诗人年谱、编年笺注、作品目录和事件锚点。表中同时保留：

- `lookup_status`、`lookup_note`：区分匹配成功、无结果、接口错误和候选歧义；接口失败不再等同于作品无法系年
- `dating_status`、`date_start`、`date_end` 与 `date_precision`：区分单年、范围、争议和未定年
- `dating_method`、`source_type`、`manual_source_1/2`：记录编年版本、诗人年谱、事件锚点等依据
- `confidence`、`review_status`、`evidence_quote_or_summary`、`research_note`：记录证据等级、复核进度、不确定性和下一步线索
- `duplicate_of`、`corpus_scope`：标记重复作品、非唐作品和疑似误入条目

### 面向艺术时间轴的展示坐标

作品级系年与展示坐标严格分开：`date_start/end` 只保存作品本身的可考系年，绝不写入作者生卒年或视觉推定年。`author_activity_periods.csv` 单独保存作者层证据：有编年资料时使用活动期；仅有完整生卒年时才作为低置信度兜底；资料不足则明确为 `unknown`。

`poem_dates.csv` 另含下列展示字段，供后续竖版时间线或海报使用：

- `timeline_year`、`timeline_status`、`timeline_basis`：展示年份、其来源类别和计算依据
- `timeline_anchor_start/end`、`timeline_center_year`、`timeline_offset`：星团的锚点、中点与相对偏移
- `timeline_confidence`、`timeline_note`：视觉上可用于透明度或虚实等轻微区分的证据提示

当前 100 条记录中有 80 条获得展示坐标：作品级单年 27 条、范围中点 3 条、活动期星团 26 条、生卒期兜底 14 条、重复继承 10 条；其余 20 条保持 `unavailable`。同一作者的未定年独立作品按 `record_id` 稳定排序，以锚点中点为中心对称展开，完整星团宽度限制在 12 至 30 年。这个位置仅服务于艺术化的时间组织，不应作为作品写作年份引用。

重新查询开放接口并生成审计表：

```bash
python3 scripts/build_poem_dates.py \
  --manual-input data/poem_dates_manual.csv \
  --activity-input data/author_activity_periods.csv
```

该研究脚本使用 Python 的 `certifi` 证书包。接口开放数据限非商业用途；当前新增候选年份均保持低置信度或待复核状态，正式发布前仍应核对所列年谱、编年笺注或纸本原页。
