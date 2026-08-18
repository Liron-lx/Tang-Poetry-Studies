# Foundation and Prologue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the formal-page smoke test match the current site, then rebuild `index.html` as the Figma 00/01 prologue with testable state transitions and accessible interactions.

**Architecture:** Keep the project framework-free. The formal route list remains in `scripts/smoke_test.py`; a small CommonJS-and-browser compatible prologue state module owns the sequence of view states, while `assets/js/prologue.js` maps those states to DOM classes in `index.html`. Page-specific CSS stays in `index.html` until it is reused by another page; shared tokens and navigation stay in `assets/css/common.css` and `assets/js/site.js`.

**Tech Stack:** Static HTML/CSS, browser JavaScript, Node built-in test runner, Python `unittest`, existing local image/SVG assets, and the existing local Python static server.

**Spec:** `docs/superpowers/specs/2026-08-18-figma-page-sequence-design.md`

## Global Constraints

- Work only in this worktree and never alter its parent checkout or the outer repository.
- Retain the `data/` source files and their 100-poem / 76-location source counts.
- Formal smoke tests must cover only `index.html`, `xiayi-scroll.html`, `interactive.html`, `poets.html`, `emotions.html`, and `keyword-river.html`.
- Desktop hover may preview but never lock a selection; mobile interaction must work by click or keyboard alone.
- In `prefers-reduced-motion`, show final state without timed animation or smooth-scroll dependence.
- Treat Figma red text as implementation notes, never reader-facing copy.
- Do not begin later pages until the user has reviewed the local preview of this prologue page.

---

### Task 1: Make the smoke-test route contract executable

**Files:**
- Create: `scripts/test_smoke_test.py`
- Modify: `scripts/smoke_test.py:14-23`
- Modify: `package.json:6-10`

**Interfaces:**
- Consumes: `scripts.smoke_test.PAGES`, the formal routes defined by the specification.
- Produces: `python3 -m unittest discover -s scripts -p "test_*.py"` as the repeatable Python regression test command; `npm test` includes it before serving-page checks.

- [ ] **Step 1: Write the failing regression test for the formal route list**

Create `scripts/test_smoke_test.py`:

```python
import unittest

from smoke_test import PAGES


class FormalRouteTest(unittest.TestCase):
    def test_smoke_test_covers_only_formal_pages(self) -> None:
        self.assertEqual(
            PAGES,
            [
                "index.html",
                "xiayi-scroll.html",
                "interactive.html",
                "poets.html",
                "emotions.html",
                "keyword-river.html",
            ],
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify it fails because archived routes are still listed**

Run: `python3 -m unittest discover -s scripts -p 'test_smoke_test.py' -v`

Expected: FAIL showing that `geography.html`, `poetry-emotion.html`, `word-association.html`, `circular_sankey.html`, `可行情感1.html`, and `词频可视化.html` are still present.

- [ ] **Step 3: Replace the stale smoke-test page list and include the Python tests in npm test**

Replace the `PAGES` value in `scripts/smoke_test.py` with:

```python
PAGES = [
    "index.html",
    "xiayi-scroll.html",
    "interactive.html",
    "poets.html",
    "emotions.html",
    "keyword-river.html",
]
```

Change the `test` script in `package.json` to:

```json
"test": "python3 -m unittest discover -s scripts -p 'test_*.py' && python3 scripts/validate_project.py && python3 scripts/smoke_test.py --base-url http://127.0.0.1:8000"
```

- [ ] **Step 4: Run the route regression test and data validation**

Run: `python3 -m unittest discover -s scripts -p 'test_*.py' -v && npm run validate`

Expected: all Python tests pass and validation reports 100 poetry rows with valid local schemas.

- [ ] **Step 5: Commit the route-contract repair**

```bash
git add scripts/test_smoke_test.py scripts/smoke_test.py package.json
git commit -m "test: align smoke pages with formal routes"
```

### Task 2: Extract the prologue sequence into a testable state machine

**Files:**
- Create: `assets/js/prologue-state.js`
- Create: `tests/prologue-state.test.cjs`
- Modify: `package.json:6-10`

**Interfaces:**
- Consumes: a `phase` string and an interaction event.
- Produces: `PrologueState.next(phase, event)` returning one of `splash`, `cover`, `poem`, `preface`, or `unfurled`; `assets/js/prologue.js` will consume this interface in Task 3.

- [ ] **Step 1: Write the failing Node test for legal and ignored transitions**

Create `tests/prologue-state.test.cjs`:

```javascript
const test = require("node:test");
const assert = require("node:assert/strict");
const { next } = require("../assets/js/prologue-state.js");

