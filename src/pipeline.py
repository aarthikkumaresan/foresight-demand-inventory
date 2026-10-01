from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)

def build_dataset():
    sales = pd.read_csv(DATA/'sales_daily.csv', parse_dates=['Date'])
    sku = pd.read_csv(DATA/'sku_master.csv', parse_dates=['Launch_Date'])
    inv = pd.read_csv(DATA/'inventory_snapshots.csv', parse_dates=['Snapshot_Date'])
    cal = pd.read_csv(DATA/'calendar.csv', parse_dates=['date'])

    # Clean types and labels.
    sales.columns = [c.strip() for c in sales.columns]
    sku.columns = [c.strip() for c in sku.columns]
    inv.columns = [c.strip() for c in inv.columns]
    cal.columns = [c.strip() for c in cal.columns]

    # Remove exact duplicates; none are expected in the supplied data.
    sales = sales.drop_duplicates()
    sku = sku.drop_duplicates(subset=['SKU'])
    inv = inv.drop_duplicates(subset=['Snapshot_Date','SKU'])
    cal = cal.drop_duplicates(subset=['date'])

    # Calendar fields.
    cal['WeekStart'] = cal['date'] - pd.to_timedelta(cal['date'].dt.weekday, unit='D')
    cal['promotion_event_flag'] = cal['promotion_event'].notna().astype(int)
    weekly_cal = cal.groupby('WeekStart').agg(
        month=('month','first'), season=('season','first'),
        is_holiday=('is_holiday','max'), promotion_event_flag=('promotion_event_flag','max')
    ).reset_index()

    # Daily sales enriched with SKU + calendar dimensions.
    sales = sales.merge(sku[['SKU','Product_Name','Category','Subcategory','Cost_Price','Selling_Price']], on='SKU', how='left')
    sales = sales.merge(cal[['date','week','month','season','is_holiday','promotion_event']], left_on='Date', right_on='date', how='left')
    sales['WeekStart'] = sales['Date'] - pd.to_timedelta(sales['Date'].dt.weekday, unit='D')

    # Weekly modelling table: complete grid for the 50 SKUs with sales history.
    weeks = pd.date_range(sales['WeekStart'].min(), sales['WeekStart'].max(), freq='W-MON')
    skus = sorted(sales['SKU'].dropna().unique())
    grid = pd.MultiIndex.from_product([weeks, skus], names=['WeekStart','SKU']).to_frame(index=False)
    weekly_sales = sales.groupby(['WeekStart','SKU'], as_index=False).agg(
        Units_Sold=('Units_Sold','sum'), Revenue=('Revenue','sum'), Promotion=('Promotion','max')
    )
    weekly = grid.merge(weekly_sales, on=['WeekStart','SKU'], how='left')
    weekly['Units_Sold'] = weekly['Units_Sold'].fillna(0)
    weekly['Revenue'] = weekly['Revenue'].fillna(0)
    weekly['Promotion'] = weekly['Promotion'].fillna(0)
    weekly = weekly.merge(sku[['SKU','Product_Name','Category','Subcategory','Cost_Price','Selling_Price']], on='SKU', how='left')
    weekly = weekly.merge(weekly_cal, on='WeekStart', how='left')
    weekly = weekly.sort_values(['SKU','WeekStart'])

    # Data-quality summary.
    dq = {
        'sales_rows': len(sales), 'sales_skus': sales.SKU.nunique(),
        'inventory_rows': len(inv), 'inventory_skus': inv.SKU.nunique(),
        'sku_master_rows': len(sku), 'calendar_rows': len(cal),
        'sales_duplicate_sku_days': int(sales.duplicated(['Date','SKU']).sum()),
        'inventory_duplicate_snapshots': int(inv.duplicated(['Snapshot_Date','SKU']).sum()),
        'inventory_skus_not_in_master': int(len(set(inv.SKU)-set(sku.SKU))),
        'sales_skus_not_in_master': int(len(set(sales.SKU)-set(sku.SKU))),
        'sales_missing_values': int(sales.isna().sum().sum()),
        'inventory_missing_values': int(inv.isna().sum().sum()),
    }
    pd.DataFrame([dq]).to_csv(OUT/'data_quality_summary.csv', index=False)
    weekly.to_csv(OUT/'weekly_model_data.csv', index=False)
    sales.to_csv(OUT/'sales_enriched.csv', index=False)
    return sales, sku, inv, cal, weekly, dq

if __name__ == '__main__':
    _,_,_,_,weekly,dq = build_dataset()
    print('Pipeline complete:', weekly.shape)
    print(dq)
