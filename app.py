import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'

st.set_page_config(page_title='FORESIGHT | Demand & Inventory Intelligence', layout='wide')
st.title('FORESIGHT — Demand & Inventory Intelligence')
st.caption('NorthBay Living | SKU-level forecasting, stockout/overstock risk and planning decisions')

@st.cache_data
def load():
    fc=pd.read_csv(OUT/'forecast_8_weeks.csv',parse_dates=['WeekStart'])
    risk=pd.read_csv(OUT/'risk_scores.csv',parse_dates=['Snapshot_Date'])
    bt=pd.read_csv(OUT/'backtest_summary.csv')
    return fc,risk,bt

fc,risk,bt=load()

c1,c2,c3,c4=st.columns(4)
c1.metric('SKUs forecast', risk.SKU.nunique())
c2.metric('8-week forecast units', f"{fc.Forecast_Units.sum():,.0f}")
c3.metric('Revenue at risk', f"₹{risk.Revenue_at_Risk.sum():,.0f}")
c4.metric('Capital locked', f"₹{risk.Capital_Locked.sum():,.0f}")

st.subheader('Planning view')
cat=st.selectbox('Category', ['All']+sorted(risk.Category.dropna().unique().tolist()))
view=risk if cat=='All' else risk[risk.Category==cat]
st.dataframe(view[['SKU','Product_Name','Category','Forecast_8W','Current_Stock','On_Order','Risk_Level','Decision','Revenue_at_Risk','Capital_Locked']].sort_values(['Risk_Level','Revenue_at_Risk'],ascending=[True,False]), use_container_width=True)

st.subheader('Risk decision grid')
fig=px.scatter(view, x='Lead_Time_Demand', y='Current_Stock', size='Revenue_at_Risk', color='Decision', hover_name='SKU', hover_data=['Product_Name','Forecast_8W','Lead_Time_Days'])
st.plotly_chart(fig,use_container_width=True)

st.subheader('SKU forecast')
selected=st.selectbox('SKU', sorted(view.SKU.unique()))
h=fc[fc.SKU==selected].copy()
hist=pd.read_csv(ROOT/'outputs/weekly_model_data.csv',parse_dates=['WeekStart'])
hist=hist[hist.SKU==selected].tail(20)
actual=hist[['WeekStart','Units_Sold']].rename(columns={'Units_Sold':'Value'}); actual['Series']='Actual'
pred=h[['WeekStart','Forecast_Units']].rename(columns={'Forecast_Units':'Value'}); pred['Series']='Forecast'
chart=pd.concat([actual,pred])
st.plotly_chart(px.line(chart,x='WeekStart',y='Value',color='Series',markers=True),use_container_width=True)

st.subheader('Model validation')
st.dataframe(bt, use_container_width=True)
st.info('The project brief requires rolling-origin backtesting and comparison with a seasonal-naive baseline. This dashboard reports those validation results rather than a single random train/test split.')
