/**
 * charts.js — Chart.js chart builders for GridSight.
 * Each function returns the Chart instance.
 */

import {
  HISTORICAL_DEMAND, FORECAST_2025, FORECAST_2026,
  MONTHS_SHORT, YOY_DATA, MIX_FORECAST, REGION_DATA,
  FORECAST_CI_PCT, COLORS
} from "./data.js";

// ── Shared defaults ───────────────────────────────────────────────────────
const FONT_MONO = "'JetBrains Mono', monospace";
const FONT_HEAD = "'Syne', sans-serif";

function baseScales(yLabel = "MW") {
  return {
    x: {
      ticks: { color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 } },
      grid:  { color: COLORS.gridLine },
    },
    y: {
      ticks: {
        color: COLORS.textMuted,
        font:  { family: FONT_MONO, size: 10 },
        callback: v => yLabel === "GW"
          ? v.toFixed(0) + " GW"
          : (v / 1000).toFixed(0) + "k",
      },
      grid: { color: COLORS.gridLine },
    },
  };
}

function basePlugin(title = "") {
  return {
    legend: { display: false },
    tooltip: {
      backgroundColor: "#111827",
      borderColor: COLORS.muted,
      borderWidth: 1,
      titleFont: { family: FONT_MONO, size: 11 },
      bodyFont:  { family: FONT_MONO, size: 11 },
      callbacks: {
        label: ctx => ` ${ctx.dataset.label}: ${
          ctx.raw >= 1000
            ? (ctx.raw / 1000).toFixed(1) + " GW"
            : ctx.raw
        }`,
      },
    },
  };
}

// ── 1. Monthly Forecast Chart ─────────────────────────────────────────────
export function buildForecastChart(canvasId, year = 2025) {
  const ctx = document.getElementById(canvasId)?.getContext("2d");
  if (!ctx) return null;

  const forecastData = year === 2025 ? FORECAST_2025 : FORECAST_2026;
  const labels = MONTHS_SHORT.map(m => `${m} ${year}`);

  // Historical reference (last 12 months of 2024)
  const hist = HISTORICAL_DEMAND.slice(-12);

  const ciHigh = forecastData.map(v => Math.round(v * (1 + FORECAST_CI_PCT)));
  const ciLow  = forecastData.map(v => Math.round(v * (1 - FORECAST_CI_PCT)));

  return new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Historical (2024)",
          data: hist,
          borderColor: COLORS.muted,
          borderWidth: 1.5,
          borderDash: [4, 4],
          pointRadius: 0,
          tension: 0.4,
        },
        {
          label: "CI High",
          data: ciHigh,
          borderColor: "transparent",
          backgroundColor: "rgba(245,158,11,0.08)",
          pointRadius: 0,
          fill: "+1",
          tension: 0.4,
        },
        {
          label: "Forecast",
          data: forecastData,
          borderColor: COLORS.yellow,
          borderWidth: 2.5,
          backgroundColor: "rgba(245,158,11,0.15)",
          pointBackgroundColor: COLORS.yellow,
          pointRadius: 4,
          tension: 0.4,
          fill: false,
        },
        {
          label: "CI Low",
          data: ciLow,
          borderColor: "transparent",
          backgroundColor: "rgba(245,158,11,0.08)",
          pointRadius: 0,
          fill: "-1",
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      animation: { duration: 600 },
      plugins: { ...basePlugin(), legend: { display: true, labels: {
        color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 },
        boxWidth: 14,
      }}},
      scales: baseScales(),
    },
  });
}

// ── 2. Year-Over-Year Chart ───────────────────────────────────────────────
export function buildYoyChart(canvasId) {
  const ctx = document.getElementById(canvasId)?.getContext("2d");
  if (!ctx) return null;

  const isPredicted = YOY_DATA.years.map(y => y >= 2025);
  const barColors = YOY_DATA.years.map(y =>
    y >= 2025 ? COLORS.yellow : "rgba(245,158,11,0.35)"
  );

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: YOY_DATA.years,
      datasets: [{
        label: "Peak Demand (GW)",
        data: YOY_DATA.demand,
        backgroundColor: barColors,
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      animation: { duration: 700 },
      plugins: basePlugin(),
      scales: {
        x: { ticks: { color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 } }, grid: { color: COLORS.gridLine } },
        y: {
          ticks: { color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 }, callback: v => v + " GW" },
          grid: { color: COLORS.gridLine },
          min: 150,
        },
      },
    },
  });
}

