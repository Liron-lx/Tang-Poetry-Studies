const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const ROOT = path.resolve(__dirname, "..");
const PAGE = path.join(ROOT, "poets.html");

test("the people page introduces all five supplied poets in one white city-stage before the lifeline", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /class="poet-stage"/);
  assert.match(html, /\.poet-stage\s*\{[\s\S]*background:\s*#fff/);
  assert.match(html, /image\/poets\/stage-background\.png/);
  assert.equal((html.match(/class="poet-stage-figure(?:\s|\")/g) || []).length, 5);
  assert.match(html, /id="lifelineSvg"/);
});

test("the people page lets a visitor select one poet, return to the overview, and browse poem cards four at a time", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /id="poetOverview"/);
  assert.match(html, /id="poetDetail"/);
  assert.match(html, /class="poet-return"/);
  assert.match(html, /data-poet="骆宾王"/);
  assert.match(html, /classList\.toggle\('is-muted'/);
  assert.match(html, /function showPoetDetail\(name\)/);
  assert.match(html, /function showPoetOverview\(\)/);
  assert.match(html, /\.plaques\s*\{[\s\S]*overflow-x:\s*auto/);
  assert.match(html, /flex:\s*0 0 calc\(\(100% - 3rem\) \/ 4\)/);
});

test("each overview poet has an immediate detail route before the asynchronous poet data loads", () => {
  const html = fs.readFileSync(PAGE, "utf8");

  assert.match(html, /<a class="poet-stage-figure figure-luo" href="#poet=%E9%AA%86%E5%AE%BE%E7%8E%8B"/);
  assert.match(html, /<a class="poet-stage-figure figure-wang" href="#poet=%E7%8E%8B%E7%BB%B4"/);
  assert.match(html, /<a class="poet-stage-figure figure-li" href="#poet=%E6%9D%8E%E7%99%BD"/);
  assert.match(html, /<a class="poet-stage-figure figure-gao" href="#poet=%E9%AB%98%E9%80%82"/);
  assert.match(html, /<a class="poet-stage-figure figure-du" href="#poet=%E6%9D%9C%E7%94%AB"/);
});