test("the prologue advances through the Figma reading sequence", () => {
  assert.equal(next("splash", "BEGIN"), "cover");
  assert.equal(next("cover", "OPEN_BOOK"), "poem");
  assert.equal(next("poem", "SHOW_PREFACE"), "preface");
  assert.equal(next("preface", "UNFURL"), "unfurled");
});

test("the prologue ignores an event that is unavailable in the current state", () => {
  assert.equal(next("splash", "UNFURL"), "splash");
  assert.equal(next("unfurled", "OPEN_BOOK"), "unfurled");
});
```

- [ ] **Step 2: Run the Node test and verify it fails because the module is missing**

Run: `node --test tests/prologue-state.test.cjs`

Expected: FAIL with `Cannot find module '../assets/js/prologue-state.js'`.

- [ ] **Step 3: Implement the smallest browser-and-Node compatible state module**

Create `assets/js/prologue-state.js`:

```javascript
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.PoetryViz = root.PoetryViz || {};
  root.PoetryViz.PrologueState = api;
}(typeof globalThis === "undefined" ? this : globalThis, function () {
  "use strict";

  var transitions = {
    splash: { BEGIN: "cover" },
    cover: { OPEN_BOOK: "poem" },
    poem: { SHOW_PREFACE: "preface" },
    preface: { UNFURL: "unfurled" },
    unfurled: {}
  };

  function next(phase, event) {
    return (transitions[phase] && transitions[phase][event]) || phase;
  }

  return { next: next };
}));
```

Update the `test` script in `package.json` so the state-machine tests run in the normal project command:

```json
"test": "node --test tests/prologue-state.test.cjs && python3 -m unittest discover -s scripts -p 'test_*.py' && python3 scripts/validate_project.py && python3 scripts/smoke_test.py --base-url http://127.0.0.1:8000"
```

- [ ] **Step 4: Run the state tests and the existing project tests**

Run: `npm test`

Expected: Node reports two passing tests, Python tests remain green, validation reports valid local data, and the six formal pages are reachable.

- [ ] **Step 5: Commit the state-machine boundary**

```bash
git add assets/js/prologue-state.js tests/prologue-state.test.cjs package.json
git commit -m "feat: add prologue state machine"
```

### Task 3: Rebuild the Figma 00/01 prologue as one accessible page

**Files:**
- Create: `assets/js/prologue.js`
- Modify: `index.html:1-516`
- Modify: `assets/css/common.css:1-293`
- Test: `tests/prologue-state.test.cjs`

**Interfaces:**
- Consumes: `window.PoetryViz.PrologueState.next`, local visual assets from `image/`, and the existing `XIA` navigation setup.
- Produces: an `index.html` with a `data-prologue-phase` attribute, real buttons for each state advance, and the six-route chapter directory.

- [ ] **Step 1: Add a failing DOM-contract test for the required prologue controls**

Append this test to `scripts/test_smoke_test.py`:

```python
from pathlib import Path


class PrologueMarkupTest(unittest.TestCase):
    def test_index_contains_the_five_figma_prologue_states(self) -> None:
        index = (Path(__file__).parents[1] / "index.html").read_text(encoding="utf-8")
        for phase in ("splash", "cover", "poem", "preface", "unfurled"):
            self.assertIn(f'data-prologue-phase="{phase}"', index)
        for control_id in ("beginBtn", "openBookBtn", "prefaceBtn", "unfurlBtn"):
            self.assertIn(f'id="{control_id}"', index)
```

- [ ] **Step 2: Run the DOM-contract test and verify the old homepage fails it**

Run: `python3 -m unittest discover -s scripts -p 'test_smoke_test.py' -v`

Expected: FAIL because the current page has no `splash` state or `beginBtn` and `openBookBtn` controls.

- [ ] **Step 3: Replace the homepage structure with explicit Figma states**

In `index.html`, retain the shared stylesheet and `assets/js/site.js`, then replace the old hero/evidence markup with these state-bearing sections in order:

```html
<main class="prologue" data-prologue-root>
  <section class="prologue-state splash" data-prologue-phase="splash">
    <img src="image/title-brush-诗风侠影.png" alt="诗风侠影" />
    <p>唐代侠义诗信息可视化网页</p>
    <button id="beginBtn" type="button">开始探索</button>
  </section>
  <section class="prologue-state book-cover" data-prologue-phase="cover" hidden>
    <button id="openBookBtn" type="button" aria-label="打开《横吹曲辞·出塞》">打开诗卷</button>
  </section>
  <section class="prologue-state book-poem" data-prologue-phase="poem" hidden>
    <button id="prefaceBtn" type="button">继续</button>
  </section>
  <section class="prologue-state book-preface" data-prologue-phase="preface" hidden>
    <button id="unfurlBtn" type="button">展卷寻侠</button>
  </section>
  <section class="prologue-state unfurled" data-prologue-phase="unfurled" hidden>
    <!-- 长安、边塞、数字与五章目录 -->
  </section>
