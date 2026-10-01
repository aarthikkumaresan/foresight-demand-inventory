from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'outputs'
FEATURES = ['lag1','lag2','lag4','lag8','lag13','lag26','lag52','roll4','roll8','roll13','Promotion','is_holiday','promotion_event_flag','woy_sin','woy_cos']

def add_features(df):
    df = df.sort_values(['SKU','WeekStart']).copy()
    for lag in [1,2,4,8,13,26,52]:
        df[f'lag{lag}'] = df.groupby('SKU').Units_Sold.shift(lag)
    for win in [4,8,13]:
        df[f'roll{win}'] = df.groupby('SKU').Units_Sold.shift(1).rolling(win).mean().reset_index(level=0, drop=True)
    week = df.WeekStart.dt.isocalendar().week.astype(int)
    df['woy_sin'] = np.sin(2*np.pi*week/52)
    df['woy_cos'] = np.cos(2*np.pi*week/52)
    return df

def wape(actual, pred):
    denom = np.abs(actual).sum()
    return float(np.abs(actual-pred).sum()/denom) if denom else np.nan

def backtest(df):
    df = add_features(df)
    origins = pd.to_datetime(['2025-06-02','2025-08-04','2025-10-06'])
    all_rows=[]
    for origin in origins:
        train=df[df.WeekStart<origin].dropna(subset=FEATURES)
        test=df[(df.WeekStart>=origin)&(df.WeekStart<origin+pd.Timedelta(weeks=8))].copy()
        model=HistGradientBoostingRegressor(max_iter=300, learning_rate=.06, max_leaf_nodes=31, l2_regularization=1.0, random_state=42)
        model.fit(train[FEATURES], train.Units_Sold)
        test['Model_Forecast']=np.maximum(0, model.predict(test[FEATURES].fillna(0)))
        test['Seasonal_Naive']=test['lag52']
        test['Origin']=origin
        all_rows.append(test[['Origin','WeekStart','SKU','Units_Sold','Model_Forecast','Seasonal_Naive']])
    bt=pd.concat(all_rows, ignore_index=True)
    summary=pd.DataFrame({
        'Metric':['Model WAPE','Seasonal-naive WAPE','Improvement'],
        'Value':[wape(bt.Units_Sold,bt.Model_Forecast),wape(bt.Units_Sold,bt.Seasonal_Naive),1-wape(bt.Units_Sold,bt.Model_Forecast)/wape(bt.Units_Sold,bt.Seasonal_Naive)]
    })
    bt.to_csv(OUT/'backtest_predictions.csv',index=False)
    summary.to_csv(OUT/'backtest_summary.csv',index=False)
    return bt, summary

def train_and_forecast(df, horizon=8):
    df=add_features(df)
    train=df.dropna(subset=FEATURES)
    model=HistGradientBoostingRegressor(max_iter=400, learning_rate=.05, max_leaf_nodes=31, l2_regularization=1.0, random_state=42)
    model.fit(train[FEATURES], train.Units_Sold)
    history=df[['WeekStart','SKU','Units_Sold']].copy()
    last_week=df.WeekStart.max()
    future_weeks=pd.date_range(last_week+pd.Timedelta(weeks=1), periods=horizon, freq='W-MON')
    skus=sorted(df.SKU.unique())
    rows=[]
    for wk in future_weeks:
        for s in skus:
            sub=history[(history.SKU==s)&(history.WeekStart<wk)].sort_values('WeekStart')
            vals=sub.set_index('WeekStart').Units_Sold
            row={'WeekStart':wk,'SKU':s,'Promotion':0,'is_holiday':0,'promotion_event_flag':0}
            for lag in [1,2,4,8,13,26,52]:
                row[f'lag{lag}']=vals.get(wk-pd.Timedelta(weeks=lag), np.nan)
            prev=sub.Units_Sold
            for win in [4,8,13]: row[f'roll{win}']=prev.tail(win).mean()
            week=int(wk.isocalendar().week)
            row['woy_sin']=np.sin(2*np.pi*week/52); row['woy_cos']=np.cos(2*np.pi*week/52)
            pred=max(0,float(model.predict(pd.DataFrame([row])[FEATURES].fillna(0))[0]))
            rows.append({'WeekStart':wk,'SKU':s,'Forecast_Units':pred})
            history=pd.concat([history,pd.DataFrame([{'WeekStart':wk,'SKU':s,'Units_Sold':pred}])],ignore_index=True)
    fc=pd.DataFrame(rows)
    fc.to_csv(OUT/'forecast_8_weeks.csv',index=False)
    return fc, model

if __name__=='__main__':
    from pipeline import build_dataset
    *_,weekly,_=build_dataset()
    bt,summary=backtest(weekly)
    fc,_=train_and_forecast(weekly,8)
    print(summary.to_string(index=False))
    print('Forecast rows:',len(fc))
