# 「心」页交互 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 以用户给定的 05 素材和 CSV 数据，在 `emotions.html` 实现完整 05-1 与可恢复 05-2 交互。

**Architecture:** 页面保留原有单页 ECharts 数据加载，新增三个独立状态：`worldSelection`、`currentPoet`、`selectedCategory`。图表保持真实 CSV 数据；HTML 场景负责默认插画、对象选择和状态转换。

**Tech Stack:** 静态 HTML/CSS/JavaScript、ECharts 5、`XIA.loadCSV`、Node `node:test`。

**Spec:** `docs/superpowers/specs/2026-08-20-emotions-interaction-design.md`

## Global Constraints

- 只使用 `/Users/yueruili/Documents/ChatGPT/唐代侠义诗可视化/网页素材/05-心-*` 的用户素材，不生成或重绘图像。
- `word_frequency.csv` 的 12 个类别及物品映射不可变；不修改 CSV。
- 每个场景可通过当前选择或场景空白处恢复默认状态。
- 处理 `prefers-reduced-motion: reduce`，并通过 `http://127.0.0.1:8000/emotions.html` 验证，不以 `file://` 运行。
- 不提交 worktree 中现存的无关改动。

---

### Task 1: 添加用户素材与交互结构

**Files:**

- Create: `image/emotions/worlds/{侠客的世界,诗人的内心}.png`
- Create: `image/emotions/projection/地面.png`、五位诗人 SVG
- Create: `image/emotions/lexicon/{桌子,窗,背景半圆,背景地面}.svg`、十二件物品 SVG
- Create: `tests/emotions-page.test.cjs`
- Modify: `emotions.html:24-137`

**Interfaces:** Produces `#worldXia`、`#worldShi`、`#poetStage`、`#lexScene`、5 个 `[data-poet]` 和 24 个 `[data-category]`（12 个物品加 12 个筛选项）。

- [ ] **Step 1: Write the failing test**

```js
test("the emotions page exposes supplied illustration, poet, and lexicon-item controls", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  assert.match(html, /id="worldXia"/);
  assert.match(html, /id="poetStage"/);
  assert.match(html, /id="lexScene"/);
  assert.equal((html.match(/data-poet="/g) || []).length, 5);
  assert.equal((html.match(/data-category="/g) || []).length, 24);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/emotions-page.test.cjs`

Expected: FAIL because these structures do not exist.

- [ ] **Step 3: Copy source assets and create semantic DOM**

Copy every specified asset into `image/emotions/`. Replace chart-only world cards with world regions containing art and hidden chart hosts; replace `#poetFilter` with five image buttons above the supplied ground; build `#lexScene` from window, desk, floor, semicircle and twelve object buttons.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/emotions-page.test.cjs`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add emotions.html image/emotions tests/emotions-page.test.cjs && git commit -m "feat: add emotions scene assets"`

### Task 2: 两个世界的可恢复折线图

**Files:**

- Modify: `emotions.html:25-60,96-113,193-233`
- Modify: `tests/emotions-page.test.cjs`

**Interfaces:** Consumes `worldChart(id, dims)`; produces `setWorldSelection(name)` with `'xia'`、`'shi'` 或 `null` and `.is-expanded`.

- [ ] **Step 1: Write the failing test**

```js
test("two worlds keeps art by default and has reversible one-side chart state", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  assert.match(html, /function setWorldSelection\(name\)/);
  assert.match(html, /worldSelection === name \? null : name/);
  assert.match(html, /classList\.toggle\('is-expanded'/);
  assert.match(html, /prefers-reduced-motion/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/emotions-page.test.cjs`

Expected: FAIL because no state setter exists.

- [ ] **Step 3: Add default/expanded state CSS and event handlers**

Keep `.world-art` visible by default. On selected side, fade art, shift title up, reveal that chart, and resize its ECharts instance after transition; preserve the opposite illustration. Bind current-side repeated click and blank-section click to reset. Make animation duration zero under reduced motion.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/emotions-page.test.cjs`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add emotions.html tests/emotions-page.test.cjs && git commit -m "feat: add reversible two worlds charts"`

### Task 3: 用诗人图像筛选投射图

**Files:**

- Modify: `emotions.html:42-61,115-120,234-388`
- Modify: `tests/emotions-page.test.cjs`

