"""
app.py — Flask web server for GridSight Energy Forecasting.

Routes:
    GET  /                  → index page
    GET  /result            → result page (GET with query params, for demo)
    POST /predict           → single-point prediction (JSON or form)
    GET  /api/forecast      → 24-month forecast JSON
    GET  /api/residuals     → actual vs predicted JSON
    POST /api/train         → trigger model re-training
    GET  /api/health        → health check
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Always resolve config relative to the project root (one level above app/)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from src.utils import load_config, get_logger

logger = get_logger(__name__)
config = load_config(os.path.join(_PROJECT_ROOT, "config", "config.yaml"))

app = Flask(__name__,
            template_folder=os.path.join(_PROJECT_ROOT, "app", "templates"),
            static_folder=os.path.join(_PROJECT_ROOT, "app", "static"))


# ── Helpers ────────────────────────────────────────────────────────────────

def _run_with_root(fn, *args, **kwargs):
    """
    Call fn(*args, **kwargs) with CWD set to project root so all relative
    file paths inside pipeline functions resolve correctly.
    Does NOT auto-inject config — callers pass it explicitly.
    """
    prev = os.getcwd()
    try:
        os.chdir(_PROJECT_ROOT)
        return fn(*args, **kwargs)
    finally:
        os.chdir(prev)


def _ensure_model():
    """Train model if not yet persisted."""
    from pathlib import Path
    model_path = Path(os.path.join(_PROJECT_ROOT, config["paths"]["model_output"]))
    if not model_path.exists():
        logger.info("No model found — auto-training…")
        from src.train_model import train
        _run_with_root(train, config)


# ── Pages ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result")
def result():
    """
    Display prediction result page.
    Accepts query params: trend, temperature_index, gdp_index, month
    """
    _ensure_model()
    from src.predict import predict_single

    input_data = {
        "trend":             float(request.args.get("trend", 120)),
        "temperature_index": float(request.args.get("temperature_index", 0.65)),
        "gdp_index":         float(request.args.get("gdp_index", 185.0)),
        "month":             int(request.args.get("month", 6)),
    }
    prediction = _run_with_root(predict_single, input_data, config)
    return render_template("result.html",
                           prediction=prediction,
                           input_data=input_data)


# ── API ────────────────────────────────────────────────────────────────────

@app.route("/predict", methods=["POST"])
def predict():
    """Single-point prediction from form or JSON body."""
    _ensure_model()
    from src.predict import predict_single

    data = request.get_json(silent=True) or request.form.to_dict()
    try:
        result = _run_with_root(predict_single, data, config)
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        logger.exception("Prediction error")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/forecast")
def api_forecast():
    """Return 24-month ahead forecast as JSON."""
    _ensure_model()
    from src.predict import generate_forecast

    year_filter = request.args.get("year", type=int)
    try:
        forecast = _run_with_root(generate_forecast, config)
        if year_filter:
            forecast = [f for f in forecast if f["year"] == year_filter]
        return jsonify({"status": "ok", "forecast": forecast})
    except Exception as e:
        logger.exception("Forecast error")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/residuals")
def api_residuals():
    """Return actual vs predicted residuals for last 24 months."""
    _ensure_model()
    from src.predict import get_residuals

    try:
        residuals = _run_with_root(get_residuals, config)
        return jsonify({"status": "ok", "residuals": residuals})
    except Exception as e:
        logger.exception("Residuals error")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/train", methods=["POST"])
def api_train():
    """Trigger model re-training and return metrics."""
    from src.train_model import train

    try:
        metrics = _run_with_root(train, config)
        safe_metrics = {k: v for k, v in metrics.items() if k != "features"}
        return jsonify({"status": "ok", "metrics": safe_metrics})
    except Exception as e:
        logger.exception("Training error")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/health")
def health():
    from pathlib import Path
    model_exists = Path(os.path.join(_PROJECT_ROOT, config["paths"]["model_output"])).exists()
    return jsonify({
        "status": "ok",
        "model_trained": model_exists,
        "version": config["project"]["version"],
    })


# ── Entry ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    flask_cfg = config.get("flask", {})
    app.run(
        host=flask_cfg.get("host", "0.0.0.0"),
        port=flask_cfg.get("port", 5000),
        debug=flask_cfg.get("debug", True),
    )
