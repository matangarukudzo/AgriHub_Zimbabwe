from datetime import date, timedelta
import numpy as np
import pandas as pd
import requests
import streamlit as st

# Approximate district-centre coordinates (lat, lon)
DISTRICTS = {
    "Harare": (-17.83, 31.05), "Mazowe": (-17.50, 30.97), "Bindura": (-17.30, 31.33),
    "Chinhoyi": (-17.36, 30.20), "Marondera": (-18.18, 31.55), "Mutoko": (-17.40, 32.22),
    "Gweru": (-19.45, 29.82), "Kwekwe": (-18.93, 29.81), "Bulawayo": (-20.15, 28.58),
    "Masvingo": (-20.07, 30.83), "Mutare": (-18.97, 32.67), "Chipinge": (-20.19, 32.62),
    "Hwange": (-18.37, 26.50), "Gokwe": (-18.22, 28.93),
}
SEASON_MONTHS = [10, 11, 12, 1, 2, 3]  # October to March rainy season


def _synthetic(district, start_year, end):
    """Fallback climate so the app still works offline. Clearly labelled as simulated in the UI."""
    lat = DISTRICTS[district][0]
    rng = np.random.default_rng(sum(map(ord, district)))
    scale = 1 - (-lat - 18) * 0.1
    p_wet = {10: .12, 11: .35, 12: .5, 1: .55, 2: .5, 3: .3, 4: .1}
    tmonth = {1: 28, 2: 28, 3: 27, 4: 26, 5: 24, 6: 22, 7: 22, 8: 25, 9: 29, 10: 32, 11: 31, 12: 29}
    yf = {y: rng.lognormal(0, .25) for y in range(start_year - 1, end.year + 1)}
    rows = []
    for d in pd.date_range(f"{start_year}-01-01", end):
        sy = d.year if d.month >= 7 else d.year - 1
        wet = rng.random() < p_wet.get(d.month, .03)
        rows.append((d, wet * rng.exponential(11 * scale * yf[sy]), tmonth[d.month] + rng.normal(0, 2) - (scale - 1) * -3))
    return pd.DataFrame(rows, columns=["date", "rain", "tmax"])


@st.cache_data(ttl=86400, show_spinner="Loading climate data...")
def get_history(district, start_year=2000):
    lat, lon = DISTRICTS[district]
    end = date.today() - timedelta(days=7)
    try:
        r = requests.get("https://archive-api.open-meteo.com/v1/archive", timeout=30, params=dict(
            latitude=lat, longitude=lon, start_date=f"{start_year}-01-01", end_date=end.isoformat(),
            daily="precipitation_sum,temperature_2m_max", timezone="Africa/Harare"))
        r.raise_for_status()
        d = r.json()["daily"]
        df = pd.DataFrame({"date": pd.to_datetime(d["time"]), "rain": d["precipitation_sum"], "tmax": d["temperature_2m_max"]})
        df["rain"] = df.rain.fillna(0.0)
        return df, "Open-Meteo (live)"
    except Exception:
        return _synthetic(district, start_year, end), "SIMULATED (live data unavailable)"


@st.cache_data(ttl=10800, show_spinner=False)
def get_forecast(district):
    lat, lon = DISTRICTS[district]
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", timeout=20, params=dict(
            latitude=lat, longitude=lon, daily="precipitation_sum,temperature_2m_max", forecast_days=16,
            timezone="Africa/Harare"))
        r.raise_for_status()
        d = r.json()["daily"]
        return pd.DataFrame({"date": pd.to_datetime(d["time"]), "rain": d["precipitation_sum"], "tmax": d["temperature_2m_max"]}).fillna(0)
    except Exception:
        return None


def add_season(df):
    df = df.copy()
    df["season"] = np.where(df.date.dt.month >= 7, df.date.dt.year, df.date.dt.year - 1)
    return df


def longest_run(mask):
    best = cur = 0
    for x in mask:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best


def season_stats(df):
    """Per complete rainy season (Oct-Mar): total rain, hot days (35C+), longest dry spell (<1 mm/day)."""
    w = df[df.date.dt.month.isin(SEASON_MONTHS)]
    rows = {}
    for s, g in w.groupby("season"):
        if len(g) < 175:
            continue  # skip incomplete (current) season
        rows[s] = dict(total=g.rain.sum(), heat_days=int((g.tmax >= 35).sum()),
                       dry_spell=longest_run((g[g.date.dt.month.isin([11, 12, 1, 2, 3])].rain < 1).values))
    return pd.DataFrame(rows).T


def onset_dates(df):
    """First day from 15 Oct with 20+ mm in 3 days and no 10-day spell under 5 mm in the next 3 weeks."""
    out = {}
    for y in sorted(df.date.dt.year.unique()):
        w = df[(df.date >= f"{y}-10-15") & (df.date <= f"{y + 1}-03-15")]
        if len(w) < 150:
            continue
        arr, dates = w.rain.values, w.date.values
        c = np.concatenate([[0], np.cumsum(arr)])
        for i in range(2, len(arr) - 23):
            if c[i + 1] - c[i - 2] >= 20 and all(c[j + 10] - c[j] >= 5 for j in range(i + 1, i + 13)):
                out[y] = pd.Timestamp(dates[i])
                break
    return pd.Series(out, dtype="datetime64[ns]")


def onset_days(onsets):
    """Days since 1 October of the same year."""
    return pd.Series([(d - pd.Timestamp(f"{y}-10-01")).days for y, d in onsets.items()], index=onsets.index)


def natural_region(season_rain):
    r = season_rain * 1.05  # rough annual equivalent
    if r >= 1000: return "Region I (very high rainfall)"
    if r >= 750: return "Region II (high rainfall)"
    if r >= 650: return "Region III (moderate)"
    if r >= 450: return "Region IV (low, drought-prone)"
    return "Region V (very low)"
