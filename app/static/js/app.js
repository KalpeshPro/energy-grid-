/**
 * app.js — Application entry point.
 * Initialises all charts, UI components, cursor, and scroll animations.
 */

import { buildForecastChart, buildYoyChart, buildMixChart, buildRegionalChart, buildResidualChart } from "./charts.js";
import { renderSourcesGrid, renderForecastSidebar, renderRegionDetail, startLiveTicker } from "./ui.js";

// ── State ─────────────────────────────────────────────────────────────────
let forecastChart  = null;
let regionalChart  = null;
let currentFcYear  = 2025;

// ── Custom cursor ─────────────────────────────────────────────────────────
function initCursor() {
  const dot  = document.getElementById("cursor");
  const ring = document.getElementById("cursorRing");
  if (!dot || !ring) return;

  let mx = 0, my = 0, rx = 0, ry = 0;

  document.addEventListener("mousemove", e => {
    mx = e.clientX; my = e.clientY;
    dot.style.transform  = `translate(${mx - 4}px, ${my - 4}px)`;
  });

  (function animRing() {
    rx += (mx - rx) * 0.14;
    ry += (my - ry) * 0.14;
    ring.style.transform = `translate(${rx - 14}px, ${ry - 14}px)`;
    requestAnimationFrame(animRing);
  })();

  document.querySelectorAll("a, button, .map-region").forEach(el => {
    el.addEventListener("mouseenter", () => {
      ring.style.width  = "44px";
      ring.style.height = "44px";
    });
    el.addEventListener("mouseleave", () => {
      ring.style.width  = "28px";
      ring.style.height = "28px";
    });
  });
}

// ── Intersection observer for fade-up ────────────────────────────────────
function initScrollAnimations() {
  const els = document.querySelectorAll(".fade-up");
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.animationPlayState = "running";
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.12 });

  els.forEach(el => {
    el.style.animationPlayState = "paused";
    obs.observe(el);
  });
}

// ── Forecast year toggle ──────────────────────────────────────────────────
window.switchForecastYear = function(year, btn) {
  currentFcYear = year;
  document.querySelectorAll(".yr-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");

  if (forecastChart) {
    forecastChart.destroy();
  }
  forecastChart = buildForecastChart("forecastChart", year);
  renderForecastSidebar(year);
};

// ── Region select (called from inline onclick) ────────────────────────────
window.selectRegion = function(name) {
  document.querySelectorAll(".map-region").forEach(el => el.classList.remove("active"));
  // Find button by text content
  document.querySelectorAll(".map-region").forEach(el => {
    if (el.querySelector(".rname")?.textContent === name.toUpperCase() ||
        el.querySelector(".rname")?.textContent === "NE" && name === "Northeast") {
      el.classList.add("active");
    }
  });
  // Also handle via id
  const idMap = { North:"rNorth", South:"rSouth", East:"rEast", West:"rWest", Northeast:"rNE" };
  if (idMap[name]) document.getElementById(idMap[name])?.classList.add("active");
  renderRegionDetail(name);
};

// ── Training button (called from inline onclick) ──────────────────────────
window.runTraining = function() {
  import("./ui.js").then(m => m.runTraining());
};

// ── Init ──────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initCursor();
  initScrollAnimations();
  startLiveTicker();

  // Build all charts
  forecastChart = buildForecastChart("forecastChart", 2025);
  buildYoyChart("yoyChart");
  buildMixChart("mixChart");
  regionalChart = buildRegionalChart("regionalChart", 2025);
  buildResidualChart("residualChart");

  // Render UI components
  renderSourcesGrid();
  renderForecastSidebar(2025);
  renderRegionDetail("North");

  console.log("[GridSight] App initialised ✓");
});
