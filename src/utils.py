"""
utils.py — Shared helper functions for GridSight Energy Forecasting.
"""

import os
import yaml
import logging
import numpy as np
import pandas as pd
from pathlib import Path


# ── Logging ────────────────────────────────────────────────────────────────

def get_logger(name: str) -> logging.Logger:
    """Return a consistently formatted logger."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(name)


# ── Config ─────────────────────────────────────────────────────────────────

def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load YAML configuration file and return as dict."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ── Path helpers ───────────────────────────────────────────────────────────

def ensure_dir(path: str) -> None:
    """Create directory (and parents) if it does not exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def project_root() -> Path:
    """Return the project root directory (two levels above src/)."""
    return Path(__file__).resolve().parent.parent


# ── Metrics ────────────────────────────────────────────────────────────────

def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error (%)."""
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def r2_score_manual(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Coefficient of determination R²."""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot != 0 else 0.0


# ── Data helpers ───────────────────────────────────────────────────────────

def month_label(year: int, month: int) -> str:
    """Return a readable month label, e.g. 'Jan-2025'."""
    months = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]
    return f"{months[(month - 1) % 12]}-{year}"


def date_range_monthly(start_year: int, start_month: int,
                        n_months: int) -> pd.DatetimeIndex:
    """Generate a monthly DatetimeIndex of length n_months."""
    start = pd.Timestamp(year=start_year, month=start_month, day=1)
    return pd.date_range(start=start, periods=n_months, freq="MS")
