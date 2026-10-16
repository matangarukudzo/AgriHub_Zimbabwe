import pandas as pd
import plotly.express as px
import streamlit as st
from theme import apply_theme

apply_theme("Farm Profit Calculator", "Find your break-even price and see which crop pays best.", "💰")

# Illustrative per-hectare defaults (USD). Replace with your own numbers.
D = {
    "Maize": dict(y=1500, seed=60, fert=180, labor=120, chem=40, other=50, price=0.36),
    "Sorghum": dict(y=1000, seed=20, fert=60, labor=90, chem=20, other=40, price=0.40),
    "Soya beans": dict(y=1200, seed=90, fert=70, labor=100, chem=60, other=40, price=0.55),
    "Groundnuts": dict(y=800, seed=120, fert=40, labor=130, chem=30, other=40, price=1.20),
    "Wheat": dict(y=4000, seed=120, fert=450, labor=200, chem=150, other=300, price=0.50),
}
st.caption("Default numbers are illustrative assumptions, not official statistics. Enter your own.")

crop = st.selectbox("Crop", list(D))
d = D[crop]
c1, c2, c3 = st.columns(3)
ha = c1.number_input("Area (hectares)", 0.1, 1000.0, 1.0, 0.1, key=f"ha_{crop}")
yld = c2.number_input("Expected yield (kg/ha)", 0, 20000, d["y"], 50, key=f"y_{crop}")
price = c3.number_input("Selling price (USD/kg)", 0.0, 50.0, d["price"], 0.01, key=f"p_{crop}")

st.markdown("**Costs per hectare (USD)**")
k = st.columns(5)
costs = {n: k[i].number_input(n.title(), 0.0, 10000.0, float(d[n]), 5.0, key=f"{n}_{crop}")
         for i, n in enumerate(["seed", "fert", "labor", "chem", "other"])}
cost_ha = sum(costs.values())
total_kg, total_cost = yld * ha, cost_ha * ha
if total_kg == 0 or price == 0:
    st.warning("Enter a yield and price above zero.")
    st.stop()

revenue = total_kg * price
profit = revenue - total_cost
m = st.columns(4)
m[0].metric("Total cost", f"${total_cost:,.0f}")
m[1].metric("Revenue", f"${revenue:,.0f}")
m[2].metric("Profit", f"${profit:,.0f}", f"{profit / revenue * 100:.0f}% margin")
m[3].metric("Profit per hectare", f"${profit / ha:,.0f}")
b = st.columns(2)
b[0].metric("Break-even price", f"${total_cost / total_kg:.3f}/kg")
b[1].metric("Break-even yield", f"{cost_ha / price:,.0f} kg/ha")
(st.success if profit > 0 else st.error)(
    "You make a profit at these numbers." if profit > 0 else "You make a loss at these numbers: raise yield or price, or cut costs.")

st.subheader("What if price or yield changes?")
fs = [0.8, 0.9, 1.0, 1.1, 1.2]
grid = pd.DataFrame({f"Yield {int((y - 1) * 100):+d}%": [total_kg * y * price * p - total_cost for p in fs] for y in fs},
                    index=[f"Price {int((p - 1) * 100):+d}%" for p in fs]).round(0)
shade = lambda v: "background-color:#c8e6c9;color:#12301a" if v >= 0 else "background-color:#ffcdd2;color:#12301a"
st.dataframe(grid.style.map(shade).format("${:,.0f}"))

st.subheader("Crop comparison (profit per hectare, default assumptions)")
comp = pd.DataFrame([(c, v["y"] * v["price"] - sum(v[x] for x in ["seed", "fert", "labor", "chem", "other"]))
                     for c, v in D.items()], columns=["Crop", "Profit per ha (USD)"])
st.plotly_chart(px.bar(comp, x="Crop", y="Profit per ha (USD)", color_discrete_sequence=["#ef6c00"]),
                width="stretch")
