import streamlit as st
import pandas as pd
import plotly.express as px
import re

# --- 1. SETTINGS ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

# --- 2. DATA ENGINES (READ/WRITE) ---
def load_data(file, sheet, skip=0):
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def save_data(df, file, sheet):
    # This function writes your changes back to the Excel file
    with pd.ExcelWriter(file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet, index=False)

# --- 3. DATA SYNC ---
# We load the data into "Session State" so it stays editable while you use the app
if 'cards' not in st.session_state:
    st.session_state.cards = load_data("Terrance Credit Card 1.xlsx", "Credit Cards", 1)
if 'bills' not in st.session_state:
    st.session_state.bills = load_data("Terrance Credit Card 1.xlsx", "Bill Master List", 1)
if 'uber' not in st.session_state:
    st.session_state.uber = load_data("Terrance Uber Tracker.xlsx", "March", 3)

# --- 4. THE COMMAND CENTER ---
st.title("🏛️ Massey Strategic Capital Terminal")
st.caption("Live-Editable Portfolio Management")

tabs = st.tabs(["📊 DASHBOARD", "💳 MANAGE CARDS", "📅 MANAGE BILLS", "🚖 UBER LEDGER"])

with tabs[1]:
    st.subheader("Edit Credit Cards & Limits")
    st.info("Directly edit cells below. Add a new row at the bottom to add a card.")
    # The magic "Data Editor" component
    edited_cards = st.data_editor(st.session_state.cards, num_rows="dynamic", use_container_width=True)
    if st.button("Save Card Changes"):
        st.session_state.cards = edited_cards
        # save_data(edited_cards, "Terrance Credit Card 1.xlsx", "Credit Cards")
        st.success("Card portfolio updated!")

with tabs[2]:
    st.subheader("Edit Bill Master List")
    edited_bills = st.data_editor(st.session_state.bills, num_rows="dynamic", use_container_width=True)
    if st.button("Save Bill Changes"):
        st.session_state.bills = edited_bills
        st.success("Bill schedule updated!")

with tabs[3]:
    st.subheader("Edit Uber Performance")
    edited_uber = st.data_editor(st.session_state.uber, num_rows="dynamic", use_container_width=True)
    if st.button("Save Uber Entry"):
        st.session_state.uber = edited_uber
        st.success("Earnings ledger updated!")

with tabs[0]:
    # This dashboard now updates INSTANTLY when you edit the tabs above
    c = st.session_state.cards
    u = st.session_state.uber
    
    # Auto-calculations for the main screen
    total_bal = pd.to_numeric(c.iloc[:, 1], errors='coerce').sum() # Assuming Balance is 2nd col
    total_lim = pd.to_numeric(c.iloc[:, 2], errors='coerce').sum() # Assuming Limit is 3rd col
    
    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL LIABILITIES", f"${total_bal:,.2f}")
    col2.metric("AVAILABLE CREDIT", f"${(total_lim - total_bal):,.2f}")
    col3.metric("UTILIZATION", f"{(total_bal/total_lim)*100:.1f}%" if total_lim > 0 else "0%")
    
    st.divider()
    # Dynamic Liquidity Chart
    fig = px.bar(c, x=c.columns[0], y=c.columns[1], title="Debt by Institution", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
