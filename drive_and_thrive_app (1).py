import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
def load_data(file, sheet, skip):
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        # If no file, create the structure you need
        return pd.DataFrame(columns=["Date", "Hours", "Earnings", "Daily Goal"])

# --- 3. PERSISTENT MEMORY ---
if 'cards' not in st.session_state:
    st.session_state.cards = load_data("Terrance Credit Card 1.xlsx", "Credit Cards", 1)
if 'bills' not in st.session_state:
    st.session_state.bills = load_data("Terrance Credit Card 1.xlsx", "Bill Master List", 1)
if 'uber' not in st.session_state:
    st.session_state.uber = load_data("Terrance Uber Tracker.xlsx", "March", 3)

# --- 4. THE COMMAND CENTER ---
st.title("🏛️ Massey Strategic Capital Terminal")
st.caption("Operational Dashboard | Cash Flow Arbitrage Strategy")

tabs = st.tabs(["📊 DASHBOARD", "🚖 UBER PERFORMANCE", "💳 CARDS & LIQUIDITY", "📅 BILL MASTER"])

# --- UBER PERFORMANCE (NOW FULLY EDITABLE) ---
with tabs[1]:
    st.subheader("Daily Revenue & Hours Ledger")
    st.write("Double-click any cell (Date, Hours, or Earnings) to change it.")
    
    # Use dynamic rows so you can add new drive days
    edited_uber = st.data_editor(
        st.session_state.uber,
        num_rows="dynamic",
        use_container_width=True,
        key="uber_editor_v5"
    )
    
    if st.button("Save Performance Data"):
        st.session_state.uber = edited_uber
        st.success("Uber ledger updated!")

# --- CARDS & LIQUIDITY (EDITABLE) ---
with tabs[2]:
    st.subheader("Card Portfolio Management")
    edited_cards = st.data_editor(
        st.session_state.cards,
        num_rows="dynamic",
        use_container_width=True,
        key="cards_editor_v5"
    )
    if st.button("Save Card Data"):
        st.session_state.cards = edited_cards
        st.success("Portfolio updated!")

# --- BILL MASTER (EDITABLE) ---
with tabs[3]:
    st.subheader("Monthly Burn List")
    edited_bills = st.data_editor(
        st.session_state.bills,
        num_rows="dynamic",
        use_container_width=True,
        key="bills_editor_v5"
    )
    if st.button("Save Bill Changes"):
        st.session_state.bills = edited_bills
        st.success("Bill list updated!")

# --- DASHBOARD (THE BRAIN) ---
with tabs[0]:
    c = st.session_state.cards
    u = st.session_state.uber
    
    # Find columns by keyword to avoid errors
    bal_col = next((col for col in c.columns if 'Balance' in col), None)
    lim_col = next((col for col in c.columns if 'Limit' in col), None)
    earn_col = next((col for col in u.columns if 'Earnings' in col), None)
    goal_col = next((col for col in u.columns if 'Goal' in col), None)
    
    m1, m2, m3 = st.columns(3)
    
    if bal_col and lim_col:
        total_bal = pd.to_numeric(c[bal_col], errors='coerce').sum()
        total_lim = pd.to_numeric(c[lim_col], errors='coerce').sum()
        m1.metric("TOTAL LIABILITIES", f"${total_bal:,.2f}")
        m2.metric("AVAILABLE CREDIT", f"${(total_lim - total_bal):,.2f}")
        m3.metric("UTILIZATION", f"{(total_bal/total_lim)*100:.1f}%" if total_lim > 0 else "0%")

    st.divider()
    
    if earn_col and not u.empty:
        st.subheader("Revenue Velocity")
        fig = px.bar(u, x=u.columns[0], y=earn_col, template="plotly_dark", title="Daily Gross Earnings")
        st.plotly_chart(fig, use_container_width=True)
