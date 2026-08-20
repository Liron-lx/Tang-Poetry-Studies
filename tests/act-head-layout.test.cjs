const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const ROOT = path.resolve(__dirname, "..");

test("the five chapter pages keep the same shared act-header baseline", () => {
  const pages = ["xiayi-scroll.html", "interactive.html", "poets.html", "emotions.html", "keyword-river.html"];
  for (const page of pages) {
    const html = fs.readFileSync(path.join(ROOT, page), "utf8");
    assert.match(html, /class="act-head"/);
  }

  const time = fs.readFileSync(path.join(ROOT, "xiayi-scroll.html"), "utf8");
  const place = fs.readFileSync(path.join(ROOT, "interactive.html"), "utf8");
  assert.doesNotMatch(time, /\.act-head\s*\{\s*min-width:\s*780px/);
  assert.match(place, /\.screen-map \.act-head\s*\{[^}]*width:\s*min\(1060px, calc\(100% - 3rem\)\)/s);
});
