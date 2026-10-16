from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from theme import apply_theme

apply_theme("Input Price Tracker", "Compare seed and fertilizer prices and buy from the cheapest supplier.", "🧪")

INPUTS = {"Maize seed (hybrid)": 10, "Compound D": 50, "Ammonium nitrate": 50, "Urea": 50}  # default pack size (kg)
COLS = ["date", "input", "supplier", "location", "pack_kg", "price"]
# Fictional demo prices. Real prices come from farmers and suppliers reporting in this tracker.
seed = []
for i, (inp, pk) in enumerate(INPUTS.items()):
    base = {"Maize seed (hybrid)": 32, "Compound D": 48, "Ammonium nitrate": 40, "Urea": 42}[inp]
    for sup, loc, adj in [("Supplier A (demo)", "Harare", 0), ("Supplier B (demo)", "Marondera", -2.5),
                          ("Supplier C (demo)", "Gweru", 1.5), ("Supplier D (demo)", "Mutare", -1)]:
        for k, month in enumerate(["2026-07-01", "2026-08-01", "2026-09-01"]):
            seed.append((month, inp, sup, loc, pk, round(base + adj + k * 0.8, 2)))
if "input_prices" not in st.session_state:
    st.session_state.input_prices = pd.DataFrame(seed, columns=COLS)

P = st.session_state.input_prices.copy()
P["date"] = pd.to_datetime(P["date"])
P["per_kg"] = P.price / P.pack_kg
st.caption("Demo data is fictional. Add real prices in the Report tab. Entries last only for your session unless you download them.")

compare, trend, report, data = st.tabs(["🔎 Compare", "📈 Trends", "➕ Report a price", "💾 Data"])

with compare:
    inp = st.selectbox("Input", sorted(P.input.unique()))
    sub = P[P.input == inp]
    latest = sub.sort_values("date").groupby("supplier").tail(1).sort_values("per_kg")
    need = st.number_input("How much do you need (kg)?", 1, 1_000_000, 500, step=50)
    latest = latest.assign(cost=latest.per_kg * need)
    best, avg = latest.iloc[0], latest.cost.mean()
    c = st.columns(3)
    c[0].metric("Cheapest supplier", best.supplier.replace(" (demo)", ""), f"${best.per_kg:.3f}/kg", delta_color="off")
    c[1].metric("Cost at cheapest", f"${best.cost:,.0f}")
    c[2].metric("Saving vs average", f"${avg - best.cost:,.0f}")
    st.dataframe(latest[["supplier", "location", "pack_kg", "price", "per_kg", "cost", "date"]]
                 .rename(columns={"pack_kg": "Pack (kg)", "price": "Pack price ($)", "per_kg": "$/kg", "cost": f"Cost for {need} kg ($)"})
                 .round(3), hide_index=True, use_container_width=True)
    st.caption("Remember to add transport to the supplier when comparing. A cheaper price far away may cost more overall.")

with trend:
    inp2 = st.selectbox("Input to track", sorted(P.input.unique()), key="t")
    t = P[P.input == inp2].sort_values("date")
    st.plotly_chart(px.line(t, x="date", y="per_kg", color="supplier", markers=True, labels={"per_kg": "USD per kg", "date": ""}),
                    use_container_width=True)
    monthly = t.groupby("date").per_kg.mean()
    if len(monthly) >= 2:
        chg = (monthly.iloc[-1] / monthly.iloc[0] - 1) * 100
        st.info(f"Average price changed {chg:+.1f}% between {monthly.index[0]:%b %Y} and {monthly.index[-1]:%b %Y}.")

with report:
    with st.form("report_price", clear_on_submit=True):
        a, b = st.columns(2)
        r_inp = a.selectbox("Input", list(INPUTS) + ["Other"])
        r_other = b.text_input("If other, name it")
        r_sup = a.text_input("Supplier / shop name")
        r_loc = b.text_input("Location")
        r_pack = a.number_input("Pack size (kg)", 0.5, 1000.0, 50.0, 0.5)
        r_price = b.number_input("Price per pack (USD)", 0.0, 100000.0, 40.0, 0.5)
        r_date = st.date_input("Date seen", date.today())
        ok = st.form_submit_button("Submit price")
    if ok:
        name = r_other.strip() if r_inp == "Other" else r_inp
        if not name or not r_sup.strip() or r_price <= 0:
            st.error("Please fill in the input, supplier and a price above zero.")
        else:
            row = pd.DataFrame([(str(r_date), name, r_sup.strip(), r_loc.strip() or "Unknown", r_pack, r_price)], columns=COLS)
            st.session_state.input_prices = pd.concat([st.session_state.input_prices, row], ignore_index=True)
            st.success("Price added. Check the Compare tab.")

with data:
    st.download_button("⬇️ Download all prices (CSV)", st.session_state.input_prices.to_csv(index=False), "input_prices.csv")
    up = st.file_uploader("Upload a CSV with columns: " + ", ".join(COLS), type="csv")
    if up:
        try:
            new = pd.read_csv(up)[COLS]
            st.session_state.input_prices = pd.concat([st.session_state.input_prices, new], ignore_index=True)
            st.success(f"Added {len(new)} rows. Open the Compare tab.")
        except Exception:
            st.error("Could not read that file. Check the column names.")
