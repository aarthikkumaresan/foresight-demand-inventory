from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import pandas as pd

app = FastAPI(title='FORESIGHT Scoring Service', version='1.0')
OUT=Path(__file__).resolve().parent/'outputs'
risk=pd.read_csv(OUT/'risk_scores.csv')
forecast=pd.read_csv(OUT/'forecast_8_weeks.csv')

class SKURequest(BaseModel):
    sku: str

@app.get('/')
def root():
    return {'service':'FORESIGHT scoring service','status':'ok','supported_skus':int(risk.SKU.nunique())}

@app.get('/score/{sku}')
def score(sku: str):
    r=risk[risk.SKU==sku]
    if r.empty:
        raise HTTPException(status_code=404, detail='SKU not found in supported modelling set')
    row=r.iloc[0]
    f=forecast[forecast.SKU==sku].sort_values('WeekStart')
    return {
        'sku': sku,
        'product_name': row.Product_Name,
        'decision': row.Decision,
        'risk_level': row.Risk_Level,
        'forecast_8_week_units': round(float(row.Forecast_8W),2),
        'current_stock': int(row.Current_Stock),
        'on_order': int(row.On_Order),
        'lead_time_days': int(row.Lead_Time_Days),
        'revenue_at_risk': round(float(row.Revenue_at_Risk),2),
        'capital_locked': round(float(row.Capital_Locked),2),
        'weekly_forecast': [{'week':x.WeekStart,'units':round(float(x.Forecast_Units),2)} for x in f.itertuples()]
    }

@app.post('/score')
def score_post(req: SKURequest):
    return score(req.sku)
