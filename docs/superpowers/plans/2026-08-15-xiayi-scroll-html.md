# 侠义长卷 HTML Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建一张直接读取现有 100 首唐代咏侠诗时间轴数据的竖版主视觉 HTML《侠义长卷：一百首唐代咏侠诗的五脉流变》。

**Architecture:** 新页面使用浏览器端 D3 读取 `data/poem_dates.csv`，将五类主题渲染为可辨别但不等宽分栏的山水脉流，并将现有 `timeline_status` 映射为节点的实体/雾化层级。未能定位的记录不进入虚构时间线，而是在页面末端的待考雾域保留为可交互诗作。

**Tech Stack:** 静态 HTML、CSS、原生 JavaScript、D3 v7 CDN、既有 Python smoke test。

## Global Constraints

- 不改动 `data/poem_dates.csv`、`data/author_activity_periods.csv` 或作品级系年字段。
- 使用 [docs/visual-language-xiayi-scroll.md](../../visual-language-xiayi-scroll.md) 的固定视觉语言。
- 显示全部 100 条诗歌记录；`unavailable` 记录必须可见且标为待考。
- 只以 `timeline_year` 进行时间定位，不以 `date_start/end` 或作者生卒年自行推测位置。
- 页面可在窄屏上横向缩放/滚动，图例、节点焦点和文本对比度保持可用。
- 不修改未跟踪的 `高频诗人画像/` 与 `docs/superpowers/plans/2026-08-15-maintainability-data-deployment.md`。

---

### Task 1: 固化视觉语言并注册页面烟雾测试

**Files:**
- Create: `docs/visual-language-xiayi-scroll.md`
- Modify: `scripts/smoke_test.py`

**Interfaces:**
- Produces: 固定色彩、证据层级和五脉映射规则。
- Produces: smoke test 对 `xiayi-scroll.html` 的 HTTP 200 断言。

- [ ] **Step 1: 写入失败的页面资源测试**

在 `scripts/smoke_test.py` 的 `PAGES` 中加入：

```python
"xiayi-scroll.html",
```

- [ ] **Step 2: 运行烟雾测试并确认新页面不存在**

Run: `npm test`

Expected: FAIL，报告 `xiayi-scroll.html` 连接失败或 HTTP 404。

- [ ] **Step 3: 写入视觉语言文档**

文档必须固定：暖白宣纸底、低饱和青绿/灰蓝/墨色、五脉映射、真实/推定/待考的证据层级，以及不采用商业武侠风的边界。

- [ ] **Step 4: 暂不提交**

本任务的文档和烟雾测试与页面在 Task 2 一起提交，避免单独提交一个必然失败的页面检查。

### Task 2: 实现五脉长卷页面

**Files:**
- Create: `xiayi-scroll.html`
- Modify: `scripts/smoke_test.py`

**Interfaces:**
- Consumes: `data/poem_dates.csv` 的 `record_id`、`author`、`title_original`、`cluster`、`timeline_year`、`timeline_status`、`timeline_note`。
- Produces: 独立打开的可滚动长卷页面；每条记录对应一个可聚焦 SVG 节点。

- [ ] **Step 1: 先注册烟雾检查并确认失败**

在 `PAGES` 末尾加入：

```python
"xiayi-scroll.html",
```

Run: `npm test`

Expected: FAIL，`xiayi-scroll.html` 不存在。

- [ ] **Step 2: 创建页面骨架**

创建含下列可访问结构的 `xiayi-scroll.html`：

```html
<main>
  <header class="scroll-intro">...</header>
  <section aria-labelledby="scroll-title">
    <svg id="scroll-chart" role="img" aria-label="一百首唐代咏侠诗的五脉流变"></svg>
  </section>
  <aside id="poem-detail" aria-live="polite"></aside>
</main>
```

引入 D3 v7，`fetch("data/poem_dates.csv")` 后以 `d3.csvParse` 读取记录。

- [ ] **Step 3: 渲染五脉、年代、节点和待考雾域**

实现 `renderScroll(rows)`：

```js
function renderScroll(rows) {
  const available = rows.filter((row) => row.timeline_year);
  const unavailable = rows.filter((row) => !row.timeline_year);
  // y: 608–904 年；按 cluster 生成五条缓慢变形的 SVG 带状路径。
  // observed_* 为实点，inferred_* 为半透明点，duplicate_inherited 为小伴生点。
  // unavailable 在末端雾域均匀排布，保留作者和篇名详情。
}
```

每个节点必须可聚焦并在 `mouseenter`、`focus`、`click` 时更新 `#poem-detail`。

- [ ] **Step 4: 写入固定视觉令牌与响应式规则**

CSS 使用文档指定的色彩；以 `feTurbulence` 形成轻纸张纹理，以低透明度等高线和水波线承载年代网格。页面最小画布宽度为 `960px`，窄屏容器允许横向滚动，`prefers-reduced-motion` 时关闭节点浮动动画。

- [ ] **Step 5: 运行完整验证**

Run: `npm test && python3 -m unittest discover -s scripts -p 'test_build_poem_dates.py' -v`

Expected: PASS，且 smoke test 报告 10 个页面。

- [ ] **Step 6: 浏览器视觉检查**

启动 `npm run dev`，在本地打开 `xiayi-scroll.html`，检查顶部题记、五脉、节点、待考雾域和窄屏横向滚动。若信息图形不易读，优先调整对比度、留白和节点重叠，不能以增加装饰替代。

- [ ] **Step 7: 提交**

```bash
git add docs/visual-language-xiayi-scroll.md docs/superpowers/plans/2026-08-15-xiayi-scroll-html.md xiayi-scroll.html scripts/smoke_test.py
git commit -m "feat: add xiayi scroll timeline poster"
```
