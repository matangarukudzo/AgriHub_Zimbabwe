import pandas as pd
import plotly.express as px
import streamlit as st
from theme import apply_theme

apply_theme("Post-Harvest Loss Tracker", "See where produce is lost and what fixing it is worth.", "📦")

STAGES = [
    ("Harvesting", 3, 1.5, "Harvest at the right maturity; use clean tarps and sacks."),
    ("Drying & threshing", 4, 2, "Dry to safe moisture (maize about 13%); use tarps, not bare ground."),
    ("Storage", 8, 2, "Use hermetic bags or treated, ventilated stores; check for pests monthly."),
    ("Transport", 3, 1.5, "Use strong sacks, cover loads and avoid delays."),
    ("Handling & market", 2, 1, "Grade and weigh properly; sell quickly after arrival."),
]
st.caption("Default loss rates are illustrative. Use your own estimates from your last season.")

c1, c2, c3 = st.columns(3)
qty = c1.number_input("Quantity harvested (kg)", 100, 10_000_000, 10000, step=100)
price = c2.number_input("Price (USD/kg)", 0.01, 50.0, 0.36, 0.01)
cost = c3.number_input("Cost of improvements (USD)", 0.0, 100000.0, 150.0, 10.0)

st.markdown("**Loss % at each stage: now vs. after improvement**")
now_pct, new_pct = [], []
for name, cur, imp, _ in STAGES:
    a, b = st.columns(2)
    now_pct.append(a.slider(f"{name}: now", 0.0, 30.0, float(cur), 0.5, key=f"n{name}"))
    new_pct.append(b.slider(f"{name}: improved", 0.0, 30.0, float(imp), 0.5, key=f"i{name}"))


def run(pcts):
    rem, losses = float(qty), []
    for p in pcts:
        loss = rem * p / 100
        losses.append(loss)
        rem -= loss
    return rem, losses


rem_now, loss_now = run(now_pct)
rem_new, loss_new = run(new_pct)
lost_now, saved_kg = qty - rem_now, rem_new - rem_now
saved_usd = saved_kg * price

m = st.columns(4)
m[0].metric("Total lost now", f"{lost_now:,.0f} kg", f"{lost_now / qty * 100:.1f}% of harvest", delta_color="off")
m[1].metric("Value lost now", f"${lost_now * price:,.0f}")
m[2].metric("Extra kg saved", f"{saved_kg:,.0f} kg")
m[3].metric("Extra income", f"${saved_usd:,.0f}")
if saved_usd > cost > 0:
    st.success(f"The improvements pay for themselves: about ${saved_usd - cost:,.0f} net gain, a return of "
               f"{(saved_usd - cost) / cost * 100:.0f}% on the ${cost:,.0f} spent.")
elif saved_usd <= cost:
    st.warning("At these numbers the improvements cost more than they save. Try cheaper fixes or larger volumes.")

df = pd.DataFrame({"Stage": [s[0] for s in STAGES] * 2, "Value lost (USD)": [x * price for x in loss_now + loss_new],
                   "Scenario": ["Now"] * len(STAGES) + ["Improved"] * len(STAGES)})
st.plotly_chart(px.bar(df, x="Stage", y="Value lost (USD)", color="Scenario", barmode="group",
                       color_discrete_sequence=["#ef6c00", "#7cb342"]), use_container_width=True)

worst = max(range(len(STAGES)), key=lambda i: loss_now[i])
st.info(f"Biggest loss stage: **{STAGES[worst][0]}**. Tip: {STAGES[worst][3]}")
with st.expander("Tips for every stage"):
    for n, _, _, tip in STAGES:
        st.markdown(f"- **{n}:** {tip}")
