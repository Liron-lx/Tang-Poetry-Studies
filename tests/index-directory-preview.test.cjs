const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const html = fs.readFileSync(path.resolve(__dirname, "..", "index.html"), "utf8");

test("directory entries provide an illustration, copy, and data preview for every chapter", () => {
  const expected = [
    ["时", "image/prologue-directory/时.png"],
    ["地", "image/prologue-directory/地.png"],
    ["人", "image/prologue-directory/人.png"],
    ["心", "image/prologue-directory/心.png"],
    ["存", "image/prologue-directory/存.png"],
  ];

  for (const [chapter, illustration] of expected) {
    const item = new RegExp(
      `<a class="scene-directory-item"[^>]*>[\\s\\S]*?<span class="t-char">${chapter}</span>[\\s\\S]*?class="directory-preview"[\\s\\S]*?src="${illustration}"[\\s\\S]*?class="t-data"[\\s\\S]*?class="t-desc"[\\s\\S]*?</a>`
    );
    assert.match(html, item);
  }
});

test("directory previews support desktop hover and mobile tap expansion", () => {
  assert.match(html, /\.scene-directory-item:hover \.directory-preview/);
  assert.match(html, /\.scene-directory-item\.is-expanded \.directory-preview/);
  assert.match(html, /directoryItems\.forEach/);
  assert.match(html, /item\.classList\.add\('is-expanded'\)/);
});

test("foreground data positions avoid the central road", () => {
  assert.match(html, /\.scene-data-90 \{ left: calc\(100vw \* \.64\);/);
  assert.match(html, /\.scene-data-56 \{ left: calc\(100vw \* \.635\);/);
  assert.match(html, /\.scene-data-76 \{ left: calc\(100vw \* \.74\);/);
});
