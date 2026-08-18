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
