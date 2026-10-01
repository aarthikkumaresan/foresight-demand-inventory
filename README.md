# Project FORESIGHT — Demand & Inventory Intelligence

**Client:** NorthBay Living (simulated)  
**Role:** Data Scientist & Analytics  
**Stack:** Python, pandas, scikit-learn, Streamlit, Plotly

## Business problem
NorthBay needs a weekly SKU-level demand forecast and an early-warning system for stockout and overstock risk. The system should turn sales, SKU, calendar and inventory extracts into clear reorder/markdown decisions.

## What is included
- Reproducible ingestion and cleaning pipeline
- Data-quality summary and EDA-ready enriched data
- Seasonal-naive baseline and rolling-origin backtest
- Leakage-safe gradient-boosting forecast
- 8-week SKU-level forecast
- Explainable stockout/overstock risk scoring
- Streamlit planning dashboard
- Executive/data-quality reports

## Data
The four supplied extracts are in `data/`:
- `sales_daily.csv`
- `sku_master.csv`
- `calendar.csv`
- `inventory_snapshots.csv`

Important data-quality finding: sales/master contain 50 SKUs, while inventory contains 200 SKUs. The 150 inventory-only SKUs do not have sales history/master records, so the modelling/risk layer uses the 50 SKUs supported by sales history and documents the mismatch rather than fabricating demand.

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py
streamlit run app.py
```

## Main outputs
- `outputs/data_quality_summary.csv`
- `outputs/weekly_model_data.csv`
- `outputs/backtest_predictions.csv`
- `outputs/backtest_summary.csv`
- `outputs/forecast_8_weeks.csv`
- `outputs/risk_scores.csv`

## Forecast methodology
The model uses lagged weekly demand, rolling statistics, promotion/calendar indicators and cyclical week-of-year features. Validation uses rolling-origin 8-week windows. The seasonal-naive baseline predicts the same week in the previous year (`lag52`).

The model should only be trusted when it beats the baseline honestly. If a rerun produces a worse model, retain/report the baseline rather than hiding the result.

## Risk methodology
- **Stockout risk:** forecast demand over the replenishment lead time exceeds available stock after considering on-order inventory and safety stock.
- **Overstock risk:** current + on-order inventory materially exceeds the 8-week forecast plus safety stock.
- **Decision:** Reorder now / Markdown-clear / Watch-volatile / Healthy.

## Submission checklist
1. Push the repository.
2. Deploy the Streamlit app.
3. Include the live dashboard URL.
4. Include the scoring/output URL if your mentor requires a separate service.
5. Submit README, EDA/data-quality memo, executive readout and 3–5 minute demo video.
6. Complete the cohort submission form.
