(function () {
  "use strict";

  var root = document.querySelector("[data-prologue-root]");
  var stateApi = window.PoetryViz && window.PoetryViz.PrologueState;
  if (!root || !stateApi) return;

  var phase = "splash";
  var buttonEvents = {
    beginBtn: "BEGIN",
    openBookBtn: "OPEN_BOOK",
    prefaceBtn: "SHOW_PREFACE",
    unfurlBtn: "UNFURL"
  };

  function render() {
    root.dataset.currentPhase = phase;
    document.body.classList.toggle("is-splash", phase === "splash");
    document.body.classList.toggle("is-book", phase !== "splash");

    root.querySelectorAll("[data-prologue-phase]").forEach(function (section) {
      var active = section.dataset.prologuePhase === phase;
      section.hidden = !active;
      section.setAttribute("aria-hidden", String(!active));
    });
  }

  function advance(event, control) {
    var nextPhase = stateApi.next(phase, event);
    if (nextPhase === phase) return;
    phase = nextPhase;
    render();
    if (control && typeof control.focus === "function") {
      var activeControl = root.querySelector(
        '[data-prologue-phase="' + phase + '"] button'
      );
      if (activeControl) activeControl.focus({ preventScroll: true });
    }
    if (phase === "unfurled") window.scrollTo(0, 0);
  }

  Object.keys(buttonEvents).forEach(function (id) {
    var button = document.getElementById(id);
    if (!button) return;
    button.addEventListener("click", function () {
      advance(buttonEvents[id], button);
    });
  });

  render();
}());
