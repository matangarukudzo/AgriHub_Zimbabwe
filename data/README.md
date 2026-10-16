# Data

## Maize, sorghum, wheat (WFP via HDX)
1. Open https://data.humdata.org/dataset/wfp-food-prices-for-zimbabwe
2. Download the **Zimbabwe - Food Prices CSV**
3. Rename it to `wfp_food_prices_zwe.csv` and place it in this `data/` folder
4. Commit and push; the app picks it up automatically

The app uses the `usdprice` column, since Zimbabwe's local currency changed several times.
Commodity names (e.g. maize, sorghum, wheat flour) appear in the dropdown as they are in the file.

## Tobacco
WFP does not track tobacco. Use auction prices (e.g. Tobacco Industry and Marketing Board reports),
saved as a CSV with columns: `date,price,commodity` (commodity = `Tobacco`), and upload it in the app.
Alternatively, merge it into the WFP file using the same columns.

## Other sources
- FEWS NET Zimbabwe monthly staple food prices (HDX)
