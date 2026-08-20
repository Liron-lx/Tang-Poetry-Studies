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

  /* Keep the splash hit area attached to the button inside the supplied
     1440 × 1024 reference image, even when object-fit: cover changes its
     rendered scale on wider or taller viewports. */
  var splashReferenceButton = {
    left: 0.433,
    top: 0.674,
    width: 0.134,
    height: 0.055
  };

  function positionSplashHotspot() {
    var stage = root.querySelector('[data-prologue-phase="splash"] .reference-stage');
    var image = stage && stage.querySelector("img");
    var button = document.getElementById("beginBtn");
    if (!stage || !image || !button || !image.naturalWidth || !image.naturalHeight) return;

    var stageWidth = stage.clientWidth;
    var stageHeight = stage.clientHeight;
    var objectFit = window.getComputedStyle(image).objectFit;
    var scaleX = stageWidth / image.naturalWidth;
    var scaleY = stageHeight / image.naturalHeight;
    var offsetX = 0;
    var offsetY = 0;

    if (objectFit === "cover") {
      var scale = Math.max(scaleX, scaleY);
      scaleX = scale;
      scaleY = scale;
      offsetX = (stageWidth - image.naturalWidth * scale) / 2;
    }

    button.style.left = (offsetX + splashReferenceButton.left * image.naturalWidth * scaleX) + "px";
    button.style.top = (offsetY + splashReferenceButton.top * image.naturalHeight * scaleY) + "px";
    button.style.width = (splashReferenceButton.width * image.naturalWidth * scaleX) + "px";
    button.style.height = (splashReferenceButton.height * image.naturalHeight * scaleY) + "px";
  }

  function render() {
    root.dataset.currentPhase = phase;
    document.body.dataset.prologuePhase = phase;
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
    if (phase === "unfurled") {
      window.scrollTo(0, 0);
      requestParallaxUpdate();
    }
  }

  Object.keys(buttonEvents).forEach(function (id) {
    var button = document.getElementById(id);
    if (!button) return;
    button.addEventListener("click", function () {
      advance(buttonEvents[id], button);
    });
  });

  var splashImage = root.querySelector('[data-prologue-phase="splash"] .reference-stage img');
  if (splashImage) {
    splashImage.addEventListener("load", positionSplashHotspot);
    positionSplashHotspot();
    window.addEventListener("resize", positionSplashHotspot);
  }

  var parallaxScene = root.querySelector("[data-scene-parallax]");
  var parallaxLayers = parallaxScene ? parallaxScene.querySelectorAll("[data-scene-layer]") : [];
  var parallaxFrame = 0;
  /* The supplied long-scroll reference is composed at the middle of the
     scene. Keep one shared alignment point so the layers can settle back to
     their design positions before continuing the parallax movement. */
  var sceneAlignmentRatio = 0.28;
  var reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");

  function updateParallax() {
    parallaxFrame = 0;
    if (!parallaxScene || !parallaxLayers.length || (reducedMotion && reducedMotion.matches)) {
      parallaxLayers.forEach(function (layer) {
        layer.style.transform = "translate3d(0, 0, 0)";
      });
      return;
    }

    var sceneTop = parallaxScene.getBoundingClientRect().top + window.scrollY;
    var distance = Math.max(0, window.scrollY - sceneTop);
    var alignmentDistance = parallaxScene.clientHeight * sceneAlignmentRatio;
    var signedDistance = distance - alignmentDistance;
    parallaxLayers.forEach(function (layer) {
      var depth = Number(layer.dataset.depth || 0);
      var offset = Math.max(-270, Math.min(270, signedDistance * depth));
      layer.style.transform = "translate3d(0, " + (-offset).toFixed(2) + "px, 0)";
    });
  }

  function requestParallaxUpdate() {
    if (parallaxFrame) return;
    parallaxFrame = window.requestAnimationFrame(updateParallax);
  }

  if (parallaxScene) {
    window.addEventListener("scroll", requestParallaxUpdate, { passive: true });
    window.addEventListener("resize", requestParallaxUpdate);
    updateParallax();
  }

  var directoryRows = root.querySelectorAll("[data-directory-preview-trigger]");
  var lockedDirectoryRow = null;

  function setDirectoryRow(row, value) {
    if (!row) return;
    row.classList.toggle("is-preview", value);
    row.setAttribute("aria-expanded", String(value));
  }

  function clearDirectoryRows() {
    directoryRows.forEach(function (row) {
      setDirectoryRow(row, false);
    });
  }

  function showDirectoryRow(row) {
    directoryRows.forEach(function (candidate) {
      setDirectoryRow(candidate, candidate === row);
    });
  }

  function hoverEnabled() {
    return !(window.matchMedia && window.matchMedia("(hover: none)").matches);
  }

  directoryRows.forEach(function (row) {
    row.addEventListener("mouseenter", function () {
      if (hoverEnabled() && !lockedDirectoryRow) showDirectoryRow(row);
    });
    row.addEventListener("mouseleave", function () {
      if (hoverEnabled() && !lockedDirectoryRow) clearDirectoryRows();
    });
    row.addEventListener("focus", function () {
      if (!lockedDirectoryRow) showDirectoryRow(row);
    });
    row.addEventListener("blur", function () {
      if (!lockedDirectoryRow) clearDirectoryRows();
    });
    row.addEventListener("click", function () {
      if (lockedDirectoryRow === row) {
        lockedDirectoryRow = null;
        clearDirectoryRows();
        return;
      }
      lockedDirectoryRow = row;
      showDirectoryRow(row);
    });
  });

  render();
}());
