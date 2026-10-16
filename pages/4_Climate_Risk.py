from datetime import date
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from theme import apply_theme
from climate import DISTRICTS, SEASON_MONTHS, get_history, add_season, season_stats

apply_theme("Climate & Drought Risk", "How often do dry seasons hit, and how risky is your district?", "🌦️")

picked = st.multiselect("Districts to compare (up to 4)", list(DISTRICTS), default=["Harare"], max_selections=4)
if not picked:
    st.stop()


def risk(freq, cv):
    return "🔴 High" if freq >= 0.30 or cv >= 0.35 else "🟡 Medium" if freq >= 0.20 or cv >= 0.25 else "🟢 Low"


data, rows, simulated = {}, [], False
for d in picked:
    h, src = get_history(d)
    simulated |= src.startswith("SIMULATED")
    h = add_season(h)
    s = season_stats(h)
    if s.empty:
        continue
    mean, cv = s.total.mean(), s.total.std() / s.total.mean()
    freq = float((s.total < 0.8 * mean).mean())
    data[d] = (h, s)
    rows.append({"District": d, "Avg season rain (mm)": round(mean), "Variability (CV)": round(cv, 2),
                 "Dry seasons (<80% of avg)": f"{freq * 100:.0f}%", "Avg longest dry spell (days)": round(s.dry_spell.mean(), 1),
                 "Risk": risk(freq, cv)})
if simulated:
    st.warning("Live climate data could not be loaded, so some results are SIMULATED for demonstration only.")
if not rows:
    st.error("Not enough climate history.")
    st.stop()

st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
st.caption("A dry season means total October-March rainfall below 80% of the long-term average. "
           "Variability (CV) is the standard deviation divided by the average; higher means less predictable.")

focus = st.selectbox("Detailed view", list(data))
h, s = data[focus]
mean = s.total.mean()
dry = s.total < 0.8 * mean
slope = np.polyfit(s.index.astype(float), s.total.values, 1)[0] * 10

m = st.columns(4)
m[0].metric("Driest season", f"{s.total.min():,.0f} mm", f"in {int(s.total.idxmin())}", delta_color="off")
m[1].metric("Wettest season", f"{s.total.max():,.0f} mm", f"in {int(s.total.idxmax())}", delta_color="off")
m[2].metric("Hot days (35°C+) per season", f"{s.heat_days.mean():.0f}")
m[3].metric("Rainfall trend", f"{slope:+.0f} mm/decade")

fig = go.Figure()
fig.add_bar(x=s.index.astype(int), y=s.total, marker_color=["#ef6c00" if x else "#7cb342" for x in dry], name="Season rain")
fig.add_scatter(x=s.index.astype(int), y=[mean] * len(s), mode="lines", name="Average", line=dict(color="#1b5e20", dash="dash"))
fig.add_scatter(x=s.index.astype(int), y=[0.8 * mean] * len(s), mode="lines", name="Dry threshold (80%)", line=dict(color="#c62828", dash="dot"))
fig.update_layout(height=340, margin=dict(t=10), yaxis_title="Oct-Mar rainfall (mm)", xaxis_title="Season start year",
                  legend=dict(orientation="h", y=-0.3))
st.plotly_chart(fig, use_container_width=True)

# Current season progress vs normal
today_season = date.today().year if date.today().month >= 7 else date.today().year - 1
w = h[h.date.dt.month.isin(SEASON_MONTHS)].copy()
w["off"] = (w.date - pd.to_datetime(w.season.astype(str) + "-10-01")).dt.days
cur = w[w.season == today_season]
if not cur.empty:
    cutoff = cur.off.max()
    so_far = cur.rain.sum()
    normal = w[(w.season < today_season) & (w.off <= cutoff)].groupby("season").rain.sum().mean()
    st.subheader(f"This season so far ({today_season}/{today_season + 1})")
    if normal and normal >= 20:
        st.metric("Rain since 1 October vs normal", f"{so_far:,.0f} mm", f"{so_far / normal * 100:.0f}% of normal", delta_color="off")
    else:
        st.caption("The season has only just started, so there is not enough rain data to compare yet.")

freq = float(dry.mean())
st.subheader("What this means for farmers")
if freq >= 0.30 or s.total.std() / mean >= 0.35:
    st.markdown("- Favour drought-tolerant crops (sorghum, pearl millet) and short-season varieties.\n"
                "- Use water harvesting, mulching and conservation agriculture.\n- Consider crop insurance and staggered planting.")
elif freq >= 0.20:
    st.markdown("- Mix crops: keep a drought-tolerant crop alongside maize.\n- Plant early with the first reliable rains.\n"
                "- Store some grain as a buffer for dry years.")
else:
    st.markdown("- Rainfall is relatively reliable here, but still plan for a dry year about 1 in 5.\n"
                "- Invest in yield-raising inputs and good storage.")
