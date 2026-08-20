/* 诗风侠影 · 全站共享运行时：章回导航、落款印章、tooltip、幕尾钩子 */
(function () {
  "use strict";

  var CHAPTERS = [
    { id: "xu",  char: "序", name: "何谓侠",   file: "index.html" },
    { id: "shi", char: "时", name: "侠从何来", file: "xiayi-scroll.html" },
    { id: "di",  char: "地", name: "侠行何处", file: "interactive.html" },
    { id: "ren", char: "人", name: "侠者何人", file: "poets.html" },
    { id: "xin", char: "心", name: "侠心何似", file: "emotions.html" },
    { id: "cun", char: "存", name: "侠韵长存", file: "keyword-river.html" }
  ];

  var FONT_LINK_ID = "xia-fonts";

  function ensureFonts() {
    if (document.getElementById(FONT_LINK_ID)) return;
    var link = document.createElement("link");
    link.id = FONT_LINK_ID;
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=EB+Garamond:ital@0;1&family=Ma+Shan+Zheng&family=Noto+Sans+SC:wght@300;400;500&family=Noto+Serif+SC:wght@400;500;600&display=swap";
    document.head.appendChild(link);
  }

  function buildNav(current) {
    var nav = document.createElement("nav");
    nav.className = "site-nav";
    nav.setAttribute("aria-label", "章回导航");

    var brand = document.createElement("a");
    brand.className = "brand";
    brand.href = "index.html";
    brand.setAttribute("aria-label", "返回序章");
    brand.innerHTML = '<img class="brand-logo" src="image/prologue-logo.svg" alt="诗风侠影" />';
    nav.appendChild(brand);

    var chapters = document.createElement("div");
    chapters.className = "chapters";
    CHAPTERS.forEach(function (ch) {
      var el = document.createElement("a");
      el.className = "chapter";
      el.href = ch.file;
      if (ch.id === current) el.setAttribute("aria-current", "page");
      el.innerHTML = '<span class="char">' + ch.char + '</span>' +
                     '<span class="fullname">' + ch.name + '</span>';
      chapters.appendChild(el);
    });
    nav.appendChild(chapters);
    document.body.prepend(nav);
  }

  function buildSeal(char) {
    if (!char) return;
    var seal = document.createElement("div");
    seal.className = "seal page-seal";
    seal.textContent = char;
    seal.setAttribute("aria-hidden", "true");
    document.body.appendChild(seal);
  }

  /* 幕尾钩子：<div class="act-hook" data-hook-line="…" data-hook-next="poets.html" data-hook-label="侠者何人 →"></div> */
  function buildHooks() {
    document.querySelectorAll(".act-hook[data-hook-line]").forEach(function (el) {
      var line = document.createElement("span");
      line.className = "hook-line";
      line.textContent = el.dataset.hookLine;
      var link = document.createElement("a");
      link.className = "hook-link";
      link.href = el.dataset.hookNext;
      link.textContent = el.dataset.hookLabel;
      el.appendChild(line);
      el.appendChild(link);
    });
  }

  /* 共享 tooltip：Tip.show(html, x, y) / Tip.hide() */
  var tipEl = null;
  var Tip = {
    show: function (html, x, y) {
      if (!tipEl) {
        tipEl = document.createElement("div");
        tipEl.className = "viz-tip";
        document.body.appendChild(tipEl);
      }
      tipEl.innerHTML = html;
      tipEl.style.opacity = "1";
      var w = tipEl.offsetWidth, h = tipEl.offsetHeight;
      var left = Math.min(x + 14, window.innerWidth - w - 12);
      var top = Math.min(y + 14, window.innerHeight - h - 12);
      tipEl.style.left = left + "px";
      tipEl.style.top = top + "px";
    },
    hide: function () {
      if (tipEl) tipEl.style.opacity = "0";
    }
  };

  /* 简易 CSV 解析（项目 CSV 字段不含逗号/引号转义） */
  function parseCSV(text) {
    var lines = text.trim().split(/\r?\n/);
    var headers = lines[0].replace(/^﻿/, "").split(",");
    return lines.slice(1).filter(function (l) { return l.trim(); }).map(function (line) {
      var cols = line.split(",");
      var obj = {};
      headers.forEach(function (h, i) { obj[h] = cols[i]; });
      return obj;
    });
  }

  function loadCSV(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + " 加载失败");
      return r.text();
    }).then(parseCSV);
  }

  window.XIA = {
    chapters: CHAPTERS,
    tip: Tip,
    loadCSV: loadCSV,
    parseCSV: parseCSV
  };

  document.addEventListener("DOMContentLoaded", function () {
    ensureFonts();
    var chapter = document.body.dataset.chapter || "";
    if (!document.body.dataset.noNav) buildNav(chapter);
    buildSeal(document.body.dataset.seal);
    buildHooks();
  });
}());
