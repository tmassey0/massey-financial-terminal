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
        return pd.DataFrame()

# --- 3. PERSISTENT "EDITABLE" MEMORY ---
# This ensures your edits to hours and earnings stay locked in
if 'cards' not in st.session_state:
    st.session_state.cards = load_data("Terrance Credit Card 1.xlsx", "Credit Cards", 1)
if 'bills' not in st.session_state:
    st.session_state.bills = load_data("Terrance Credit Card 1.xlsx", "Bill Master List", 1)
if 'uber' not in st.session_state:
    st.session_state.uber = load_data("Terrance Uber Tracker.xlsx", "March", 3)

# --- 4. THE COMMAND CENTER ---
st.title("🏛️ Massey Strategic Capital Terminal")
st.info("Strategy: Cash Flow Arbitrage | Legal Case vs Anamika Mishra/A3S LLC - ACTIVE")

tabs = st.tabs(["📊 DASHBOARD", "💳 MANAGE CARDS", "📅 MANAGE BILLS", "🚖 UBER LEDGER"])

# --- UBER LEDGER (FULLY EDITABLE) ---
with tabs[3]:
    st.subheader("Daily Drive Log")
    st.write("Double-click any cell to edit Hours or Earnings. Use the (+) to add a new day.")
    # This is where you add more cards, hours, and earnings
    edited_uber = st.data_editor(
        st.session_state.uber,
        num_rows="dynamic",
        use_container_width=True,
        key="uber_editor_final"
    )
    if st.button("💾 Save Uber Entries"):
        st.session_state.uber = edited_uber
        st.success("Uber data updated!")

# --- MANAGE CARDS (FULLY EDITABLE) ---
with tabs[1]:
    st.subheader("Edit Card Portfolio & Status")
    edited_cards = st.data_editor(
        st.session_state.cards,
        num_rows="dynamic",
        use_container_width=True,
        key="cards_editor_final"
    )
    if st.button("💾 Save Portfolio"):
        st.session_state.cards = edited_cards
        st.success("Card data updated!")

# --- MANAGE BILLS (FULLY EDITABLE) ---
with tabs[2]:
    st.subheader("Edit Monthly Burn List")
    edited_bills = st.data_editor(
        st.session_state.bills,
        num_rows="dynamic",
        use_container_width=True,
        key="bills_editor_final"
    )
    if st.button("💾 Save Bills"):
        st.session_state.bills = edited_bills
        st.success("Bill list updated!")

# --- DASHBOARD (THE BRAIN) ---
with tabs[0]:
    c = st.session_state.cards
    u = st.session_state.uber
    
    # Smart math: It looks for 'Balance' and 'Limit' by name, not index
    bal_col = next((col for col in c.columns if 'Balance' in col), None)
    lim_col = next((col for col in c.columns if 'Limit' in col), None)
    
    if bal_col and lim_col:
        total_bal = pd.to_numeric(c[bal_col], errors='coerce').sum()
        total_lim = pd.to_numeric(c[lim_col], errors='coerce').sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("TOTAL LIABILITIES", f"${total_bal:,.2f}")
        m2.metric("AVAILABLE CREDIT", f"${(total_lim - total_bal):,.2f}")
        m3.metric("UTILIZATION", f"{(total_bal/total_lim)*100:.1f}%" if total_lim > 0 else "0%")
    else:
        st.warning("Please ensure your Credit Card columns have the headers 'Balance' and 'Limit'.")

    st.divider()
    st.write("### Legal Update")
    st.write("- **Feb 4, 2026**: Judge denied Motion to Dismiss.")
    st.write("- **Parties**: Anamika Mishra and A3S LLC.")
