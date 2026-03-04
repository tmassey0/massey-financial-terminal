import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="MASSEY CAPITAL | ARBITRAGE TERMINAL", layout="wide")

# --- 2. DATA ENGINE ---
@st.cache_data
def load_data():
    try:
        # File names from your GitHub repository 
        cards = pd.read_excel("Terrance Credit Card 1.xlsx", sheet_name="Credit Cards", skiprows=1)
        bills = pd.read_excel("Terrance Credit Card 1.xlsx", sheet_name="Bill Master List", skiprows=1)
        return cards, bills
    except:
        return None, None

cards_df, bills_df = load_data()

# --- 3. DAILY SWEEP CONTROLS ---
with st.sidebar:
    st.title("🏛️ SWEEP CONTROLS")
    st.divider()
    today_earnings = st.number_input("Today's Uber Earnings ($)", 0, 500, 150)
    st.info("Goal: Use daily earnings to sweep bill charges off credit cards.")

# --- 4. THE ARBITRAGE DASHBOARD ---
if cards_df is not None:
    # Logic: Identify bills currently on cards
    active_bills = bills_df[bills_df['Active'] == 'Yes']
    total_bill_load = active_bills['Amount'].sum()
    
    st.title("Massey Arbitrage & Sweep Terminal")
    
    # Header Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("TOTAL BILL LOAD", f"${total_bill_load:,.2f}", help="Total monthly expenses moved to cards")
    m2.metric("DAILY SWEEP TARGET", f"${(total_bill_load / 30):,.2f}", help="Amount needed per day to clear bills by month-end")
    
    sweep_progress = (today_earnings / (total_bill_load / 30)) * 100
    m3.metric("TODAY'S PROGRESS", f"{sweep_progress:.1f}%")

    st.divider()
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("💳 Current Card Exposure")
        # Showing where the bills are sitting
        st.dataframe(cards_df[['Bank Name', 'Total Current Balance', 'Credit Limit']], use_container_width=True)
        
    with col_b:
        st.subheader("📅 Bill-to-Card Mapping")
        # This tracks which bills are active and need to be swept
        st.dataframe(active_bills[['Bill Name', 'Amount', 'Due Day', 'Pay Via']], use_container_width=True)

    # --- THE VELOCITY TRACKER ---
    st.subheader("Monthly Sweep Velocity")
    # Visualization of your progress toward clearing the monthly bill load
    days = list(range(1, 31))
    target_line = [(total_bill_load / 30) * d for d in days]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=target_line, name="Required Sweep", line=dict(color="#38BDF8", dash='dash')))
    fig.update_layout(template="plotly_dark", xaxis_title="Day of Month", yaxis_title="Cumulative Payments ($)")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Awaiting Data Feed synchronization. Upload your Excel files to GitHub.")
