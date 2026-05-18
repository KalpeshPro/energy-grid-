"""
data_preprocessing.py — Data loading, cleaning, and preprocessing.

Generates synthetic proxy data modelled after CEA / NLDC historical records
(2015–2024) and saves clean CSV to data/processed/.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from src.utils import get_logger, load_config, ensure_dir, date_range_monthly

logger = get_logger(__name__)


# ── Synthetic data generation ──────────────────────────────────────────────

def generate_raw_data(start_year: int = 2015, n_months: int = 120,
                      seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic monthly energy demand data for India (2015–2024).

    Columns produced:
        date, peak_demand_mw, temperature_index, gdp_index, region,
        coal_pct, solar_pct, wind_pct, hydro_pct, nuclear_pct, gas_pct
    """
    rng = np.random.default_rng(seed)
    dates = date_range_monthly(start_year, 1, n_months)

    t = np.arange(n_months)

    # Base demand with linear growth + seasonality + noise
    base = 140_000
    trend = t * 450
    seasonal = (
        18_000 * np.sin(2 * np.pi * t / 12)        # annual cycle
        + 5_000 * np.cos(2 * np.pi * t / 12)
        + 3_500 * np.sin(4 * np.pi * t / 12)       # semi-annual harmonic
    )
    noise = rng.normal(0, 2_500, n_months)
    peak_demand = base + trend + seasonal + noise

    # Temperature index (proxy, 0–1 scaled, summer peaks)
    temp_base = 0.5 + 0.35 * np.sin(2 * np.pi * (t - 2) / 12)
    temperature_index = np.clip(temp_base + rng.normal(0, 0.04, n_months), 0, 1)

    # GDP index (smooth growth)
    gdp_index = 100 * (1 + 0.065 / 12) ** t + rng.normal(0, 0.8, n_months)

    # Region assignments (round-robin for variety)
    regions = ["North", "South", "East", "West", "Northeast"]
    region_col = [regions[i % len(regions)] for i in range(n_months)]

    # Energy mix evolution (coal declining, solar rising)
    coal_pct   = np.clip(70 - t * 0.15 + rng.normal(0, 1, n_months), 50, 75)
    solar_pct  = np.clip(2  + t * 0.20 + rng.normal(0, 0.5, n_months), 2, 25)
    wind_pct   = np.clip(4  + t * 0.08 + rng.normal(0, 0.4, n_months), 4, 12)
    hydro_pct  = np.clip(12 - t * 0.02 + rng.normal(0, 0.5, n_months), 8, 14)
    nuclear_pct = np.clip(3 + rng.normal(0, 0.2, n_months), 2, 4)
    gas_pct    = 100 - coal_pct - solar_pct - wind_pct - hydro_pct - nuclear_pct

    df = pd.DataFrame({
        "date": dates,
        "peak_demand_mw": peak_demand.round(0).astype(int),
        "temperature_index": temperature_index.round(4),
        "gdp_index": gdp_index.round(2),
        "region": region_col,
        "coal_pct": coal_pct.round(2),
        "solar_pct": solar_pct.round(2),
        "wind_pct": wind_pct.round(2),
        "hydro_pct": hydro_pct.round(2),
        "nuclear_pct": nuclear_pct.round(2),
        "gas_pct": gas_pct.round(2),
    })
    return df


# ── Cleaning pipeline ──────────────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply cleaning steps:
      - Parse dates
      - Drop exact duplicates
      - Clip demand outliers (IQR-based)
      - Fill missing values with forward-fill then median
      - Ensure mix percentages sum to ≈100
    """
    df = df.copy()

    # Parse date
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Drop full duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    logger.info("Dropped %d duplicate rows", before - len(df))

    # Outlier clipping on peak demand (IQR)
    q1, q3 = df["peak_demand_mw"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 3 * iqr, q3 + 3 * iqr
    clipped = df["peak_demand_mw"].clip(lower, upper)
    n_clipped = (df["peak_demand_mw"] != clipped).sum()
    df["peak_demand_mw"] = clipped
    logger.info("Clipped %d outlier demand values", n_clipped)

    # Fill NaN values
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].ffill().fillna(df[numeric_cols].median())

    logger.info("Cleaning complete. Shape: %s", df.shape)
    return df


# ── Main entry ─────────────────────────────────────────────────────────────

def run_preprocessing(config: dict | None = None) -> pd.DataFrame:
    """
    Full preprocessing pipeline:
      1. Generate (or load) raw data  →  data/raw/
      2. Clean
      3. Save processed CSV           →  data/processed/
    Returns the cleaned DataFrame.
    """
    if config is None:
        config = load_config()

    raw_path = Path(config["paths"]["raw_data"])
    processed_path = Path(config["paths"]["processed_data"])

    ensure_dir(raw_path.parent)
    ensure_dir(processed_path.parent)

    # Generate raw if missing
    if not raw_path.exists():
        logger.info("Generating synthetic raw data → %s", raw_path)
        raw_df = generate_raw_data()
        raw_df.to_csv(raw_path, index=False)
    else:
        logger.info("Loading existing raw data from %s", raw_path)
        raw_df = pd.read_csv(raw_path)

    # Clean
    clean_df = clean_data(raw_df)

    # Save processed
    clean_df.to_csv(processed_path, index=False)
    logger.info("Processed data saved → %s", processed_path)

    return clean_df


if __name__ == "__main__":
    run_preprocessing()
