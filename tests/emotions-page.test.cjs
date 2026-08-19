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
  assert.match(html, /prefers-reduced-motion/);
});

test("projection filters from figures and resets from blank chart space", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.doesNotMatch(html, /id="poetFilter"/);
  assert.match(html, /function setCurrentPoet\(name\)/);
  assert.match(html, /classList\.toggle\('is-muted'/);
  assert.match(html, /scatterChart\.addEventListener\('click'/);
});
