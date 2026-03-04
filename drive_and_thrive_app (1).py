import streamlit as st
import pandas as pd
import plotly.express as px  # or graph_objects if you prefer

# --- 1. BRANDING & UI CONFIG ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

st.markdown(
    """
    <style>
        html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
        div[data-testid="stMetric"] {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 20px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
