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

# --- 2. DATA LOAD ENGINE (CLEANS 'NONE' ON LOAD) ---
def load_and_scrub(file, sheet, skip, default_cols):
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        df.columns = [str(c).strip() for c in df.columns]
        # FIX: Replace 'None' and 'NaN' with 0 for numbers or empty strings for text
        df = df.fillna(0) 
        return df
    except:
        return pd.DataFrame(columns=default_cols)

# --- 3. PERSISTENT SESSION STATE ---
if 'cards' not in st.session_state:
    st.session_state.cards = load_and_scrub("Terrance Credit Card 1.xlsx", "Credit Cards", 1, ["Bank Name", "Balance", "Limit"])
if 'bills' not in st.session_state:
    st.session_state.bills = load_and_scrub("Terrance Credit Card 1.xlsx", "Bill Master List", 1, ["Bill Name", "Amount", "Due Day"])
if 'uber' not in st.session_state:
    # Ensure Uber headers match exactly what's in your sheet
    st.session_state.uber = load_and_scrub("Terrance Uber Tracker.xlsx", "March", 3, ["Date", "Hours Worked", "Gross Earnings", "Daily Goal", "Difference"])

# --- 4. THE COMMAND CENTER ---
st.title("🏛️ Massey Strategic Capital Terminal")

tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS & LIQUIDITY", "📅 BILL MASTER", "🚖 UBER PERFORMANCE"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    c = st.session_state.cards
    u = st.session_state.uber
    
    # Calculate Totals
    bal_col = next((col for col in c.columns if 'Balance' in col), None)
    lim_col = next((col for col in c.columns if 'Limit' in col), None)
    
    m1, m2, m3 = st.columns(3)
    if bal_col and lim_col and not c.empty:
        total_bal = pd.to_numeric(c[bal_col], errors='coerce').sum()
        total_lim = pd.to_numeric(c[lim_col], errors='coerce').sum()
        m1.metric("TOTAL LIABILITIES", f"${total_bal:,.2f}")
        m2.metric("AVAILABLE CREDIT", f"${(total_lim - total_bal):,.2f}")
        m3.metric("UTILIZATION", f"{(total_bal/total_lim)*100:.1f}%" if total_lim > 0 else "0%")

# --- TAB 2: CARDS & LIQUIDITY ---
with tabs[1]:
    st.subheader("Manage Credit Card Portfolio")
    st.session_state.cards = st.data_editor(
        st.session_state.cards,
        num_rows="dynamic",
        use_container_width=True,
        key="cards_edit_vFinal"
    )
    if st.button("Save Cards"): st.success("Saved")

# --- TAB 3: BILL MASTER ---
with tabs[2]:
    st.subheader("Monthly Burn List")
    st.session_state.bills = st.data_editor(
        st.session_state.bills,
        num_rows="dynamic",
        use_container_width=True,
        key="bills_edit_vFinal"
    )
    if st.button("Save Bills"): st.success("Saved")

# --- TAB 4: UBER PERFORMANCE (THE FIX) ---
with tabs[3]:
    st.subheader("Daily Drive Log")
    st.info("Boxes should now be empty or '0' instead of 'None'. Double-click to type.")
    
    # FORCING EDITABILITY BY DEFINING COLUMN TYPES
    edited_uber = st.data_editor(
        st.session_state.uber,
        num_rows="dynamic",
        use_container_width=True,
        key="uber_edit_vFinal",
        column_config={
            "Date": st.column_config.TextColumn("Date"),
            "Hours Worked": st.column_config.NumberColumn("Hours", format="%.2f", min_value=0),
            "Gross Earnings": st.column_config.NumberColumn("Earnings", format="$%.2f", min_value=0),
            "Daily Goal": st.column_config.NumberColumn("Goal", format="$%.2f", min_value=0),
            "Difference": st.column_config.NumberColumn("Diff", format="$%.2f")
        }
    )
    
    if st.button("Commit Uber Data"):
        # Auto-calculate the difference column
        try:
            e = pd.to_numeric(edited_uber.iloc[:, 2], errors='coerce').fillna(0) # Earnings
            g = pd.to_numeric(edited_uber.iloc[:, 3], errors='coerce').fillna(0) # Goal
            edited_uber.iloc[:, 4] = e - g # Difference
        except:
            pass
        st.session_state.uber = edited_uber
        st.rerun() # Refresh to show the new math
