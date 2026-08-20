const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const ROOT = path.resolve(__dirname, "..");
const PAGE = path.join(ROOT, "xiayi-scroll.html");

const READING_ASSETS = [
  {
    file: "image/shi-reading/peak-ka-yuan.png",
    alt: "开元时期河面最宽处的长安建筑配图"
  },
  {
    file: "image/shi-reading/divide-755.png",
    alt: "755 年安史之乱分水岭配图"
  },
  {
    file: "image/shi-reading/stars-in-heaven.png",
    alt: "无年诗作散于天汉的星辰配图"
  }
];

test("time reading cards expose the three supplied illustrations", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  for (const asset of READING_ASSETS) {
    assert.ok(fs.existsSync(path.join(ROOT, asset.file)), `missing supplied asset: ${asset.file}`);
    assert.match(html, new RegExp(`src="${asset.file}"`));
    assert.match(html, new RegExp(`alt="${asset.alt}"`));
  }

  assert.equal((html.match(/class="reading-figure"/g) || []).length, 3);
});

test("time reading illustrations retain their intrinsic aspect ratio", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /\.reading-figure__image\s*\{[^}]*height:\s*auto;/s);
  assert.match(html, /\.reading-figure__image\s*\{[^}]*object-fit:\s*contain;/s);
});

test("time reading illustrations sit above their colored dividers", () => {
  const html = fs.readFileSync(PAGE, "utf8");
  const cards = [...html.matchAll(/<article class="r-block [^"]+">([\s\S]*?)<\/article>/g)];

  assert.equal(cards.length, 3);
  for (const [, card] of cards) {
    assert.match(card, /<figure class="reading-figure">[\s\S]*?<\/figure>\s*<div class="reading-copy">/);
  }

  assert.match(html, /\.reading-copy\s*\{[^}]*border-top:\s*2px solid var\(--ink\);/s);
});