</main>
```

Use the existing `image/title-brush-诗风侠影.png`, `image/act2-changan.png`, and `image/act2-frontier.png` as local fallback artwork; do not add a network image dependency. Preserve the existing six-route directory, but make each row a semantic `<a>` that exposes its text and target without hover.

- [ ] **Step 4: Add the phase-to-DOM controller and reduced-motion behavior**

Create `assets/js/prologue.js` with the following controller shape:

```javascript
(function () {
  "use strict";
  var root = document.querySelector("[data-prologue-root]");
  if (!root) return;
  var phase = "splash";
  var next = window.PoetryViz.PrologueState.next;

  function render() {
    root.querySelectorAll("[data-prologue-phase]").forEach(function (section) {
      var active = section.dataset.prologuePhase === phase;
      section.hidden = !active;
      section.setAttribute("aria-hidden", String(!active));
    });
    root.dataset.currentPhase = phase;
  }

  function advance(event) {
    phase = next(phase, event);
    render();
  }

  document.getElementById("beginBtn").addEventListener("click", function () { advance("BEGIN"); });
  document.getElementById("openBookBtn").addEventListener("click", function () { advance("OPEN_BOOK"); });
  document.getElementById("prefaceBtn").addEventListener("click", function () { advance("SHOW_PREFACE"); });
  document.getElementById("unfurlBtn").addEventListener("click", function () { advance("UNFURL"); });
  render();
}());
```

Load `assets/js/prologue-state.js` before `assets/js/prologue.js`. Define page-local CSS for state visibility, book opening, poem-line reveal, landscape layers, directory expansion, and the corresponding `@media (prefers-reduced-motion: reduce)` final-state presentation. Keep global visual tokens in `common.css`; only add tokens there if at least two pages consume them.

- [ ] **Step 5: Run automated verification and visually inspect the page**

Run in one terminal: `npm run dev`

Run in another terminal: `npm test && node --test tests/prologue-state.test.cjs`

Then open `http://127.0.0.1:8000/index.html` and verify in this exact order: `开始探索 → 打开诗卷 → 继续 → 展卷寻侠 → 五章目录`; resize to 390 px wide; enable reduced motion and confirm controls remain usable.

- [ ] **Step 6: Commit the user-reviewable prologue**

```bash
git add index.html assets/js/prologue.js assets/js/prologue-state.js assets/css/common.css scripts/test_smoke_test.py tests/prologue-state.test.cjs package.json
git commit -m "feat: rebuild figma prologue sequence"
```

### Task 4: Present the prologue checkpoint before any subsequent page

**Files:**
- Modify: `README.md:11-24`

**Interfaces:**
- Consumes: the completed `index.html` route and validation commands.
- Produces: concise local-running instructions and an explicit user checkpoint before `xiayi-scroll.html` work.

- [ ] **Step 1: Add a concise README note for the prologue interaction sequence**

Add this paragraph after the formal route list:

```markdown
首页序章按“片头 → 封面 → 诗句 → 序词 → 展卷”推进。桌面和移动端均通过按钮点击推进；系统启用减少动态效果时，状态切换不依赖动画。
```

- [ ] **Step 2: Run full project verification before presenting the checkpoint**

Run: `npm test && git diff --check`

Expected: data validation, formal-route smoke test, Python regression tests, Node state tests, and whitespace check all exit with status 0.

- [ ] **Step 3: Commit the documentation update**

```bash
git add README.md
git commit -m "docs: describe prologue interaction"
```

- [ ] **Step 4: Provide the local preview and stop for review**

Report the URL `http://127.0.0.1:8000/index.html`, list the tested interaction sequence, and ask for confirmation before beginning the “时” page plan.
