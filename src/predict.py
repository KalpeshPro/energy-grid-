"""
predict.py — Inference and future demand forecasting.

Loads the trained model artefact and generates predictions for:
  - A single input row (via Flask form)
  - A full 24-month ahead forecast horizon
"""

import numpy as np
import pandas as pd
from pathlib import Path

from src.utils import get_logger, load_config, date_range_monthly, month_label
from src.train_model import load_model

logger = get_logger(__name__)


# ── Single prediction ──────────────────────────────────────────────────────

def predict_single(input_data: dict, config: dict | None = None) -> dict:
    """
    Predict peak demand for a single month given input features.

    Args:
        input_data: dict with keys matching feature_cols expected by model.
                    At minimum: trend, temperature_index, gdp_index
    Returns:
        dict with keys: predicted_mw, confidence_low, confidence_high, features_used
    """
    if config is None:
        config = load_config()

    artefact     = load_model(config)
    model        = artefact["model"]
    feature_cols = artefact["feature_cols"]
    ci           = config["forecast"].get("confidence_interval", 0.06)
    harmonics    = config["model"].get("fourier_harmonics", 2)

    t = float(input_data.get("trend", 0))

    # Seed lag/rolling features from training data tail so single predictions
    # are in the same scale as training (not zero-filled).
    processed_path = Path(config["paths"]["processed_data"])
    if processed_path.exists():
        from src.feature_engineering import build_features
        hist_df = pd.read_csv(processed_path)
        hist_df, _, _ = build_features(hist_df, config)
        target_col     = config.get("target", "peak_demand_mw")
        demand_history = list(hist_df[target_col].values)
    else:
        demand_history = []

    row = {col: 0.0 for col in feature_cols}
    row["trend"]             = t
    row["temperature_index"] = float(input_data.get("temperature_index", 0.5))
    row["gdp_index"]         = float(input_data.get("gdp_index", 150.0))

    for k in range(1, harmonics + 1):
        row[f"sin_{k}"] = float(np.sin(2 * np.pi * k * t / 12))
        row[f"cos_{k}"] = float(np.cos(2 * np.pi * k * t / 12))

    if "month" in feature_cols:
        row["month"] = int(input_data.get("month", 6))

    # Lag features from real history when available
    if demand_history:
        lag_map = {"demand_lag_1": -1, "demand_lag_3": -3, "demand_lag_12": -12}
        for col, offset in lag_map.items():
            if col in feature_cols and abs(offset) <= len(demand_history):
                row[col] = float(demand_history[offset])

        for col in feature_cols:
            if col.startswith("rolling_mean_"):
                w = int(col.split("_")[-1])
                if len(demand_history) >= w:
                    row[col] = float(np.mean(demand_history[-w:]))
            elif col.startswith("rolling_std_"):
                w = int(col.split("_")[-1])
                if len(demand_history) >= w:
                    row[col] = float(np.std(demand_history[-w:], ddof=0))

    X    = np.array([[row[c] for c in feature_cols]])
    pred = float(model.predict(X)[0])

    return {
        "predicted_mw":    round(pred),
        "confidence_low":  round(pred * (1 - ci)),
        "confidence_high": round(pred * (1 + ci)),
        "features_used":   feature_cols,
    }


# ── Forecast horizon ───────────────────────────────────────────────────────

