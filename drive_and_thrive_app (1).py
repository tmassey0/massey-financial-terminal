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
        # Force every cell to be a number or empty, clearing the "Lock"
        return df.fillna(0)
    except:
        return pd.DataFrame(columns=cols)

# --- 3. PERSISTENT MEMORY ---
if 'cards' not in st.session_state:
    st.session_state.cards = load_and_fix("Terrance Credit Card 1.xlsx", "Credit Cards", 1, ["Bank Name", "Balance", "Limit"])
if 'bills' not in st.session_state:
    st.session_state.bills = load_and_fix("Terrance Credit Card 1.xlsx", "Bill Master List", 1, ["Bill Name", "Amount"])
if 'uber' not in st.session_state:
    st.session_state.uber = load_and_fix("Terrance Uber Tracker.xlsx", "March", 3, ["Date", "Hours Worked", "Gross Earnings", "Daily Goal", "Difference"])

# --- 4. THE COMMAND CENTER ---
st.title("🏛️ Massey Strategic Capital Terminal")

tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS & LIQUIDITY", "📅 BILL MASTER", "🚖 UBER PERFORMANCE"])

# --- DASHBOARD ---
with tabs[0]:
    c = st.session_state.cards
    bal_col = next((col for col in c.columns if 'Balance' in col), None)
    lim_col = next((col for col in c.columns if 'Limit' in col), None)
    
    m1, m2, m3 = st.columns(3)
    if bal_col and lim_col:
        b = pd.to_numeric(c[bal_col], errors='coerce').sum()
        l = pd.to_numeric(c[lim_col], errors='coerce').sum()
        m1.metric("TOTAL LIABILITIES", f"${b:,.2f}")
        m2.metric("AVAILABLE CREDIT", f"${(l - b):,.2f}")
        m3.metric("UTILIZATION", f"{(b/l)*100:.1f}%" if l > 0 else "0%")

# --- CARDS ---
with tabs[1]:
    st.subheader("Manage Portfolio")
    st.session_state.cards = st.data_editor(st.session_state.cards, num_rows="dynamic", use_container_width=True, key="ce_final")
    if st.button("Save Cards"): st.rerun()

# --- BILLS ---
with tabs[2]:
    st.subheader("Manage Bills")
    st.session_state.bills = st.data_editor(st.session_state.bills, num_rows="dynamic", use_container_width=True, key="be_final")
    if st.button("Save Bills"): st.rerun()

# --- UBER PERFORMANCE (THE FORCED FIX) ---
with tabs[3]:
    st.subheader("Edit Drive Performance")
    st.info("Double-click a zero to change it. Use (+) at bottom for new rows.")
    
    # We are using column_config to EXPLICITLY UNLOCK these boxes
    edited_uber = st.data_editor(
        st.session_state.uber,
        num_rows="dynamic",
        use_container_width=True,
        key="ue_final",
        column_config={
            "Hours Worked": st.column_config.NumberColumn(disabled=False),
            "Gross Earnings": st.column_config.NumberColumn(disabled=False, format="$%f"),
            "Daily Goal": st.column_config.NumberColumn(disabled=False, format="$%f"),
            "Difference": st.column_config.NumberColumn(disabled=False, format="$%f")
        }
    )
    
    if st.button("Commit & Calculate"):
        # This part does the math automatically so you don't have to
        edited_uber["Difference"] = edited_uber["Gross Earnings"] - edited_uber["Daily Goal"]
        st.session_state.uber = edited_uber
        st.rerun()
