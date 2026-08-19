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
