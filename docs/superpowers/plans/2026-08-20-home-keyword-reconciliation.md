# Homepage and Keyword-River Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Combine the uncommitted `main`-worktree edits to the homepage and keyword-river page with the current Figma-sequence worktree without losing either set of changes.

**Architecture:** Both worktrees share `e8bb957` as their common base. Generate one isolated three-way comparison per page, carry only main-only hunks into the Figma-sequence version, then use existing static-site tests and a local browser smoke check to validate the unified preview.

**Tech Stack:** Static HTML/CSS/JavaScript, Git worktrees, Node test runner, Python validation and smoke-test scripts.

**Spec:** User-approved reconciliation request in the current Codex conversation, 2026-08-20.

## Global Constraints

- Keep the existing `codex/figma-page-sequence` worktree and branch; do not reset, clean, or overwrite user changes.
- Treat the current `main` versions of `index.html` and `keyword-river.html` as an additional source of approved work, not as disposable changes.
- Reconcile only `index.html`, `keyword-river.html`, and any directly referenced main-only assets or tests required by those pages.
- Do not commit or merge into `main` until the user has reviewed the unified local preview.
- Preview the combined site only from `http://127.0.0.1:8000/`.

---

### Task 1: Reconcile homepage changes

**Files:**
- Modify: `index.html`
- Potentially copy: `assets/img/` files referenced only by main's homepage
- Potentially copy: `scripts/test_index_intro.py`

**Interfaces:**
- Consumes: base revision `e8bb957`, main worktree's uncommitted homepage diff, Figma-sequence worktree's uncommitted homepage diff.
- Produces: one homepage containing both non-conflicting change sets and no references to missing assets.

- [ ] **Step 1: Write the failing provenance test**

Add a Node test that asserts the reconciled homepage retains each unique, user-visible marker identified from both worktree diffs.

- [ ] **Step 2: Run the targeted test to verify it fails**

Run: `node --test tests/site-navigation.test.cjs`

Expected: FAIL until the main-only homepage marker is present in the Figma-sequence worktree.

- [ ] **Step 3: Generate and inspect a three-way comparison**

Run `git diff e8bb957 -- index.html` in each worktree and compare both patches section-by-section. Copy only main-only source hunks and assets that do not replace current Figma-sequence behavior.

- [ ] **Step 4: Apply the minimal reconciliation**

Use `apply_patch` to integrate the chosen main-only homepage changes into the Figma-sequence `index.html`; copy required referenced assets without removing current Figma-sequence assets.

- [ ] **Step 5: Run the targeted test to verify it passes**

Run: `node --test tests/site-navigation.test.cjs`

Expected: PASS with the expected homepage marker and existing navigation assertions.

### Task 2: Reconcile keyword-river changes

**Files:**
- Modify: `keyword-river.html`

**Interfaces:**
- Consumes: base revision `e8bb957`, main worktree's uncommitted keyword-river diff, Figma-sequence worktree's uncommitted keyword-river diff.
- Produces: one keyword-river page that preserves both non-conflicting page changes.

- [ ] **Step 1: Write the failing provenance test**

Add an assertion to the relevant page test for a unique main-only visible marker that must survive the reconciliation.

- [ ] **Step 2: Run the targeted test to verify it fails**

Run: `node --test tests/site-navigation.test.cjs`

Expected: FAIL until the main-only keyword-river marker is present.

- [ ] **Step 3: Generate and inspect a three-way comparison**

Run `git diff e8bb957 -- keyword-river.html` in each worktree and identify non-overlapping content, style, and interaction changes.

- [ ] **Step 4: Apply the minimal reconciliation**

Use `apply_patch` to carry main-only changes into the Figma-sequence page without removing current page navigation and common-style integration.

- [ ] **Step 5: Run the targeted test to verify it passes**

Run: `node --test tests/site-navigation.test.cjs`

Expected: PASS.

### Task 3: Validate the unified preview

**Files:**
- Verify: `index.html`, `keyword-river.html`, referenced assets, existing tests

**Interfaces:**
- Consumes: reconciled worktree from Tasks 1–2.
- Produces: evidence that all six pages and local resources load from the one worktree.

- [ ] **Step 1: Run static checks**

Run: `git diff --check`

Expected: no whitespace errors.

- [ ] **Step 2: Run full regression suite**

Run: `npm test`

Expected: Node tests, Python tests, project validation, and smoke test all pass.

- [ ] **Step 3: Visually check unified local routes**

Open `http://127.0.0.1:8000/index.html` and `http://127.0.0.1:8000/keyword-river.html`; confirm no missing-image or console-load errors.

- [ ] **Step 4: Report remaining true conflicts**

Report any section where both worktrees changed the same visual behavior differently and request a design choice rather than silently choosing.
