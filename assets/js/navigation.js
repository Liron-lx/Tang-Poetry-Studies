(function () {
  "use strict";

  function navigate(path) {
    if (typeof path === "string" && path.trim()) {
      window.location.assign(path);
    }
  }

  window.PoetryViz = window.PoetryViz || {};
  window.PoetryViz.navigate = navigate;

  document.querySelectorAll("[data-route]").forEach(function (element) {
    element.setAttribute("role", element.getAttribute("role") || "link");
    if (!element.hasAttribute("tabindex")) {
      element.setAttribute("tabindex", "0");
    }

    element.addEventListener("click", function () {
      navigate(element.dataset.route);
    });

    element.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        navigate(element.dataset.route);
      }
    });
  });
})();
