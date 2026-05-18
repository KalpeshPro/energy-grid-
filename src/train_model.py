"""
train_model.py — Model training, evaluation, and serialisation.

Trains a scikit-learn LinearRegression (or any sklearn estimator)
on the engineered feature set and saves the artefact to models/model.pkl.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score

from src.utils import get_logger, load_config, ensure_dir, rmse, mape, r2_score_manual
from src.data_preprocessing import run_preprocessing
from src.feature_engineering import build_features

logger = get_logger(__name__)


# ── Training ───────────────────────────────────────────────────────────────

def train(config: dict | None = None) -> dict:
    """
    Full training pipeline.

    1. Load / generate processed data
    2. Build features
    3. Train / test split
    4. Fit LinearRegression
    5. Evaluate (R², RMSE, MAPE, cross-val)
    6. Persist model to disk

    Returns a metrics dict.
    """
    if config is None:
        config = load_config()

    # ── Data ──
    processed_path = Path(config["paths"]["processed_data"])
    if processed_path.exists():
        logger.info("Loading processed data from %s", processed_path)
        df = pd.read_csv(processed_path)
    else:
        logger.info("Processed data not found — running preprocessing…")
        df = run_preprocessing(config)

    # ── Features ──
    df, feature_cols, _ = build_features(df, config)
    target_col = config.get("target", "peak_demand_mw")

    X = df[feature_cols].values
    y = df[target_col].values

    # ── Split ──
    test_size   = config["model"].get("test_size", 0.2)
    random_state = config["model"].get("random_state", 42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, shuffle=False  # time-series: no shuffle
    )
    logger.info("Train size: %d | Test size: %d", len(X_train), len(X_test))

    # ── Fit ──
    model = LinearRegression()
    model.fit(X_train, y_train)
    logger.info("Model trained: %s", model)

    # ── Evaluate on test set ──
    y_pred_test  = model.predict(X_test)
    y_pred_train = model.predict(X_train)

    metrics = {
        "r2_train": round(r2_score_manual(y_train, y_pred_train), 4),
        "r2_test":  round(r2_score_manual(y_test,  y_pred_test),  4),
        "rmse_test": round(rmse(y_test, y_pred_test), 1),
        "mape_test": round(mape(y_test, y_pred_test), 2),
        "n_train": len(X_train),
        "n_test":  len(X_test),
        "features": feature_cols,
    }

    # ── Cross-validation ──
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="r2")
    metrics["cv_r2_mean"] = round(cv_scores.mean(), 4)
    metrics["cv_r2_std"]  = round(cv_scores.std(),  4)

    logger.info(
        "Metrics → R² train: %.4f | R² test: %.4f | RMSE: %.1f | MAPE: %.2f%%",
        metrics["r2_train"], metrics["r2_test"],
        metrics["rmse_test"], metrics["mape_test"],
    )
    logger.info(
        "CV R² (5-fold): %.4f ± %.4f",
        metrics["cv_r2_mean"], metrics["cv_r2_std"],
    )

    # ── Persist ──
    model_path = Path(config["paths"]["model_output"])
    ensure_dir(model_path.parent)

    artefact = {
        "model": model,
        "feature_cols": feature_cols,
        "target_col": target_col,
        "metrics": metrics,
        "config": config,
    }
    joblib.dump(artefact, model_path)
    logger.info("Model saved → %s", model_path)

    return metrics


# ── Loader helper ──────────────────────────────────────────────────────────

def load_model(config: dict | None = None) -> dict:
    """Load the persisted model artefact dict from disk."""
    if config is None:
        config = load_config()
    model_path = Path(config["paths"]["model_output"])
    if not model_path.exists():
        raise FileNotFoundError(
            f"No trained model found at {model_path}. Run train() first."
        )
    return joblib.load(model_path)


if __name__ == "__main__":
    metrics = train()
    print("\n=== Training Complete ===")
    for k, v in metrics.items():
        if k != "features":
            print(f"  {k}: {v}")
    print(f"  features ({len(metrics['features'])}): {metrics['features']}")
