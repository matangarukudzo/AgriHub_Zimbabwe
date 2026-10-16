import streamlit as st
from theme import apply_theme

apply_theme("AgriHub Zimbabwe", "One platform to plan, grow, harvest, sell and finance, built for Zimbabwean farmers.", "🌾")

GROUPS = {
    "1. Plan": [
        ("pages/1_Price_Forecaster.py", "Price Forecaster", "📈", "Forecast crop prices and find the best month to sell."),
        ("pages/3_Planting_Advisor.py", "Planting Advisor", "🌱", "When planting rains start and which crops suit your district."),
        ("pages/4_Climate_Risk.py", "Climate & Drought Risk", "🌦️", "How often dry seasons hit and how risky your area is."),
    ],
    "2. Grow": [
        ("pages/8_Input_Prices.py", "Input Price Tracker", "🧪", "Compare seed and fertilizer prices across suppliers."),
        ("pages/5_Profit_Calculator.py", "Farm Profit Calculator", "💰", "Break-even price, profit per hectare, crop comparison."),
    ],
    "3. Harvest": [
        ("pages/6_Post_Harvest_Losses.py", "Post-Harvest Loss Tracker", "📦", "Find where produce is lost and what fixing it is worth."),
    ],
    "4. Sell": [
        ("pages/2_Marketplace.py", "Marketplace", "🛒", "Post produce or find buyers and contact them on WhatsApp."),
        ("pages/7_Transport_Planner.py", "Transport & Market Planner", "🚚", "Which market pays most after transport costs?"),
    ],
    "5. Finance": [
        ("pages/9_Loan_Readiness.py", "Loan Readiness Scorer", "🏦", "Check loan readiness and how to improve it."),
    ],
}
for stage, tools in GROUPS.items():
    st.subheader(stage)
    for path, name, icon, desc in tools:
        with st.container(border=True):
            st.page_link(path, label=f"**{name}**", icon=icon)
            st.caption(desc)

st.info("Default figures in these tools are illustrative. Replace them with your own real costs, yields and prices. "
        "Climate pages use free Open-Meteo data when available.")
