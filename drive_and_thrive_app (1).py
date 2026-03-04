import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. THE DATA ENGINES (READ/WRITE) ---
def load_excel_data(file, sheet, skip=0):
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        # Ensure all column names are clean
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        # Create a default structure if the file isn't found
        return pd.DataFrame(columns=["Date", "Gross Earnings", "Daily Goal", "Hours Worked"])

# --- 3. PERSISTENT STATE ---
# This keeps your edits alive while you switch between tabs
if 'cards_data' not in st.session_state:
    st.session_state.cards_data = load_excel_data("Terrance Credit Card 1.xlsx", "Credit Cards", 1)
if 'bills_data' not in st.session_state:
    st.session_state.bills_data = load_excel_data("Terrance Credit Card 1.xlsx", "Bill Master List", 1)
if 'uber_data' not in st.session_state:
    st.session_state.uber_data = load_excel_data("Terrance Uber Tracker.xlsx", "March", 3)

# --- 4. THE COMMAND CENTER ---
st.title("🏛️ Massey Strategic Capital Terminal")
st.caption("Live Operational Command & Financial Arbitrage")

tabs = st.tabs(["📊 DASHBOARD", "💳 MANAGE CARDS", "📅 MANAGE BILLS", "🚖 UBER LEDGER"])

# --- TAB: UBER LEDGER (THE EDITING SUITE) ---
with tabs[3]:
    st.subheader("Daily Performance Entry")
    st.write("Click any cell to edit. Use the **(+)** at the bottom to add a new day of work.")
    
    # We enable 'num_rows="dynamic"' so you can add/delete rows
    edited_uber = st.data_editor(
        st.session_state.uber_data, 
        num_rows="dynamic", 
        use_container_width=True,
        key="uber_editor"
    )
    
    if st.button("💾 Commit Uber Entries"):
        st.session_state.uber_data = edited_uber
        st.success("Uber Ledger updated in terminal memory!")

# --- TAB: MANAGE CARDS ---
with tabs[1]:
    st.subheader("Edit Card Portfolio")
    edited_cards = st.data_editor(
        st.session_state.cards_data, 
        num_rows="dynamic", 
        use_container_width=True,
        key="cards_editor"
    )
    if st.button("💾 Commit Portfolio Changes"):
        st.session_state.cards_data = edited_cards
        st.success("Card data updated!")

# --- TAB: MANAGE BILLS ---
with tabs[2]:
    st.subheader("Edit Bill Schedule")
    edited_bills = st.data_editor(
        st.session_state.bills_data, 
        num_rows="dynamic", 
        use_container_width=True,
        key="bills_editor"
    )
    if st.button("💾 Commit Bill Changes"):
        st.session_state.bills_data = edited_bills
        st.success("Bill schedule updated!")

# --- TAB: DASHBOARD (THE CALCULATION ENGINE) ---
with tabs[0]:
    # We perform math ONLY on valid numbers to prevent crashes
    u_df = st.session_state.uber_data.copy()
    c_df = st.session_state.cards_data.copy()
    
    # Scrubbing data for math
    u_df['Gross Earnings'] = pd.to_numeric(u_df['Gross Earnings'], errors='coerce').fillna(0)
    u_df['Daily Goal'] = pd.to_numeric(u_df['Daily Goal'], errors='coerce').fillna(0)
    u_df['Variance'] = u_df['Gross Earnings'] - u_df['Daily Goal']
    
    c_df['Balance'] = pd.to_numeric(c_df.iloc[:, 1], errors='coerce').fillna(0)
    c_df['Limit'] = pd.to_numeric(c_df.iloc[:, 2], errors='coerce').fillna(0)
    
    # Display Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TOTAL LIABILITIES", f"${c_df['Balance'].sum():,.2f}")
    col2.metric("AVAILABLE CREDIT", f"${(c_df['Limit'].sum() - c_df['Balance'].sum()):,.2f}")
    
    latest_var = u_df['Variance'].iloc[-1] if not u_df.empty else 0
    col3.metric("LATEST VARIANCE", f"${latest_var:+,.2f}", delta_color="normal" if latest_var >= 0 else "inverse")
    
    total_mtd = u_df['Variance'].sum()
    col4.metric("MTD SURPLUS", f"${total_mtd:,.2f}")

    st.divider()
    
    # Visualizing the Edit results
    if not u_df.empty:
        fig = px.line(u_df, x=u_df.columns[0], y='Gross Earnings', title="Revenue Velocity", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
