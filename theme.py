import streamlit as st

CSS = """<style>
.stApp {background: linear-gradient(180deg,#fff8e1,#ffe9c7) !important;}
section[data-testid="stSidebar"] > div {background: #fff3e0 !important;}
.hero {background: linear-gradient(135deg,#ef6c00,#f9a825 55%,#7cb342); border-radius: 16px; padding: 20px 24px; margin-bottom: 16px;}
.hero h1 {margin: 0; font-size: 1.7rem; color: #fff !important;}
.hero p {margin: 6px 0 0; color: #fff !important;}
[data-testid="stMetric"] {background: #fff; border: 1px solid #f3d9a8; border-radius: 14px; padding: 12px 14px;}
</style>"""


def apply_theme(title: str, subtitle: str, icon: str = "🌾"):
    st.set_page_config(page_title=f"{title} | AgriHub", page_icon=icon, layout="wide")
    st.markdown(CSS + f'<div class="hero"><h1>{icon} {title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)
