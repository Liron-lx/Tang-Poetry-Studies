const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const ROOT = path.resolve(__dirname, "..");
const PAGE = path.join(ROOT, "keyword-river.html");

test("the finale uses the supplied ink background and separates its copy from methods", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  assert.ok(fs.existsSync(path.join(ROOT, "image", "finale-background.png")));
  assert.match(html, /url\("image\/finale-background\.png"\)/);
  assert.match(html, /class="finale-copy"/);
  assert.match(html, /<section class="scene method-scene">/);
  assert.doesNotMatch(html, /class="f-seal"/);
});
