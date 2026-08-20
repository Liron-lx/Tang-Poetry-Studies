const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const ROOT = path.resolve(__dirname, "..");
const PAGES = [
  "index.html",
  "xiayi-scroll.html",
  "interactive.html",
  "poets.html",
  "emotions.html",
  "keyword-river.html"
];

test("all formal pages load the shared navigation runtime", () => {
  for (const page of PAGES) {
    const html = fs.readFileSync(path.join(ROOT, page), "utf8");
    assert.match(html, /assets\/js\/site\.js/);
  }
});

test("the shared navigation uses the supplied xia logo and preserves inactive gray chapters", () => {
  const runtime = fs.readFileSync(path.join(ROOT, "assets/js/site.js"), "utf8");
  const css = fs.readFileSync(path.join(ROOT, "assets/css/common.css"), "utf8");

  assert.match(runtime, /class="brand-logo"[^>]+src="image\/prologue-logo\.svg"/);
  assert.match(css, /\.site-nav\s*\{[^}]*height:\s*60px;/s);
  assert.match(css, /\.site-nav \.brand-logo\s*\{[^}]*width:\s*48px;[^}]*height:\s*35px;/s);
  assert.match(css, /\.site-nav \.chapter\s*\{[^}]*color:\s*var\(--ink-2\);/s);
  assert.match(css, /\.site-nav \.chapter\[aria-current="page"\]\s*\{[^}]*color:\s*var\(--ink\);/s);
});

test("the prologue only controls navigation visibility, not chapter color", () => {
  const html = fs.readFileSync(path.join(ROOT, "index.html"), "utf8");

  assert.doesNotMatch(html, /\.site-nav a\s*\{\s*color:\s*transparent;/);
  assert.doesNotMatch(html, /\.site-nav a\s*\{\s*color:\s*var\(--ink\);/);
  assert.match(html, /body\.intro-started \.site-nav/);
});
