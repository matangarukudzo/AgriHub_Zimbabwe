import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from theme import apply_theme
from climate import (DISTRICTS, get_history, get_forecast, add_season, season_stats,
                     onset_dates, onset_days, natural_region)

apply_theme("Planting Advisor", "When do planting rains usually start, and which crops suit your area?", "🌱")

district = st.selectbox("District", list(DISTRICTS))
hist, source = get_history(district)
if source.startswith("SIMULATED"):
    st.warning("Live climate data could not be loaded, so this page shows SIMULATED data for demonstration only.")
else:
    st.caption(f"Data: {source}, daily rainfall since 2000.")

hist = add_season(hist)
stats, onsets = season_stats(hist), onset_dates(hist)
if stats.empty or len(onsets) < 5:
    st.error("Not enough climate history for this district.")
    st.stop()

od = onset_days(onsets)
base = pd.Timestamp("2001-10-01")
fmt = lambda d: (base + pd.Timedelta(days=float(d))).strftime("%d %b")
med, early, late = od.median(), od.quantile(0.1), od.quantile(0.9)
mean_rain, p20 = stats.total.mean(), stats.total.quantile(0.2)

m = st.columns(4)
m[0].metric("Typical planting rains", fmt(med))
m[1].metric("Early / late years", f"{fmt(early)} / {fmt(late)}")
m[2].metric("Average season rain", f"{mean_rain:,.0f} mm")
m[3].metric("Rainfall zone", natural_region(mean_rain).split(" (")[0])
st.caption(f"{natural_region(mean_rain)}. Planting rains = 20 mm or more in 3 days from 15 October, "
           "with no long dry spell in the next 3 weeks.")

dates = [base + pd.Timedelta(days=int(d)) for d in od.values]
fig = go.Figure()
fig.add_scatter(x=od.index, y=dates, mode="markers+lines", name="Onset date", marker=dict(color="#ef6c00"))
fig.add_scatter(x=[od.index.min(), od.index.max()], y=[base + pd.Timedelta(days=float(med))] * 2,
                mode="lines", name="Median", line=dict(color="#7cb342", dash="dash"))
fig.update_layout(height=320, margin=dict(t=10), yaxis_title="Planting rains start", xaxis_title="Season start year",
                  yaxis_tickformat="%d %b", legend=dict(orientation="h", y=-0.3))
st.plotly_chart(fig, use_container_width=True)

# Approximate agronomic needs: (days to maturity, minimum seasonal rainfall in mm). Confirm with local extension officers.
CROPS = {
    "Maize (medium season)": (140, 500), "Maize (short season)": (115, 450), "Sorghum": (120, 350),
    "Pearl millet (mhunga)": (95, 250), "Soya beans": (125, 450), "Groundnuts": (125, 450),
}
END_OF_RAINS = 210  # about 30 April, as days after 1 October
rows = []
for crop, (days, need) in CROPS.items():
    fit = "✅ Good" if p20 >= need else "⚠️ Risky in dry years" if mean_rain >= need else "❌ Poor fit"
    late_finish = med + days > END_OF_RAINS
    rows.append({"Crop": crop, "Plant from": fmt(med), "Plant by": fmt(med + 14), "Ready about": fmt(med + days),
                 "Suitability": fit + (" · late finish" if late_finish else "")})
st.subheader("Crop suitability for this district")
st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
st.caption("Suitability compares each crop's approximate minimum rainfall with the average season and a dry year "
           "(1 in 5). Dates and requirements are guides, not guarantees. Confirm with your extension officer.")

st.subheader("Next 16 days: rainfall outlook")
fc = get_forecast(district)
if fc is None:
    st.info("The weather forecast is unavailable right now.")
else:
    st.plotly_chart(px.bar(fc, x="date", y="rain", labels={"rain": "Rain (mm)", "date": ""},
                           color_discrete_sequence=["#42a5f5"]).update_layout(height=260, margin=dict(t=10)),
                    use_container_width=True)
    if fc.rain.rolling(3).sum().max() >= 20:
        st.success("A heavy rain spell (20 mm or more in 3 days) is forecast. Do not rush to plant: wait for follow-up rains.")
    else:
        st.info("No planting-type rain spell is forecast in the next 16 days.")
