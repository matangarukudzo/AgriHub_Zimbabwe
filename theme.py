import streamlit as st

# Green theme. Text colours are set explicitly so headings stay visible even when the
# phone or browser is in dark mode.
CSS = """<style>
.stApp {background: linear-gradient(180deg,#f3faf0,#dff0d8) !important;}
header[data-testid="stHeader"] {background: transparent !important;}
section[data-testid="stSidebar"] > div {background: #e3f2dc !important;}
.block-container {padding-top: 1.2rem; max-width: 1100px;}

/* Text: always dark green on the light background */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp p, .stApp li, .stApp label, .stApp summary,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMetricLabel"], .stApp [data-testid="stMetricValue"],
.stApp button[data-baseweb="tab"] p {color: #12301a !important;}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] p {color: #3f6b48 !important;}
.stApp h2, .stApp h3 {color: #1b5e20 !important;}
.stApp button[data-baseweb="tab"][aria-selected="true"] p {color: #1b5e20 !important; font-weight: 700;}

/* Inputs: light boxes with dark text */
.stApp input, .stApp textarea {color: #12301a !important; -webkit-text-fill-color: #12301a !important;
    background: #ffffff !important;}
.stApp div[data-baseweb="select"] > div {background: #ffffff !important;}
.stApp div[data-baseweb="select"] * {color: #12301a !important;}

/* Cards and header */
[data-testid="stMetric"] {background: #ffffff; border: 1px solid #bfe0b4; border-radius: 14px;
    padding: 12px 14px; box-shadow: 0 2px 8px rgba(27,94,32,.10);}
.hero {background: linear-gradient(135deg,#1b5e20,#2e7d32 55%,#66bb6a); border-radius: 16px;
    padding: 20px 24px; margin-bottom: 16px; box-shadow: 0 4px 14px rgba(27,94,32,.25);}
.stApp .hero h1 {margin: 0; font-size: 1.7rem; color: #ffffff !important;}
.stApp .hero p {margin: 6px 0 0; color: #ffffff !important;}
</style>"""


def apply_theme(title: str, subtitle: str, icon: str = "🌾"):
    st.set_page_config(page_title=f"{title} | AgriHub", page_icon=icon, layout="wide")
    st.markdown(CSS + f'<div class="hero"><h1>{icon} {title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)
