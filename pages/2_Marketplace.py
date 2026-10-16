import re
import urllib.parse
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

from theme import apply_theme
apply_theme("Marketplace", "Connecting farmers directly to buyers: better prices for growers, reliable supply for buyers.", "🛒")

DISTRICTS = ["Harare", "Mazowe", "Bindura", "Chinhoyi", "Marondera", "Mutoko", "Gweru", "Kwekwe",
             "Bulawayo", "Masvingo", "Mutare", "Chipinge", "Hwange", "Gokwe"]
# Demo reference prices (USD/kg). In production, replace with forecasts from AgriPrice Advisor (Project 1).
REF = {"Maize": 0.36, "Sorghum": 0.40, "Wheat": 0.50, "Groundnuts": 1.30, "Soya beans": 0.58, "Tobacco": 3.30}

SEED = pd.DataFrame([
    ("Maize", 12000, 0.32, "Mazowe", "Mazowe Growers Co-op (demo)", "263770000001", "2026-05-20"),
    ("Maize", 4000, 0.38, "Marondera", "Demo Farmer 2", "263770000002", "2026-05-28"),
    ("Sorghum", 3000, 0.37, "Gweru", "Demo Farmer 3", "263770000003", "2026-06-02"),
    ("Wheat", 8000, 0.52, "Chinhoyi", "Demo Wheat Group", "263770000004", "2026-10-15"),
    ("Groundnuts", 1500, 1.20, "Mutoko", "Demo Farmer 5", "263770000005", "2026-06-10"),
    ("Soya beans", 6000, 0.55, "Bindura", "Demo Farmer 6", "263770000006", "2026-05-30"),
    ("Tobacco", 2500, 3.40, "Mazowe", "Demo Tobacco Grower", "263770000007", "2026-04-25"),
    ("Sorghum", 5000, 0.42, "Masvingo", "Demo Farmer 8", "263770000008", "2026-06-05"),
], columns=["crop", "qty_kg", "price_kg", "district", "seller", "phone", "harvest"])

if "listings" not in st.session_state:
    st.session_state.listings = SEED.copy()
L = st.session_state.listings


def flag(crop, price):
    r = price / REF[crop]
    return "🟢 Below market" if r <= 0.95 else "🟡 Fair price" if r <= 1.05 else "🔴 Above market"


st.sidebar.info("Prototype with demo listings. Do not enter real personal data. Listings reset when the app restarts.")
st.sidebar.download_button("⬇️ Download listings (CSV)", L.to_csv(index=False), "agrilink_listings.csv")

browse, sell, insights = st.tabs(["🛒 Buy", "🌱 Sell", "📊 Insights"])

with browse:
    f1, f2, f3, f4 = st.columns(4)
    crop = f1.selectbox("Crop", ["All"] + sorted(REF))
    dist = f2.selectbox("District", ["All"] + DISTRICTS)
    min_qty = f3.number_input("Min quantity (kg)", 0, 100000, 0, step=500)
    sort = f4.selectbox("Sort by", ["Cheapest", "Largest quantity", "Newest harvest"])
    v = L.copy()
    if crop != "All":
        v = v[v.crop == crop]
    if dist != "All":
        v = v[v.district == dist]
    v = v[v.qty_kg >= min_qty]
    v = v.sort_values({"Cheapest": "price_kg", "Largest quantity": "qty_kg", "Newest harvest": "harvest"}[sort],
                      ascending=(sort == "Cheapest"))
    st.caption(f"{len(v)} listing(s) found")
    for _, r in v.iterrows():
        with st.container(border=True):
            a, b = st.columns([3, 1])
            a.markdown(f"**{r.crop}** · {r.qty_kg:,} kg · 📍 {r.district}  \n"
                       f"${r.price_kg:.2f}/kg · {flag(r.crop, r.price_kg)} (ref ${REF[r.crop]:.2f})  \n"
                       f"Seller: {r.seller} · Harvest: {r.harvest}")
            msg = f"Hello, I saw your {r.qty_kg:,} kg of {r.crop} on AgriLink Zimbabwe at ${r.price_kg:.2f}/kg. Is it still available?"
            b.link_button("💬 WhatsApp", f"https://wa.me/{r.phone}?text=" + urllib.parse.quote(msg), use_container_width=True)

with sell:
    st.subheader("Post your produce")
    with st.form("new_listing", clear_on_submit=True):
        c1, c2 = st.columns(2)
        s_crop = c1.selectbox("Crop", sorted(REF))
        s_qty = c2.number_input("Quantity (kg)", 0, 1_000_000, 1000, step=100)
        s_price = c1.number_input("Asking price (USD per kg)", 0.0, 100.0, 0.35, step=0.01)
        s_dist = c2.selectbox("District", DISTRICTS)
        s_name = c1.text_input("Your name or group")
        s_phone = c2.text_input("WhatsApp number (e.g. 263771234567)")
        s_date = st.date_input("Harvest / available date", date.today())
        ok = st.form_submit_button("Post listing")
    if ok:
        phone = re.sub(r"\D", "", s_phone)
        if not s_name.strip() or len(phone) < 9 or s_qty <= 0 or s_price <= 0:
            st.error("Please fill in all fields with valid values.")
        else:
            st.session_state.listings = pd.concat([L, pd.DataFrame([dict(
                crop=s_crop, qty_kg=s_qty, price_kg=s_price, district=s_dist, seller=s_name.strip(),
                phone=phone, harvest=str(s_date))])], ignore_index=True)
            st.success(f"Posted! Price check: {flag(s_crop, s_price)} (reference ${REF[s_crop]:.2f}/kg).")

with insights:
    m1, m2, m3 = st.columns(3)
    m1.metric("Active listings", len(L))
    m2.metric("Total supply (tonnes)", f"{L.qty_kg.sum() / 1000:,.1f}")
    m3.metric("Districts", L.district.nunique())
    avg = L.groupby("crop", as_index=False).price_kg.mean().rename(columns={"price_kg": "Avg asking"})
    avg["Reference"] = avg.crop.map(REF)
    st.plotly_chart(px.bar(avg.melt("crop", var_name="Type", value_name="USD/kg"), x="crop", y="USD/kg",
                           color="Type", barmode="group", title="Asking vs reference price",
                           color_discrete_sequence=["#ef6c00", "#7cb342"]), use_container_width=True)
    sup = L.groupby("district", as_index=False).qty_kg.sum().sort_values("qty_kg")
    st.plotly_chart(px.bar(sup, x="qty_kg", y="district", orientation="h", title="Supply by district (kg)",
                           color_discrete_sequence=["#f9a825"]), use_container_width=True)
