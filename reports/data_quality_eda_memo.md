# Data Quality & EDA Insight Memo

## Scope
This memo covers the four supplied extracts and the modelling-ready sales population.

## Data quality findings
- Sales: 36,550 rows; no duplicate SKU-date records were found.
- SKU master: 50 SKUs.
- Inventory: 4,800 rows and 200 unique SKUs; 150 inventory-only SKUs do not have matching sales/master records.
- Calendar: 731 daily rows.
- Missing calendar holiday/promotion-event values are expected because blank means no event.

## Business insights
- The sales extract contains 50 SKUs with two years of daily history, enabling weekly SKU-level forecasting.
- Top 5 SKUs by total units sold: SKU012, SKU045, SKU018, SKU049, SKU037.
- The largest category by total units is Home Decor (132,570 units).
- The current risk layer identifies 5 SKUs for reorder and 7 for markdown/clear.
- Estimated sales/revenue at risk is ₹2,775,781; estimated capital locked in overstock is ₹9,334,000 under the transparent rules used here.
- The model backtest WAPE is 10.58% versus 11.15% for the seasonal-naive baseline.

## Limitation
Inventory snapshots are monthly while sales are daily. The risk layer uses the latest available inventory snapshot and an 8-week forecast. This is a planning signal, not an automated purchase-order recommendation.
