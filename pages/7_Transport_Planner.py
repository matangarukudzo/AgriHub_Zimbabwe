import math
import pandas as pd
import plotly.express as px
import streamlit as st
from theme import apply_theme

apply_theme("Transport & Market Planner", "Find the market that pays most after transport costs.", "🚚")
st.caption("Distances and prices below are examples. Edit the table with your real markets (add rows with the + at the bottom).")

c1, c2, c3 = st.columns(3)
qty = c1.number_input("Quantity to sell (kg)", 100, 10_000_000, 8000, step=100)
cap = c2.number_input("Truck capacity (kg)", 500, 50000, 5000, step=500)
per_km = c3.number_input("Transport cost (USD per km)", 0.0, 20.0, 0.80, 0.05)
round_trip = st.checkbox("Count the return trip", True)

markets = pd.DataFrame({
    "Market": ["Local market", "Town A", "City B", "Processor C"],
    "Distance (km)": [15, 80, 250, 140],
    "Price (USD/kg)": [0.30, 0.34, 0.40, 0.37],
    "Fee (% of sales)": [0.0, 2.0, 3.0, 1.0],
    "Fixed fee (USD)": [0.0, 5.0, 20.0, 0.0],
})
ed = st.data_editor(markets, num_rows="dynamic", use_container_width=True).dropna(subset=["Market"]).fillna(0)
if ed.empty:
    st.stop()

trips = math.ceil(qty / cap)
ed = ed.copy()
ed["Transport (USD)"] = trips * ed["Distance (km)"] * (2 if round_trip else 1) * per_km
ed["Gross (USD)"] = qty * ed["Price (USD/kg)"]
ed["Fees (USD)"] = ed["Gross (USD)"] * ed["Fee (% of sales)"] / 100 + ed["Fixed fee (USD)"]
ed["Net (USD)"] = ed["Gross (USD)"] - ed["Transport (USD)"] - ed["Fees (USD)"]
ed["Net per kg"] = ed["Net (USD)"] / qty
ed = ed.sort_values("Net (USD)", ascending=False)

best, nearest = ed.iloc[0], ed.sort_values("Distance (km)").iloc[0]
st.success(f"Best option: **{best.Market}**, net ${best['Net (USD)']:,.0f} (${best['Net per kg']:.3f}/kg) using {trips} trip(s).")
if best.Market != nearest.Market:
    gain = best["Net (USD)"] - nearest["Net (USD)"]
    st.info(f"Compared with the nearest market ({nearest.Market}), you earn ${gain:,.0f} more by travelling further.")

st.dataframe(ed[["Market", "Distance (km)", "Gross (USD)", "Transport (USD)", "Fees (USD)", "Net (USD)", "Net per kg"]]
             .round(2), hide_index=True, use_container_width=True)
st.plotly_chart(px.bar(ed, x="Net (USD)", y="Market", orientation="h", color_discrete_sequence=["#ef6c00"])
                .update_layout(yaxis=dict(autorange="reversed")), use_container_width=True)
st.caption("Tip: if several farmers share one truck, split the transport cost to raise everyone's net price.")
