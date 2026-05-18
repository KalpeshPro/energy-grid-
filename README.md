# ⚡ GridSight India — Energy Demand Forecasting

ML-powered monthly energy demand forecasting for India's national grid.
24-month ahead predictions, disaggregated by region and source, served via a Flask web application.

---

## 📁 Project Structure

```
energy-forecasting-project/
│
├── data/
│   ├── raw/                        # Original dataset (auto-generated if absent)
│   └── processed/                  # Cleaned & transformed dataset
│
├── notebooks/
│   ├── eda.ipynb                   # Exploratory Data Analysis
│   └── model_training.ipynb        # Model experiments & evaluation
│
├── src/
│   ├── __init__.py
│   ├── data_preprocessing.py       # Data generation, cleaning & preprocessing
│   ├── feature_engineering.py      # Fourier terms, lags, rolling stats
│   ├── train_model.py              # Model training, CV & serialisation
│   ├── predict.py                  # Single-point & horizon forecasting
│   └── utils.py                    # Logging, config, metrics helpers
│
├── models/
│   └── model.pkl                   # Trained model artefact (joblib)
│
├── app/
│   ├── app.py                      # Flask backend — routes & API
│   ├── static/
│   │   ├── css/style.css           # Full dark-industrial UI stylesheet
│   │   └── js/
│   │       ├── app.js              # Entry point (ES module)
│   │       ├── charts.js           # Chart.js builders
│   │       ├── ui.js               # UI renderers & training console
│   │       └── data.js             # Static data & constants
│   └── templates/
│       ├── index.html              # Main dashboard
│       └── result.html             # Prediction result page
│
├── config/
│   └── config.yaml                 # Paths, hyperparameters & Flask config
│
├── requirements.txt
├── main.py                         # Pipeline entry point
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1 — Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2 — Run the full ML pipeline

```bash
python main.py
```

This will:
- Generate synthetic proxy data → `data/raw/energy_data.csv`
- Clean & preprocess → `data/processed/energy_processed.csv`
- Engineer features (Fourier, lags, rolling stats)
- Train a Linear Regression model & evaluate
- Serialise → `models/model.pkl`

### 3 — Launch the web app

```bash
python main.py --serve
```

Open → **http://localhost:5000**

---

## 🔧 Individual Pipeline Steps

```bash
python main.py --step preprocess   # Data cleaning only
python main.py --step features     # Feature engineering (prints head)
python main.py --step train        # Train & print metrics
python main.py --step predict      # Print 24-month forecast to console
```

---

## 🌐 Flask API Endpoints

| Method | Route             | Description                              |
|--------|-------------------|------------------------------------------|
| GET    | `/`               | Main dashboard (index.html)              |
| GET    | `/result`         | Prediction result page                   |
| POST   | `/predict`        | Single-point prediction (JSON or form)   |
| GET    | `/api/forecast`   | 24-month forecast JSON                   |
| GET    | `/api/forecast?year=2025` | Filtered by year                |
| GET    | `/api/residuals`  | Actual vs predicted (last 24 months)     |
| POST   | `/api/train`      | Trigger model re-training                |
| GET    | `/api/health`     | Health check + model status              |

### Example — single prediction

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"trend": 125, "month": 6, "temperature_index": 0.82, "gdp_index": 192.4}'
```

```json
{
  "status": "ok",
  "result": {
    "predicted_mw": 231840,
    "confidence_low": 217929,
    "confidence_high": 245750,
    "features_used": ["trend", "sin_1", "cos_1", ...]
  }
}
```

---

## 🤖 ML Model

| Property         | Value                                      |
|------------------|--------------------------------------------|
| Algorithm        | Multiple Linear Regression (sklearn)       |
| Features         | Trend, Fourier sin/cos (k=2), Temperature, GDP, Lags (1,3,12), Rolling stats |
| Training data    | 2015–2024 · 120 months (synthetic proxy)   |
| Train/Test split | 80/20, time-ordered (no shuffle)           |
| Validation       | 5-fold cross-validation                    |
| Forecast horizon | 24 months ahead with ±6% confidence band   |
| R² (test)        | ~0.968                                     |
| MAPE             | ~3.2%                                      |
| RMSE             | ~4,300 MW                                  |
| Model artefact   | `models/model.pkl` (joblib)                |

---

## 📊 Data Sources (Illustrative)

Data is **synthetic/illustrative** for educational purposes, modelled after:

- **CEA** — Central Electricity Authority of India
- **NLDC** — National Load Dispatch Centre
- **IMD** — India Meteorological Department
- **MNRE** — Ministry of New and Renewable Energy

---

## 🔋 Key Features

| Section      | Description                                                   |
|--------------|---------------------------------------------------------------|
| Hero         | Live demand ticker (updates every 3 s), animated pulse rings  |
| Forecast     | 2025/2026 toggle, confidence intervals, sidebar cards         |
| Sources      | Coal, Solar, Wind, Hydro, Nuclear, Gas — mix evolution chart  |
| Regions      | Interactive North/South/East/West/NE breakdown                |
| Model        | Animated training console, live R²/RMSE/MAPE metrics          |
| Insights     | 6 data-driven energy insights                                 |

---

## 📦 Dependencies

```
flask          # Web framework
numpy          # Numerical computing
pandas         # Data manipulation
scikit-learn   # ML model + preprocessing
pyyaml         # Config loading
joblib         # Model serialisation
matplotlib     # (Notebooks) Plotting
seaborn        # (Notebooks) Statistical plots
jupyter        # Notebook environment
```

Frontend (loaded via CDN — no npm required):
- **Chart.js 4.4.1** — All charts
- **Google Fonts** — Syne, JetBrains Mono, Crimson Pro

---

*Built for India's energy transition · © 2025 GridSight India*
