/**
 * ui.js — UI component renderers, training console, and interactive panels.
 * GridSight India.
 */

import { ENERGY_SOURCES, REGION_DATA, FORECAST_2025, FORECAST_2026, MONTHS_SHORT } from "./data.js";

// ── Energy sources grid ───────────────────────────────────────────────────
export function renderSourcesGrid() {
  const grid = document.getElementById("sourcesGrid");
  if (!grid) return;

  grid.innerHTML = ENERGY_SOURCES.map(s => {
    const shareNum = parseInt(s.share);
    return `
      <div class="source-card">
        <div class="source-icon">${s.icon}</div>
        <div class="source-name">${s.name}</div>
        <div class="source-share" style="color:${s.color}">${s.share}</div>
        <div class="source-delta">${s.delta}</div>
        <div class="source-bar-wrap">
          <div class="source-bar" style="width:${shareNum}%;background:${s.barColor}"></div>
        </div>
      </div>
    `;
  }).join("");
}

// ── Forecast sidebar cards ────────────────────────────────────────────────
export function renderForecastSidebar(year = 2025) {
  const sidebar = document.getElementById("forecastSidebar");
  if (!sidebar) return;

  const data = year === 2025 ? FORECAST_2025 : FORECAST_2026;
  const peakIdx = data.indexOf(Math.max(...data));
  const lowIdx  = data.indexOf(Math.min(...data));

  // Show 4 notable months
  const notable = [0, peakIdx, lowIdx, 11].filter((v, i, a) => a.indexOf(v) === i).slice(0, 4);

  sidebar.innerHTML = notable.map(i => {
    const val = data[i];
    const low  = Math.round(val * 0.94);
    const high = Math.round(val * 1.06);
    const badge = i === peakIdx ? "🔺 Peak" : i === lowIdx ? "🔻 Trough" : "";
    return `
      <div class="sidebar-card">
        ${badge ? `<div style="font-family:var(--font-mono);font-size:9px;color:var(--yellow);margin-bottom:6px;letter-spacing:.1em">${badge}</div>` : ""}
        <div class="sidebar-month">${MONTHS_SHORT[i]} ${year}</div>
        <div class="sidebar-val">${(val / 1000).toFixed(1)} GW</div>
        <div class="sidebar-range">${(low/1000).toFixed(1)}–${(high/1000).toFixed(1)} GW range</div>
      </div>
    `;
  }).join("");
}

// ── Region detail panel ───────────────────────────────────────────────────
export function renderRegionDetail(regionName) {
  const panel = document.getElementById("regionDetail");
  if (!panel) return;

  const d = REGION_DATA[regionName];
  if (!d) return;

  const f25 = d.forecast2025;
  const peak = Math.max(...f25);
  const avg  = Math.round(f25.reduce((a, b) => a + b, 0) / f25.length);

  panel.innerHTML = `
    <div style="margin-bottom:16px">
      <div style="font-family:var(--font-mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--yellow);margin-bottom:8px">${regionName} Region</div>
      <div style="font-family:var(--font-head);font-size:32px;font-weight:800">${d.capacity}</div>
      <div style="font-family:var(--font-mono);font-size:12px;color:var(--green);margin-top:4px">${d.growth}</div>
    </div>
    <div style="font-family:var(--font-mono);font-size:11px;color:var(--muted);margin-bottom:16px;line-height:1.7">
      <div style="margin-bottom:6px">📍 ${d.states}</div>
      <div>💡 ${d.highlight}</div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div style="background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:12px">
        <div style="font-family:var(--font-mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">2025 Peak</div>
        <div style="font-family:var(--font-head);font-size:20px;font-weight:700;color:var(--yellow)">${peak} GW</div>
      </div>
      <div style="background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:12px">
        <div style="font-family:var(--font-mono);font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">2025 Avg</div>
        <div style="font-family:var(--font-head);font-size:20px;font-weight:700;color:var(--teal)">${avg} GW</div>
      </div>
    </div>
  `;
}

// ── Region map selection ──────────────────────────────────────────────────
export function selectRegion(name) {
  // Remove active from all
  document.querySelectorAll(".map-region").forEach(el => el.classList.remove("active"));
  const target = document.getElementById(`r${name.replace("northeast","NE")}`);
  if (target) target.classList.add("active");
  renderRegionDetail(name);
}

// ── Training simulation ───────────────────────────────────────────────────
export function runTraining() {
  const btn      = document.getElementById("trainBtn");
  const fill     = document.getElementById("progressFill");
  const pctEl    = document.getElementById("progPct");
  const log      = document.getElementById("trainLog");
  const r2El     = document.getElementById("r2val");
  const rmseEl   = document.getElementById("rmseval");
  const mapeEl   = document.getElementById("mapeval");

  if (!btn) return;
  btn.disabled = true;
  btn.textContent = "⏳ Training…";

  const logLines = [
    ["[INIT] Loading CEA dataset (2015–2024)…", "log-ok"],
    ["[DATA] 120 monthly samples loaded", ""],
    ["[FEAT] Generating Fourier terms (k=2)…", ""],
    ["[FEAT] Trend, Temperature, GDP features added", "log-ok"],
    ["[SPLIT] Train: 96 samples | Test: 24 samples", ""],
    ["[OPT] Gradient descent — lr=1e-7, 2000 iters", ""],
    ["[ITER 500]  Loss: 1.842e+09", ""],
    ["[ITER 1000] Loss: 8.341e+08", "log-ok"],
    ["[ITER 1500] Loss: 4.122e+08", ""],
    ["[ITER 2000] Loss: 2.011e+08  ✓ converged", "log-ok"],
    ["[EVAL] Computing metrics on held-out test set…", ""],
    ["[METRIC] R²   = 0.9682", "log-ok"],
    ["[METRIC] RMSE = 4,312 MW", ""],
    ["[METRIC] MAPE = 3.18%", ""],
    ["[CV] 5-fold cross-val R²: 0.964 ± 0.008", "log-ok"],
    ["[SAVE] Model serialised → models/model.pkl", "log-ok"],
    ["[DONE] Training complete ✓", "log-ok"],
  ];

  let step = 0;
  const totalMs = 3200;
  const interval = totalMs / logLines.length;

  log.innerHTML = `<span class="log-warn">[GRIDSIGHT] Starting training pipeline…</span>\n`;

  const timer = setInterval(() => {
    const pct = Math.round(((step + 1) / logLines.length) * 100);
    fill.style.width = pct + "%";
    pctEl.textContent = pct + "%";

    const [text, cls] = logLines[step];
    const span = cls ? `<span class="${cls}">${text}</span>` : text;
    log.innerHTML += span + "\n";
    log.scrollTop = log.scrollHeight;

    step++;
    if (step >= logLines.length) {
      clearInterval(timer);
      r2El.textContent   = "0.968";
      rmseEl.textContent = "4,312";
      mapeEl.textContent = "3.18%";
      btn.disabled   = false;
      btn.textContent = "▶ Retrain Model";
    }
  }, interval);
}

// ── Live demand ticker ────────────────────────────────────────────────────
export function startLiveTicker() {
  const el = document.getElementById("liveDemand");
  if (!el) return;

  let base = 187420;
  setInterval(() => {
    base += Math.round((Math.random() - 0.5) * 400);
    el.textContent = base.toLocaleString("en-IN") + " MW";
  }, 3000);
}
