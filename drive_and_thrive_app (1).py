import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. BRANDING & UI CONFIG ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA LOAD ENGINE ---
def load_and_fix(file, sheet, skip, cols):
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna(0)
    except Exception as e:
        st.error(f"Error loading {file} / {sheet}: {e}")
        return pd.DataFrame(columns=cols)

# --- 3. PERSISTENT MEMORY ---
if 'cards' not in st.session_state:
    st.session_state.cards = load_and_fix(
        "Terrance-Credit-Card-1.xlsx", "Credit Cards", 1,
        ["Bank Name", "Balance", "Limit"]
    )

if 'bills' not in st.session_state:
    st.session_state.bills = load_and_fix(
        "Terrance-Credit-Card-1.xlsx", "Bill Master List", 1,
        ["Bill Name", "Amount"]
    )

if 'uber' not in st.session_state:
    st.session_state.uber = load_and_fix(
        "Terrance-Uber-Tracker-2.xlsx",
        "UBER EARNINGS - 2026 ANNUAL SUMMARY",  # adjust if you pick a different sheet
        3,
        ["Month", "Total Hours", "Total Earnings", "Monthly Goal", "Difference"]
    )