def generate_forecast(config: dict | None = None,
                      base_trend_offset: int = 120) -> list[dict]:
    """
    Generate a 24-month ahead demand forecast (monthly).

    Warm-starts lag and rolling features from the last rows of the training
    data, then carries predictions forward iteratively so that lag/rolling
    values are real numbers — not zeros — throughout the horizon.

    Args:
        base_trend_offset: trend index offset (default 120 = after 10 years).

    Returns:
        List of dicts with keys:
            label, year, month, trend, predicted_mw,
            confidence_low, confidence_high
    """
    if config is None:
        config = load_config()

    artefact     = load_model(config)
    model        = artefact["model"]
    feature_cols = artefact["feature_cols"]
    harmonics    = config["model"].get("fourier_harmonics", 2)
    ci           = config["forecast"].get("confidence_interval", 0.06)
    horizon      = config["forecast"].get("horizon_months", 24)
    target_col   = config.get("target", "peak_demand_mw")

    # ── Warm-start: seed lag/rolling from actual training history ─────────────
    from src.feature_engineering import build_features
    processed_path = Path(config["paths"]["processed_data"])
    hist_df = pd.read_csv(processed_path)
    hist_df, _, _ = build_features(hist_df, config)

    # Keep enough history to fill lag_12 + rolling_6 lookback
    max_lookback   = 18
    demand_history = list(hist_df[target_col].values[-max_lookback:])

    # GDP proxy — continue smoothly from last training value
    gdp_base = 100 * (1 + 0.065 / 12) ** base_trend_offset

    results = []
    for i in range(horizon):
        t         = base_trend_offset + i
        month_num = (t % 12) + 1
        year      = 2025 + (t - base_trend_offset) // 12

        temp = 0.5 + 0.35 * np.sin(2 * np.pi * (t - 2) / 12)

        row = {col: 0.0 for col in feature_cols}
        row["trend"]             = t
        row["temperature_index"] = round(float(np.clip(temp, 0, 1)), 4)
        row["gdp_index"]         = round(gdp_base * (1 + 0.065 / 12) ** i, 2)

        for k in range(1, harmonics + 1):
            row[f"sin_{k}"] = float(np.sin(2 * np.pi * k * t / 12))
            row[f"cos_{k}"] = float(np.cos(2 * np.pi * k * t / 12))

        if "month" in feature_cols:
            row["month"] = month_num

        # ── Lag features from warm-started rolling history ────────────────────
        lag_map = {"demand_lag_1": -1, "demand_lag_3": -3, "demand_lag_12": -12}
        for col, offset in lag_map.items():
            if col in feature_cols and abs(offset) <= len(demand_history):
                row[col] = float(demand_history[offset])

        for col in feature_cols:
            if col.startswith("rolling_mean_"):
                w = int(col.split("_")[-1])
                if len(demand_history) >= w:
                    row[col] = float(np.mean(demand_history[-w:]))
            elif col.startswith("rolling_std_"):
                w = int(col.split("_")[-1])
                if len(demand_history) >= w:
                    row[col] = float(np.std(demand_history[-w:], ddof=0))

        X    = np.array([[row[c] for c in feature_cols]])
        pred = float(model.predict(X)[0])

        # Append prediction to history so next iteration's lags are correct
        demand_history.append(pred)

        results.append({
            "label":           month_label(year, month_num),
            "year":            year,
            "month":           month_num,
            "trend":           t,
            "predicted_mw":    round(pred),
            "confidence_low":  round(pred * (1 - ci)),
            "confidence_high": round(pred * (1 + ci)),
        })

    logger.info("Generated %d-month forecast", horizon)
    return results


# ── Residuals for model diagnostics ───────────────────────────────────────

def get_residuals(config: dict | None = None,
                  n_months: int = 24) -> list[dict]:
    """
    Return actual vs predicted for the last n_months of training data.
    Used by the model diagnostics chart.
    """
    if config is None:
        config = load_config()

    from src.feature_engineering import build_features

    processed_path = Path(config["paths"]["processed_data"])
    df = pd.read_csv(processed_path)
    df, feature_cols, _ = build_features(df, config)

    artefact = load_model(config)
    model    = artefact["model"]
    target   = config.get("target", "peak_demand_mw")

    X      = df[feature_cols].values
    y      = df[target].values
    y_pred = model.predict(X)

    tail_df     = df.tail(n_months).copy()
    tail_pred   = y_pred[-n_months:]
    tail_actual = y[-n_months:]

    results = []
    for i, (_, row) in enumerate(tail_df.iterrows()):
        results.append({
            "label":     month_label(int(row.get("year", 2024)),
                                     int(row.get("month", 1))),
            "actual":    round(float(tail_actual[i])),
            "predicted": round(float(tail_pred[i])),
            "residual":  round(float(tail_actual[i]) - round(float(tail_pred[i]))),
        })
    return results


if __name__ == "__main__":
    forecast = generate_forecast()
    for f in forecast[:6]:
        print(f)
