# 唐代侠义诗可视化

**在线访问：<https://liron-lx.github.io/Tang-Poetry-Studies/>**（GitHub Pages，随 `main` 分支推送自动部署）

这是一个以唐代咏侠诗为对象的静态数字人文可视化项目。全站为六幕章回叙事：**序 · 时 · 地 · 人 · 心 · 存**，视觉依据《唐代侠义诗可视化 · 视觉规范》（宣纸青绿体系），叙事架构见 `docs/narrative-architecture.md`。

## 本地运行

项目使用浏览器端 HTML、D3 和 ECharts，不需要构建步骤。由于页面需要通过 `fetch` 请求加载数据，请通过静态服务器访问：

```bash
npm run dev
```

或直接使用 Python：

```bash
python3 -m http.server 8000
```

然后打开 <http://127.0.0.1:8000/index.html>。

## 页面入口（六幕）

- `index.html`：序 · 何谓侠——考据悬念开场、语料事实带、六幕回目
- `xiayi-scroll.html`：一幕 · 侠从何来——五脉汇流横向河流图（河宽 = 十年诗作密度，朝代分期、755 事件线、待考雾域）
- `interactive.html`：二幕 · 侠行何处——唐代疆域地点分布 + 十处要地排行
- `poets.html`：三幕 · 侠者何人——五位诗人全身像、诗牌与系年证据
- `emotions.html`：四幕 · 侠心何似——双轨视角（侠客的世界 × 诗人的内心）、投射图、词象
- `keyword-river.html`：终幕 · 侠韵长存——诗人×主题矩阵、十二家主笔、数据与方法

首页序章按“片头 → 封面 → 诗句 → 序词 → 展卷”推进。桌面和移动端均通过按钮点击推进；系统启用减少动态效果时，状态切换不依赖动画。

被替换的旧版页面已移入 `archive/`（含 p5.js 地图 sketch.js、弦图、旧词频/情感页）。

## 数据

权威数据位于 `data/`：

- `poetry_with_detailed_clusters_sankey.csv`：100 条诗歌记录及聚类类别
- `emotion_scores.csv`：100 条诗歌的八维情感强度评分（0-10 分），`emotions.html` 从此读取
- `word_frequency.csv`：283 个词语的词频与分类全量版，`emotions.html` 从此读取
- `poets.json`：五位高频诗人的档案、诗作、系年与双轨得分（`scripts/build_poets_json.py` 生成），`poets.html` 从此读取
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
