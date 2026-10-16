import pandas as pd
import plotly.express as px
import streamlit as st
from theme import apply_theme

apply_theme("Loan Readiness Scorer", "Check how ready a farm is for a loan, and how to improve.", "🏦")
st.caption("Educational tool only. It is not a lending decision, and real lenders use their own criteria.")

a, b = st.columns(2)
with a:
    years = st.slider("Years farming", 0, 30, 3)
    records = st.selectbox("Farm records (inputs, yields, sales)", ["Yes, regularly", "Partly", "No"])
    ratio = st.slider("Your yield vs. district average (%)", 50, 150, 100)
    formal = st.slider("Share of sales to formal/contract buyers (%)", 0, 100, 30)
    history = st.selectbox("Repayment history", ["Good", "No history yet", "Some late payments", "Defaulted before"])
with b:
    collateral = st.selectbox("Collateral or guarantee", ["None", "Group guarantee", "Equipment or livestock", "Land lease or title"])
    insured = st.checkbox("Crop insurance")
    coop = st.checkbox("Member of a cooperative or farmer group")
    revenue = st.number_input("Expected yearly revenue (USD)", 0.0, 10_000_000.0, 4000.0, 100.0)
    costs = st.number_input("Expected yearly costs (USD)", 0.0, 10_000_000.0, 2500.0, 100.0)

st.markdown("**Loan details**")
l1, l2, l3 = st.columns(3)
amount = l1.number_input("Loan amount (USD)", 0.0, 10_000_000.0, 1500.0, 100.0)
rate = l2.number_input("Interest rate (% per year)", 0.0, 100.0, 15.0, 0.5)
months = l3.number_input("Term (months)", 1, 120, 12)

r = rate / 100 / 12
monthly = amount / months if r == 0 else amount * r / (1 - (1 + r) ** -months)
annual_payment = monthly * 12
net = revenue - costs
dscr = net / annual_payment if annual_payment > 0 else float("inf")

parts = {
    "Experience": (min(years, 10), 10),
    "Record keeping": ({"Yes, regularly": 10, "Partly": 5, "No": 0}[records], 10),
    "Yield performance": (max(0, min(1, (ratio - 50) / 100)) * 15, 15),
    "Formal market access": (formal / 100 * 15, 15),
    "Repayment history": ({"Good": 15, "No history yet": 8, "Some late payments": 3, "Defaulted before": 0}[history], 15),
    "Collateral / guarantee": ({"None": 0, "Group guarantee": 8, "Equipment or livestock": 7, "Land lease or title": 10}[collateral], 10),
    "Insurance": (5 if insured else 0, 5),
    "Cooperative membership": (5 if coop else 0, 5),
    "Repayment capacity": (15 if dscr >= 1.5 else 10 if dscr >= 1.2 else 5 if dscr >= 1.0 else 0, 15),
}
score = sum(v for v, _ in parts.values())
label = "Ready" if score >= 75 else "Almost ready" if score >= 55 else "Build up first"

m = st.columns(4)
m[0].metric("Readiness score", f"{score:.0f}/100", label, delta_color="off")
m[1].metric("Monthly repayment", f"${monthly:,.0f}")
m[2].metric("Net income / yr", f"${net:,.0f}")
m[3].metric("Repayment cover", "n/a" if dscr == float("inf") else f"{dscr:.2f}x")
if dscr < 1:
    st.error("Expected net income does not cover the yearly repayments. Reduce the loan or extend the term.")

df = pd.DataFrame([(k, v / mx * 100) for k, (v, mx) in parts.items()], columns=["Factor", "Strength (%)"]).sort_values("Strength (%)")
st.plotly_chart(px.bar(df, x="Strength (%)", y="Factor", orientation="h", color_discrete_sequence=["#7cb342"],
                       range_x=[0, 100]), use_container_width=True)

TIPS = {
    "Record keeping": "Keep a simple notebook or app of inputs, yields and sales.",
    "Yield performance": "Improve seed, fertilizer timing and extension advice to raise yields.",
    "Formal market access": "Seek contract farming or cooperative marketing arrangements.",
    "Repayment history": "Start with a small loan or savings group and repay on time.",
    "Collateral / guarantee": "Join a group guarantee scheme or document land and assets.",
    "Insurance": "Consider crop insurance to protect repayment ability.",
    "Cooperative membership": "Join a cooperative for bargaining power and group guarantees.",
    "Repayment capacity": "Lower the loan, lengthen the term or raise income before applying.",
    "Experience": "Experience builds over time; document your track record.",
}
weak = sorted(parts, key=lambda k: parts[k][0] / parts[k][1])[:3]
st.subheader("Top 3 ways to improve")
for k in weak:
    st.markdown(f"- **{k}:** {TIPS[k]}")
