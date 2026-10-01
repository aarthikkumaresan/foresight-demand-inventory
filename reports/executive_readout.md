# Executive Readout — Project FORESIGHT

## 1. Decision summary
FORESIGHT converts NorthBay Living's sales and inventory extracts into an 8-week demand forecast and transparent stocking-risk actions.

## 2. What the current run says
- Forecast population: 50 SKUs with complete sales/master history.
- Reorder now: 5 SKUs.
- Markdown / clear: 7 SKUs.
- Healthy: 38 SKUs.
- Estimated revenue at risk: ₹2,775,781.
- Estimated capital locked: ₹9,334,000.

## 3. Forecast accuracy
Rolling-origin 8-week backtesting gives model WAPE of 10.58% versus 11.15% for the seasonal-naive baseline, an improvement of 5.17%.

## 4. Recommended operating actions
1. Review the reorder list first and validate supplier/lead-time assumptions before ordering.
2. Review markdown/clear candidates with the merchandising team.
3. Keep healthy SKUs under monitoring rather than changing stock policy automatically.
4. Refresh the pipeline whenever new extracts arrive.

## 5. Important limitations
- 150 inventory-only SKUs have no matching sales/master history and are excluded from the modelled population.
- The inventory snapshot is monthly, so risk is indicative rather than real-time.
- Promotion effects for the future horizon are assumed neutral when future promotion schedules are not supplied.
- The system does not place purchase orders; human review remains required.
