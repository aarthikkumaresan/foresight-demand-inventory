from src.pipeline import build_dataset
from src.forecast import backtest, train_and_forecast
from src.risk import build_risk

if __name__=='__main__':
    sales,sku,inv,cal,weekly,dq=build_dataset()
    bt,summary=backtest(weekly)
    fc,model=train_and_forecast(weekly,8)
    risk=build_risk()
    print('\n=== BACKTEST ===')
    print(summary.to_string(index=False))
    print('\n=== RISK ACTIONS ===')
    print(risk.Decision.value_counts().to_string())
    print('\n=== BUSINESS IMPACT ===')
    print('Revenue at risk: Rs', round(risk.Revenue_at_Risk.sum(),2))
    print('Capital locked: Rs', round(risk.Capital_Locked.sum(),2))
    print('\nOutputs written to outputs/')
