"""
feature_engineering.py — Feature creation for energy demand forecasting.

Produces Fourier seasonality terms, trend index, and normalised
versions of all input features ready for model training.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from src.utils import get_logger, load_config

logger = get_logger(__name__)


# ── Core feature builders ──────────────────────────────────────────────────

def add_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Add a zero-based integer trend column."""
    df = df.copy()
    df["trend"] = np.arange(len(df))
    return df


def add_fourier_features(df: pd.DataFrame,
                          harmonics: int = 2,
                          period: int = 12) -> pd.DataFrame:
    """
    Add Fourier sin/cos terms for seasonality modelling.

    For each harmonic k in 1..harmonics, produces:
        sin_k  =  sin(2π·k·trend / period)
        cos_k  =  cos(2π·k·trend / period)
    """
    df = df.copy()
    t = df["trend"].values
    for k in range(1, harmonics + 1):
        df[f"sin_{k}"] = np.sin(2 * np.pi * k * t / period)
        df[f"cos_{k}"] = np.cos(2 * np.pi * k * t / period)
    logger.info("Added %d Fourier harmonic pair(s)", harmonics)
    return df


def add_datetime_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract month and year from the date column."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["year"]  = df["date"].dt.year
    return df


def add_lag_features(df: pd.DataFrame,
                      target_col: str = "peak_demand_mw",
                      lags: list[int] | None = None) -> pd.DataFrame:
    """Add lagged demand values (default: 1, 3, 12 months)."""
    if lags is None:
        lags = [1, 3, 12]
    df = df.copy()
    for lag in lags:
        df[f"demand_lag_{lag}"] = df[target_col].shift(lag)
    logger.info("Added lag features: %s", lags)
    return df


def add_rolling_features(df: pd.DataFrame,
                          target_col: str = "peak_demand_mw",
                          windows: list[int] | None = None) -> pd.DataFrame:
    """Add rolling mean and std features."""
    if windows is None:
        windows = [3, 6]
    df = df.copy()
    for w in windows:
        df[f"rolling_mean_{w}"] = df[target_col].rolling(w, min_periods=1).mean()
        df[f"rolling_std_{w}"]  = df[target_col].rolling(w, min_periods=1).std().fillna(0)
    logger.info("Added rolling features for windows: %s", windows)
    return df


def scale_features(df: pd.DataFrame,
                   feature_cols: list[str]) -> tuple[pd.DataFrame, MinMaxScaler]:
    """
    MinMax-scale the given feature columns.
    Returns (scaled_df, fitted_scaler).
    """
    scaler = MinMaxScaler()
    df = df.copy()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    logger.info("Scaled %d feature columns", len(feature_cols))
    return df, scaler


# ── Full pipeline ──────────────────────────────────────────────────────────

def build_features(df: pd.DataFrame,
                   config: dict | None = None,
                   scale: bool = False) -> tuple[pd.DataFrame, list[str], MinMaxScaler | None]:
    """
    Full feature engineering pipeline.

    Steps:
      1. Add trend index
      2. Add Fourier seasonality terms
      3. Add datetime helpers (month, year)
      4. Add lag features
      5. Add rolling statistics
      6. (Optional) Scale features

    Returns:
        feature_df   — DataFrame with all features + target
        feature_cols — list of feature column names used for modelling
        scaler       — fitted MinMaxScaler (or None if scale=False)
    """
    if config is None:
        config = load_config()

    harmonics = config["model"].get("fourier_harmonics", 2)

    df = add_trend(df)
    df = add_fourier_features(df, harmonics=harmonics)
    df = add_datetime_features(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)

    # Drop rows with NaN introduced by lags
    df = df.dropna().reset_index(drop=True)

    # Build feature list matching config + engineered columns
    base_features   = config.get("features", ["trend", "sin_1", "cos_1",
                                               "temperature_index", "gdp_index"])
    fourier_extras  = [f"sin_{k}" for k in range(1, harmonics + 1)] + \
                      [f"cos_{k}" for k in range(1, harmonics + 1)]
    lag_cols        = [c for c in df.columns if c.startswith("demand_lag_")]
    rolling_cols    = [c for c in df.columns if c.startswith("rolling_")]
    extra_cols      = ["month"]

    feature_cols = list(dict.fromkeys(
        base_features + fourier_extras + lag_cols + rolling_cols + extra_cols
    ))
    # Keep only cols that exist in df
    feature_cols = [c for c in feature_cols if c in df.columns]

    scaler = None
    if scale:
        df, scaler = scale_features(df, feature_cols)

    logger.info("Feature engineering complete. Features: %s", feature_cols)
    return df, feature_cols, scaler


if __name__ == "__main__":
    from src.data_preprocessing import run_preprocessing
    clean_df = run_preprocessing()
    feat_df, cols, _ = build_features(clean_df)
    print(feat_df[cols].head())
    print("Feature columns:", cols)