// ── 3. Energy Mix Forecast Chart ──────────────────────────────────────────
export function buildMixChart(canvasId) {
  const ctx = document.getElementById(canvasId)?.getContext("2d");
  if (!ctx) return null;

  const sources = [
    { label: "Coal",    data: MIX_FORECAST.coal,    color: COLORS.yellow  },
    { label: "Solar",   data: MIX_FORECAST.solar,   color: "#fbbf24"      },
    { label: "Wind",    data: MIX_FORECAST.wind,    color: COLORS.teal    },
    { label: "Hydro",   data: MIX_FORECAST.hydro,   color: COLORS.blue    },
    { label: "Nuclear", data: MIX_FORECAST.nuclear, color: COLORS.purple  },
    { label: "Gas",     data: MIX_FORECAST.gas,     color: COLORS.orange  },
  ];

  return new Chart(ctx, {
    type: "line",
    data: {
      labels: MIX_FORECAST.years,
      datasets: sources.map(s => ({
        label: s.label,
        data:  s.data,
        borderColor: s.color,
        backgroundColor: s.color + "22",
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: s.color,
        tension: 0.4,
        fill: false,
      })),
    },
    options: {
      responsive: true,
      plugins: { ...basePlugin(), legend: { display: true, labels: {
        color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 }, boxWidth: 12,
      }}},
      scales: {
        x: { ticks: { color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 } }, grid: { color: COLORS.gridLine } },
        y: {
          ticks: { color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 }, callback: v => v + "%" },
          grid: { color: COLORS.gridLine },
          min: 0, max: 75,
        },
      },
    },
  });
}

// ── 4. Regional Forecast Chart ────────────────────────────────────────────
export function buildRegionalChart(canvasId, year = 2025) {
  const ctx = document.getElementById(canvasId)?.getContext("2d");
  if (!ctx) return null;

  const key = `forecast${year}`;
  const regions = Object.keys(REGION_DATA);
  const regionColors = [COLORS.yellow, COLORS.teal, COLORS.blue, COLORS.green, COLORS.purple];
  const labels = MONTHS_SHORT.map(m => `${m}`);

  return new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: regions.map((r, i) => ({
        label: r,
        data: REGION_DATA[r][key] || [],
        borderColor: regionColors[i],
        backgroundColor: regionColors[i] + "15",
        borderWidth: 2,
        pointRadius: 3,
        tension: 0.4,
        fill: false,
      })),
    },
    options: {
      responsive: true,
      plugins: { ...basePlugin(), legend: { display: true, labels: {
        color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 }, boxWidth: 12,
      }}},
      scales: {
        x: { ticks: { color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 } }, grid: { color: COLORS.gridLine } },
        y: {
          ticks: { color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 }, callback: v => v + " GW" },
          grid: { color: COLORS.gridLine },
        },
      },
    },
  });
}

// ── 5. Residual / Actual vs Predicted ────────────────────────────────────
export function buildResidualChart(canvasId) {
  const ctx = document.getElementById(canvasId)?.getContext("2d");
  if (!ctx) return null;

  const hist   = HISTORICAL_DEMAND.slice(-24);
  const labels = [];
  for (let y = 2023; y <= 2024; y++) {
    MONTHS_SHORT.forEach(m => labels.push(`${m}-${y}`));
  }

  // Simulate predicted with small noise
  const predicted = hist.map(v => Math.round(v * (0.97 + Math.random() * 0.06)));

  return new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Actual",
          data: hist,
          borderColor: COLORS.blue,
          borderWidth: 2,
          pointRadius: 3,
          tension: 0.3,
          fill: false,
        },
        {
          label: "Predicted",
          data: predicted,
          borderColor: COLORS.yellow,
          borderWidth: 2,
          borderDash: [5, 3],
          pointRadius: 3,
          tension: 0.3,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { ...basePlugin(), legend: { display: true, labels: {
        color: COLORS.textMuted, font: { family: FONT_MONO, size: 10 }, boxWidth: 12,
      }}},
      scales: baseScales(),
    },
  });
}
