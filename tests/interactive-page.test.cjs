const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const ROOT = path.resolve(__dirname, "..");
const PAGE = path.join(ROOT, "interactive.html");

test("the geography map has one callable renderer that draws the supplied data", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  const rendererCount = (html.match(/function drawMap\(tang, places\)/g) || []).length;

  assert.equal(rendererCount, 1, "a nested duplicate renderer leaves the map blank");
  assert.match(html, /drawMap\(tang, places\);/);
  assert.match(html, /peakNodes\.append\("path"\)/);
});

test("the geography page follows the map-to-frontier-to-changan visual narrative", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /id="frontierScene"/);
  assert.match(html, /id="changanScene"/);
  assert.match(html, /image\/act2-frontier-figma\.png/);
  assert.match(html, /image\/act2-changan-figma\.png/);
  assert.match(html, /href="#frontierScene"/);
  assert.doesNotMatch(html, /十峰榜/);
});

test("each geography narrative scene uses the supplied top-and-bottom white layout", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /\.place-stories\s*\{[\s\S]*background:\s*#fff/);
  assert.equal((html.match(/class="scene-top"/g) || []).length, 2);
  assert.equal((html.match(/class="scene-bottom"/g) || []).length, 2);
});
