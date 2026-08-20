(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.PoetryViz = root.PoetryViz || {};
  root.PoetryViz.PrologueState = api;
}(typeof globalThis === "undefined" ? this : globalThis, function () {
  "use strict";

  var transitions = {
    splash: { BEGIN: "cover" },
    cover: { OPEN_BOOK: "poem" },
    poem: { SHOW_PREFACE: "preface" },
    preface: { UNFURL: "unfurled" },
    unfurled: {}
  };

  function next(phase, event) {
    return (transitions[phase] && transitions[phase][event]) || phase;
  }

  return { next: next };
}));