**Interfaces:** Consumes `#poetStage`, `FIVE`, `renderScatter()`; produces `setCurrentPoet(name)` and `.is-selected` / `.is-muted`.

- [ ] **Step 1: Write the failing test**

```js
test("projection filters from figures and resets from blank chart space", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  assert.doesNotMatch(html, /id="poetFilter"/);
  assert.match(html, /function setCurrentPoet\(name\)/);
  assert.match(html, /classList\.toggle\('is-muted'/);
  assert.match(html, /scatterChart\.addEventListener\('click'/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/emotions-page.test.cjs`

Expected: FAIL because text controls still drive the filter.

- [ ] **Step 3: Implement figure hover, selection, and clear**

Remove text-filter creation. `setCurrentPoet(name)` must toggle off on a second selection, make non-selected people grey, preserve their scatter dots at low opacity, and retain selected-author lines/centroid. Hover or keyboard focus temporarily previews a person. A blank click on the chart clears selection.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/emotions-page.test.cjs`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add emotions.html tests/emotions-page.test.cjs && git commit -m "feat: filter projection from poet figures"`

### Task 4: 实现词象的物品—类别焦点状态

**Files:**

- Modify: `emotions.html:62-74,124-137,389-531`
- Modify: `tests/emotions-page.test.cjs`

**Interfaces:** Consumes `#lexScene`, `#catChips`, `renderBar(category)`; produces `CATEGORY_OBJECTS`, `setLexiconCategory(category)`, `.lexicon-focused`.

- [ ] **Step 1: Write the failing test**

```js
test("lexicon uses twelve approved mappings and reversible focus", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  assert.match(html, /var CATEGORY_OBJECTS = \{/);
  assert.match(html, /'人物形象类': '剑'/);
  assert.match(html, /'风霜雨雪水云类': '新月'/);
  assert.match(html, /function setLexiconCategory\(category\)/);
  assert.doesNotMatch(html, /词林十三圃/);
  assert.doesNotMatch(html, /十三个类别/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/emotions-page.test.cjs`

Expected: FAIL because old treemap and copy remain.

- [ ] **Step 3: Implement exact map and selected object motion**

Set the 12-category `CATEGORY_OBJECTS` exactly as the approved specification. Remove treemap functions and `#lexField`; retain real-data `renderBar`. Clicked object or chip enters a shared selected state: other props and scene layers fade, selected object moves and enlarges over `背景圆.png` at left, and the category’s top-eight bar chart appears at right. Reclicking selected object/chip or blank `#lexScene` restores the full scene. Replace old 13-category/词林 copy with the approved 12-class description.

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/emotions-page.test.cjs`

Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add emotions.html tests/emotions-page.test.cjs && git commit -m "feat: add word-object category focus"`

### Task 5: 服务器、窄屏与视觉状态验收

**Files:**

- Modify: `tests/emotions-page.test.cjs`
- Modify: `emotions.html` only if live visual QA finds a specific defect

**Interfaces:** Consumes Tasks 1–4; produces verified desktop and narrow-page states.

- [ ] **Step 1: Write the failing test**

```js
test("emotions retains CSV loaders and responsive poet-stage rules", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  assert.match(html, /XIA\.loadCSV\('data\/emotion_scores\.csv'\)/);
  assert.match(html, /XIA\.loadCSV\('data\/word_frequency\.csv'\)/);
  assert.match(html, /@media \(max-width: 820px\)/);
  assert.match(html, /\.poet-stage[\s\S]*flex-wrap/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/emotions-page.test.cjs`

Expected: FAIL until responsive poet-stage styling exists.

- [ ] **Step 3: Run live visual QA at required states**

Start the local server, open `http://127.0.0.1:8000/emotions.html`, and inspect: default, each world expanded, a selected poet, a selected object category, both reset paths, and 820 px viewport. Confirm aspect ratios, click targets, and CSV requests succeed without console errors.

- [ ] **Step 4: Run verification suite**

Run: `node --test tests/emotions-page.test.cjs && npm test && git diff --check`

Expected: all tests PASS and no whitespace errors.

- [ ] **Step 5: Commit**

Run: `git add emotions.html tests/emotions-page.test.cjs && git commit -m "test: verify emotions page interactions"`
