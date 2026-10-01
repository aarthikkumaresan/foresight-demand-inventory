from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; OUT=ROOT/'outputs'

def build_risk():
    fc=pd.read_csv(OUT/'forecast_8_weeks.csv',parse_dates=['WeekStart'])
    inv=pd.read_csv(DATA/'inventory_snapshots.csv',parse_dates=['Snapshot_Date'])
    sku=pd.read_csv(DATA/'sku_master.csv')
    latest=inv.sort_values('Snapshot_Date').groupby('SKU',as_index=False).tail(1)
    fc=fc.merge(sku[['SKU','Product_Name','Category','Subcategory','Cost_Price','Selling_Price']],on='SKU',how='left')
    # Use only inventory SKUs with matching sales/master history for transparent scoring.
    fc=fc.merge(latest[['SKU','Snapshot_Date','Current_Stock','On_Order','Lead_Time_Days','Safety_Stock','Reorder_Point','Inventory_Value']],on='SKU',how='left')
    # 8-week demand per SKU.
    agg=fc.groupby('SKU').agg(Forecast_8W=('Forecast_Units','sum'), Avg_Weekly_Forecast=('Forecast_Units','mean')).reset_index()
    risk=latest.merge(agg,on='SKU',how='inner')
    risk=risk.merge(sku[['SKU','Product_Name','Category','Subcategory','Cost_Price','Selling_Price']],on='SKU',how='left')
    # Lead-time demand approximated from weekly forecast and actual lead time.
    risk['Lead_Time_Demand']=risk['Avg_Weekly_Forecast']*(risk['Lead_Time_Days']/7)
    risk['Projected_Lead_Time_Balance']=risk['Current_Stock']+risk['On_Order']-risk['Lead_Time_Demand']
    risk['Projected_8W_Balance']=risk['Current_Stock']+risk['On_Order']-risk['Forecast_8W']
    risk['Stockout_Risk']=risk['Projected_Lead_Time_Balance'] < risk['Safety_Stock']
    # Overstock if current + on order materially exceeds 8-week forecast plus safety stock.
    risk['Overstock_Risk']=(risk['Current_Stock']+risk['On_Order']) > (risk['Forecast_8W']+risk['Safety_Stock'])*1.25
    def action(r):
        so,ov=bool(r.Stockout_Risk),bool(r.Overstock_Risk)
        if so and not ov: return 'Reorder now'
        if ov and not so: return 'Markdown / clear'
        if so and ov: return 'Watch / volatile'
        return 'Healthy'
    risk['Decision']=risk.apply(action,axis=1)
    risk['Revenue_at_Risk']=np.where(risk.Stockout_Risk, np.maximum(0,-risk.Projected_Lead_Time_Balance)*risk.Selling_Price,0)
    risk['Capital_Locked']=np.where(risk.Overstock_Risk, np.maximum(0,risk.Current_Stock+risk.On_Order-risk.Forecast_8W-risk.Safety_Stock)*risk.Cost_Price,0)
    risk['Risk_Level']=np.select([risk.Decision.eq('Reorder now'),risk.Decision.eq('Markdown / clear'),risk.Decision.eq('Watch / volatile')],['High stockout','High overstock','High mixed'],default='Low')
    cols=['SKU','Product_Name','Category','Subcategory','Snapshot_Date','Current_Stock','On_Order','Lead_Time_Days','Safety_Stock','Reorder_Point','Forecast_8W','Lead_Time_Demand','Projected_Lead_Time_Balance','Projected_8W_Balance','Stockout_Risk','Overstock_Risk','Risk_Level','Decision','Revenue_at_Risk','Capital_Locked']
    risk[cols].to_csv(OUT/'risk_scores.csv',index=False)
    return risk
if __name__=='__main__':
    print(build_risk().Decision.value_counts())
