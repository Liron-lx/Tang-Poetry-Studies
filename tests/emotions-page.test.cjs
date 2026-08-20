const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const ROOT = path.resolve(__dirname, "..");
const PAGE = path.join(ROOT, "emotions.html");

test("the emotions page exposes supplied illustration, poet, and lexicon-item controls", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /id="worldXia"/);
  assert.match(html, /id="worldShi"/);
  assert.match(html, /id="poetStage"/);
  assert.match(html, /id="lexScene"/);
  assert.equal((html.match(/data-poet="/g) || []).length, 5);
  assert.equal((html.match(/data-category="/g) || []).length, 24);
});

test("two worlds keeps art by default and has a reversible one-side chart state", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /function setWorldSelection\(name\)/);
  assert.match(html, /worldSelection === name \? null : name/);
  assert.match(html, /classList\.toggle\('is-expanded'/);
  assert.match(html, /\.world\.is-expanded \.world-art \{[^}]*height: 0;/);
  assert.match(html, /class="world-divider" aria-hidden="true"/);
  assert.match(html, /\.world-divider \{ order: 2;[^}]*background: var\(--world-divider\);/s);
  assert.match(html, /\.world\.is-expanded \.world-divider \{ order: 1;/);
  assert.match(html, /\.world\.is-expanded \.w-caption \{ order: 2;/);
  assert.match(html, /\.world\.xia \{ --world-divider: var\(--ochre\); \}/);
  assert.match(html, /\.world\.shi \{ --world-divider: var\(--blue\); \}/);
  assert.match(html, /\.world\.is-expanded \.w-chart \{ order: 3; height: 300px;/);
  assert.match(html, /function replayWorldChart\(side\)/);
  assert.match(html, /chart\.clear\(\);/);
  assert.match(html, /animationDuration: 680/);
  assert.match(html, /replayWorldChart\(expandedSelection\);/);
  assert.match(html, /chart\.resize\(\);\s*chart\.clear\(\);\s*chart\.setOption\(worldChartOption\(dims\)/);
  assert.match(html, /\}, 460\);/);
  assert.match(html, /prefers-reduced-motion/);
});

test("two worlds places each illustration above its divider and removes processing-note copy", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  const xia = html.slice(html.indexOf('id="worldXia"'), html.indexOf('id="worldShi"'));

  assert.ok(xia.indexOf('class="world-art"') < xia.indexOf('class="w-title"'));
  assert.match(html, /\.world-divider \{[^}]*height: 2px;[^}]*background: var\(--world-divider\);/s);
  assert.doesNotMatch(html, /2026-08-16 审计修正/);
  assert.doesNotMatch(html, /分类口径以 word_frequency\.csv 为准/);
});

test("projection filters from figures and resets from blank chart space", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.doesNotMatch(html, /id="poetFilter"/);
  assert.match(html, /function setCurrentPoet\(name\)/);
  assert.match(html, /classList\.toggle\('is-muted'/);
  assert.match(html, /scatterChart\.addEventListener\('click'/);
});

test("lexicon uses twelve approved mappings and reversible focus", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /var CATEGORY_OBJECTS = \{/);
  assert.match(html, /'人物形象类': '剑'/);
  assert.match(html, /'风霜雨雪水云类': '新月'/);
  assert.match(html, /function setLexiconCategory\(category\)/);
  assert.doesNotMatch(html, /词林十三圃/);
  assert.doesNotMatch(html, /十三个类别/);
});

test("lexicon keeps the full supplied scene in the default state and reveals its chart only after selection", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /class="lexicon-layout" id="lexiconLayout"/);
  assert.match(html, /\.lexicon-layout \.lex-focus-panel \{ display: none; \}/);
  assert.match(html, /\.lexicon-layout\.is-focused \{ display: grid;/);
  assert.match(html, /lexiconLayout\.classList\.toggle\('is-focused'/);
});

test("emotions keeps white page fields and reserves the paper tint for the projection band", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /body\[data-chapter="xin"\] \{ background: #fff; \}/);
  assert.match(html, /#projection \{[^}]*background: var\(--paper\);/s);
});

test("lexicon uses a fixed 1060px artboard with explicit supplied coordinates and per-object focus states", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /\.lex-scene \{ width: 1060px; height: 525px;/);
  assert.match(html, /\.lex-window \{ width: 709\.43px; left: 313\.50px; top: 29\.44px;/);
  assert.match(html, /\.obj-jian \{ width: 43\.38px; height: 249\.50px; left: 575\.28px; top: 351\.00px; transform: rotate\(84deg\);/);
  assert.match(html, /\.lex-scene\.lexicon-focused \.obj-jian \{[^}]*--focus-width:/s);
  assert.match(html, /\.lex-scene\.lexicon-focused \.obj-baoxiang \{[^}]*--focus-width:/s);
});

test("the three emotion narratives have desktop screen sections with a mobile height fallback", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  assert.match(html, /<section class="scene emotion-screen" id="worlds">/);
  assert.match(html, /<section class="scene emotion-screen" id="projection">/);
  assert.match(html, /<section class="scene emotion-screen" id="lexicon">/);
  assert.match(html, /\.scene\.emotion-screen \{[^}]*min-height:\s*calc\(100svh - 60px\)/s);
  assert.match(html, /@media \(max-width: 820px\) \{[\s\S]*?\.scene\.emotion-screen \{[^}]*min-height:\s*auto/s);
});

test("projection puts copy and poets above one shared ground before the scatter chart", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  assert.match(html, /class="projection-hero">\s*<div class="projection-copy">[\s\S]*?id="poetStage"/);
  assert.match(html, /\.projection-hero::after \{[^}]*image\/emotions\/projection\/地面\.png/s);
  assert.match(html, /\.projection-hero \{[^}]*grid-template-columns:/s);
  assert.match(html, /#scatterChart \{ width: 100%; height: clamp\(300px, 38vh, 390px\); \}/);
});
