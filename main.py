"""
main.py — GridSight Energy Forecasting pipeline entry point.

Usage:
    python main.py                  # Run full pipeline
    python main.py --step preprocess
    python main.py --step features
    python main.py --step train
    python main.py --step predict
    python main.py --serve          # Launch Flask app
"""

import argparse
import sys
from src.utils import get_logger, load_config

logger = get_logger("main")


def run_pipeline(config: dict) -> None:
    """Execute the full end-to-end pipeline."""

    logger.info("═══ Step 1/3 — Data Preprocessing ═══")
    from src.data_preprocessing import run_preprocessing
    df = run_preprocessing(config)
    logger.info("Processed shape: %s", df.shape)

    logger.info("═══ Step 2/3 — Feature Engineering ═══")
    from src.feature_engineering import build_features
    feat_df, feature_cols, _ = build_features(df, config)
    logger.info("Feature columns (%d): %s", len(feature_cols), feature_cols)

    logger.info("═══ Step 3/3 — Model Training ═══")
    from src.train_model import train
    metrics = train(config)

    logger.info("══════════════════════════════════════")
    logger.info("Pipeline complete.")
    logger.info("  R² train : %.4f", metrics["r2_train"])
    logger.info("  R² test  : %.4f", metrics["r2_test"])
    logger.info("  RMSE     : %.1f MW", metrics["rmse_test"])
    logger.info("  MAPE     : %.2f%%", metrics["mape_test"])
    logger.info("  CV R²    : %.4f ± %.4f", metrics["cv_r2_mean"], metrics["cv_r2_std"])
    logger.info("══════════════════════════════════════")


def run_step(step: str, config: dict) -> None:
    """Run a single named pipeline step."""
    if step == "preprocess":
        from src.data_preprocessing import run_preprocessing
        run_preprocessing(config)

    elif step == "features":
        from src.data_preprocessing import run_preprocessing
        from src.feature_engineering import build_features
        df = run_preprocessing(config)
        feat_df, cols, _ = build_features(df, config)
        print(feat_df[cols].head())

    elif step == "train":
        from src.train_model import train
        metrics = train(config)
        for k, v in metrics.items():
            if k != "features":
                print(f"  {k}: {v}")

    elif step == "predict":
        from src.predict import generate_forecast
        forecast = generate_forecast(config)
        print(f"\n24-Month Forecast ({len(forecast)} months):\n")
        for f in forecast:
            bar_len = int((f["predicted_mw"] / 270_000) * 30)
            bar = "█" * bar_len
            print(f"  {f['label']:10s}  {f['predicted_mw']:>7,} MW  {bar}")

    else:
        logger.error("Unknown step: '%s'. Choose from: preprocess, features, train, predict", step)
        sys.exit(1)


def serve(config: dict) -> None:
    """Launch the Flask web application."""
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from app.app import app
    flask_cfg = config.get("flask", {})
    logger.info("Starting Flask server on http://%s:%s",
                flask_cfg.get("host","0.0.0.0"), flask_cfg.get("port", 5000))
    app.run(
        host=flask_cfg.get("host", "0.0.0.0"),
        port=flask_cfg.get("port", 5000),
        debug=flask_cfg.get("debug", True),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GridSight India — Energy Demand Forecasting Pipeline"
    )
    parser.add_argument(
        "--step",
        choices=["preprocess", "features", "train", "predict"],
        help="Run a single pipeline step instead of the full pipeline",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch the Flask web application",
    )
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to config YAML (default: config/config.yaml)",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if args.serve:
        serve(config)
    elif args.step:
        run_step(args.step, config)
    else:
        run_pipeline(config)


if __name__ == "__main__":
    main()
