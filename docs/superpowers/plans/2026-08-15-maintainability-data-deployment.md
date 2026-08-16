# Maintainability, Data Integrity, and Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the static Tang-poetry visualization project easier to maintain, data-consistent, and reliably runnable through a local static server without changing the core visualizations.

**Architecture:** Keep the project framework-free. Add a small shared asset layer for global styles and navigation behavior, move authoritative data into `data/`, and add a dependency-free Python validation script plus npm scripts for repeatable local checks. Existing page filenames remain valid; pages that still contain page-specific chart data are updated only where the first-stage data audit requires it.

**Tech Stack:** HTML, CSS, browser JavaScript, D3 v7, ECharts 5.4.3, p5.js 1.7.0, Python 3 standard library, npm scripts.

## Global Constraints

- Preserve existing page URLs and the meaning of existing visual encodings.
- Treat the current CSV count of 100 poetry records as the authoritative sample size.
- Do not add a frontend framework or a build step.
- Keep raw data content unchanged except for relocating files and correcting demonstrably stale display copy.
- Use relative local paths so the project works from a static server subpath.
- Do not commit generated output, caches, or dependency directories.

### Task 1: Add project structure and repeatable commands

**Files:**
- Create: `package.json`
- Create: `README.md`
- Create: `scripts/validate_project.py`
- Create: `.gitignore`
- Create: `data/poetry_with_detailed_clusters_sankey.csv`
- Create: `data/地方名称及经纬度.csv`
- Create: `data/tang_dynasty_detailed_boundary.json`
- Delete after relocation: the three matching root-level data files

**Interfaces:**
- `python3 scripts/validate_project.py` exits 0 when required files and data schemas are valid, otherwise exits 1 with actionable errors.
- `npm run validate` invokes that validator.
- `npm run dev` starts `python3 -m http.server 8000` from the project root.

- [ ] Add the package scripts and a minimal README describing the static-server requirement, page entry points, data files, CDN dependencies, and sample-size convention.
- [ ] Implement validator checks for required columns, non-empty poetry rows, valid UTF-8 CSV, valid JSON, numeric frequencies, valid coordinate pairs, and the expected sample count of 100.
- [ ] Move the three authoritative data files into `data/` without changing their contents.
- [ ] Add `.gitignore` entries for Python caches, npm dependencies, local server logs, and generated screenshots.
- [ ] Run `python3 scripts/validate_project.py` and confirm it passes.

### Task 2: Centralize shared page styling and navigation behavior

**Files:**
- Create: `assets/css/common.css`
- Create: `assets/js/navigation.js`
- Modify: `index.html`
- Modify: `interactive.html`
- Modify: `geography.html`
- Modify: `poetry-emotion.html`
- Modify: `word-association.html`
- Modify: `keyword-river.html`
- Modify: `circular_sankey.html`

**Interfaces:**
- `assets/js/navigation.js` exposes `window.PoetryViz.navigate(path)` and initializes links marked with `data-route`.
- `assets/css/common.css` owns shared reset, page shell, top navigation, active underline, and footer/continue-button styles.

- [ ] Create shared CSS classes for the repeated 1440px shell, navigation line, logo placement, home button, menu button, active tab, and continue control while preserving the existing colors and geometry.
- [ ] Replace repeated inline navigation handlers with semantic anchors carrying `data-route` attributes.
- [ ] Load the shared CSS and navigation script from every formal page.
- [ ] Remove stale CRA-only `%PUBLIC_URL%` favicon, manifest, and apple-touch-icon references unless matching local files are added.
- [ ] Keep chart-specific CSS and inline chart logic local to each page.
- [ ] Run a local server and confirm all formal pages return HTTP 200.

### Task 3: Normalize data paths and stale sample-size copy

**Files:**
- Modify: `interactive.html`
- Modify: `sketch.js`
- Modify: `keyword-river.html`
- Modify: `circular_sankey.html`
- Modify: `poetry-emotion.html`
- Modify: `word-association.html`
- Modify: `geography.html`
- Modify: `可行情感1.html`
- Modify: `词频可视化.html`

**Interfaces:**
- Browser data requests use `data/poetry_with_detailed_clusters_sankey.csv`, `data/地方名称及经纬度.csv`, and `data/tang_dynasty_detailed_boundary.json`.
- User-facing sample text uses `100首唐代咏侠诗` where it describes the shared poetry corpus.

- [ ] Update p5.js preload paths in `sketch.js` and D3 paths in the relationship pages to use `data/`.
- [ ] Update any local JSON/CSV fetch paths in the geography page and its fallback/error messages.
- [ ] Replace stale “101首” labels and comments with “100首” only where they refer to the shared poetry corpus.
- [ ] Recheck that the emotion and word-frequency pages still load their page-specific embedded arrays without changing their values.
- [ ] Run the validator and search for remaining `101首` references.

### Task 4: Add smoke checks and verify the handoff

**Files:**
- Modify: `package.json`
- Create: `scripts/smoke_test.py`

**Interfaces:**
- `python3 scripts/smoke_test.py` starts or targets a local static server contract and verifies each formal HTML entry point is reachable with HTTP 200 and all required local data paths exist.
- `npm test` runs both validation and smoke checks when a server is available, with a clear message if the server is not running.

- [ ] Implement a small standard-library smoke test that accepts `--base-url` and checks the nine HTML pages plus required data resources.
- [ ] Run the server on port 8000 and execute the smoke test against it.
- [ ] Run `git diff --check`, `node --check sketch.js`, the validator, and the smoke test.
- [ ] Review the final diff for accidental data changes, duplicated path mistakes, and unrelated edits.
