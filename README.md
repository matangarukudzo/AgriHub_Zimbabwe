# 🌾 AgriHub Zimbabwe

🔗 Live demo: [add your Streamlit link]

One platform covering the farming cycle for Zimbabwean smallholder farmers, cooperatives and agri-businesses.

| Stage | Tool | Decision it supports |
|---|---|---|
| Plan | Price Forecaster | When should I sell? (WFP prices, 3 models, confidence range, EN/Shona/Ndebele) |
| Plan | Planting Advisor | When do planting rains start and which crops suit my district? |
| Plan | Climate & Drought Risk | How often do dry seasons hit and how risky is my area? |
| Grow | Input Price Tracker | Which supplier has the cheapest seed and fertilizer? |
| Grow | Farm Profit Calculator | What is my break-even price and which crop pays best? |
| Harvest | Post-Harvest Loss Tracker | Where do I lose produce and are fixes worth it? |
| Sell | Marketplace | Who will buy my produce, and is my price fair? |
| Sell | Transport & Market Planner | Which market pays most after transport costs? |
| Finance | Loan Readiness Scorer | How ready am I for a loan and how do I improve? |

## Data
- Prices: WFP Zimbabwe food prices (HDX), see data/README.md
- Climate: Open-Meteo archive and forecast (free, no key); falls back to clearly-labelled simulated data offline
- Other tools use illustrative defaults that users replace with their own numbers

## Limitations
Marketplace and input prices are prototypes without a database (entries reset on restart). Planting and suitability results are guides to confirm with extension officers. The loan scorer is educational only.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

## Roadmap
Database (Supabase), WhatsApp/USSD access, Crop Disease Detector, Cooperative Manager, WhatsApp Price Bot.
