/**
 * data.js — Static data constants and synthetic data generators.
 * GridSight India Energy Forecasting Platform.
 */

// ── Historical demand (2015–2024) ─────────────────────────────────────────
export const HISTORICAL_DEMAND = [
  140200, 144800, 138600, 132400, 146200, 168400, 178600, 176200, 161400,
  150800, 139600, 145200, // 2015
  148600, 153200, 147400, 140200, 154800, 174200, 186400, 182200, 167800,
  156400, 144800, 150400, // 2016
  156200, 160800, 154200, 147600, 162400, 182400, 193200, 188400, 173200,
  161800, 149600, 156000, // 2017
  162400, 167600, 160800, 153600, 168800, 190400, 200400, 196000, 179800,
  168000, 155200, 162400, // 2018
  169000, 174200, 167400, 159800, 175600, 197800, 208200, 203400, 186600,
  174400, 161000, 168600, // 2019
  162400, 148200, 130600, 125800, 152800, 184200, 196000, 192600, 176800,
  166200, 153800, 160400, // 2020 (COVID dip)
  170200, 175600, 169800, 162400, 178600, 202400, 214200, 209600, 192600,
  180200, 167200, 174800, // 2021
  178400, 183800, 177200, 169800, 186800, 211200, 223800, 219000, 201400,
  188600, 175000, 182800, // 2022
  186600, 192200, 185400, 177400, 195200, 221200, 234600, 229400, 211200,
  197600, 183400, 191600, // 2023
  195200, 201200, 194200, 185800, 204000, 231400, 245200, 240200, 221400,
  207200, 192400, 200600, // 2024
];

export const MONTHS_SHORT = [
  "Jan","Feb","Mar","Apr","May","Jun",
  "Jul","Aug","Sep","Oct","Nov","Dec"
];
export const MONTHS_LONG = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December"
];

// ── 24-month forecast (2025–2026) ─────────────────────────────────────────
export const FORECAST_2025 = [
  204200, 210600, 203400, 194600, 213400, 242000, 256400, 251200, 231800,
  216600, 201200, 209800
];
export const FORECAST_2026 = [
  214000, 220800, 213200, 203800, 223800, 253800, 268800, 263200, 242800,
  227000, 210800, 220200
];
export const FORECAST_CI_PCT = 0.06; // ±6% confidence band

// ── YoY peak demand (GW) ──────────────────────────────────────────────────
export const YOY_DATA = {
  years:  [2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026],
  demand: [178.6,186.4,193.2,200.4,208.2,196.0,214.2,223.8,234.6,245.2,256.4,268.8],
};

// ── Energy sources ────────────────────────────────────────────────────────
export const ENERGY_SOURCES = [
  { name:"Coal",    icon:"🏭", share:"61%", delta:"▼ 3.1% from 2023", color:"#f59e0b", barColor:"#f59e0b" },
  { name:"Solar",   icon:"☀️", share:"14%", delta:"▲ 4.2% from 2023", color:"#fbbf24", barColor:"#fbbf24" },
  { name:"Wind",    icon:"💨", share:" 8%", delta:"▲ 1.4% from 2023", color:"#2dd4bf", barColor:"#2dd4bf" },
  { name:"Hydro",   icon:"💧", share:" 9%", delta:"▼ 0.8% from 2023", color:"#60a5fa", barColor:"#60a5fa" },
  { name:"Nuclear", icon:"⚛️", share:" 3%", delta:"= flat",           color:"#a78bfa", barColor:"#a78bfa" },
  { name:"Gas",     icon:"🔥", share:" 5%", delta:"▼ 1.7% from 2023", color:"#f97316", barColor:"#f97316" },
];

// Energy mix forecast 2025–2030
export const MIX_FORECAST = {
  years:   [2025, 2026, 2027, 2028, 2029, 2030],
  coal:    [  61,   57,   53,   49,   44,   40],
  solar:   [  14,   18,   22,   26,   31,   37],
  wind:    [   8,    9,   10,   11,   12,   13],
  hydro:   [   9,    9,    8,    8,    7,    6],
  nuclear: [   3,    3,    3,    3,    3,    3],
  gas:     [   5,    4,    4,    3,    3,    1],
};

// ── Regions ───────────────────────────────────────────────────────────────
export const REGION_DATA = {
  North: {
    capacity: "316 GW",
    growth: "+6.1% YoY",
    states: "UP, Delhi, Haryana, Punjab, HP, J&K, Uttarakhand",
    highlight: "Industrial corridors in UP driving demand surge",
    forecast2025: [72,75,71,68,76,87,93,91,84,78,72,75],
    forecast2026: [76,79,75,71,80,91,98,96,88,82,76,79],
  },
  South: {
    capacity: "292 GW",
    growth: "+4.8% YoY",
    states: "Tamil Nadu, Karnataka, AP, Telangana, Kerala",
    highlight: "Solar leader — TN & Karnataka spearhead renewable growth",
    forecast2025: [67,69,66,63,70,80,85,83,76,71,66,69],
    forecast2026: [70,72,69,66,73,84,89,87,80,74,69,72],
  },
  East: {
    capacity: "218 GW",
    growth: "+3.9% YoY",
    states: "West Bengal, Odisha, Jharkhand, Bihar, Assam",
    highlight: "Coal-belt transition; hydro resources underutilised",
    forecast2025: [50,52,50,47,52,59,63,62,57,53,49,51],
    forecast2026: [52,54,52,49,54,62,66,65,60,55,51,53],
  },
  West: {
    capacity: "304 GW",
    growth: "+5.4% YoY",
    states: "Maharashtra, Gujarat, Rajasthan, MP, Goa",
    highlight: "Gujarat leads India in wind; MH drives industrial load",
    forecast2025: [70,72,69,66,73,83,88,86,79,74,68,71],
    forecast2026: [73,76,72,69,77,87,92,90,83,77,72,75],
  },
  Northeast: {
    capacity: "73 GW",
    growth: "+5.2% YoY",
    states: "Meghalaya, Manipur, Tripura, Mizoram, Nagaland, Arunachal, Sikkim",
    highlight: "Hydro-rich region; untapped potential for pumped storage",
    forecast2025: [17,17,16,15,18,21,22,22,20,19,17,18],
    forecast2026: [18,18,17,16,19,22,23,23,21,20,18,19],
  },
};

// ── Chart colour palette ──────────────────────────────────────────────────
export const COLORS = {
  yellow:  "#f59e0b",
  teal:    "#2dd4bf",
  blue:    "#60a5fa",
  green:   "#4ade80",
  purple:  "#a78bfa",
  orange:  "#f97316",
  red:     "#f87171",
  muted:   "#374151",
  gridLine:"rgba(255,255,255,0.06)",
  textMuted:"#6b7280",
};
