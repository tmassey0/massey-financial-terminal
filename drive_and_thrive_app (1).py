import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. BRANDING & UI CONFIG ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

# Fortune 500 Global Styling
st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
    .stTabs [aria-selected="true"] { color: #38BDF8 !important; border-bottom: 2px solid #38BDF8 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA LOAD ENGINE (With Diagnostics) ---
@st.cache_data
def load_data():
    # These must match your GitHub filenames EXACTLY
    FILE_CC = "Terrance Credit Card 1.xlsx - Credit Cards.csv"
    FILE_BILLS = "Terrance Credit Card 1.xlsx - Bill Master List.csv"
    FILE_UBER = "Terrance Uber Tracker.xlsx - March.csv"
    
    try:
        cards = pd.read_csv(FILE_CC, skiprows=1)
        bills = pd.read_csv(FILE_BILLS, skiprows=1)
        uber = pd.read_csv(FILE_UBER, skiprows=3)
        return cards, bills, uber
    except FileNotFoundError:
        st.error("🏛️ **SYSTEM ALERT: Data Feed Not Found**")
        st.info("The app is looking for your files but cannot find them. Please check the 'File Diagnostic' below.")
        
        # Self-Healing Diagnostic: List all files currently on the server
        with st.expander("🔍 File Diagnostic (Click to see what the app sees)"):
            all_files = os.listdir(".")
            st.write("Files currently in your GitHub repository:")
            st.code(all_files)
            st.write(f"Looking for: `{FILE_CC}`")
        return None, None, None

cards_df, bills_df, march_df = load_data()

# --- 3. EXECUTIVE SIDEBAR ---
with st.sidebar:
    st.title("MASSEY CAPITAL")
    st.divider()
    st.subheader("Liquidity Parameters")
    target_daily = st.slider("Daily Uber Revenue Goal ($)", 100, 300, 150)
    tax_reserve_pct = st.slider("Tax/Maint. Reserve (%)", 0, 30, 15)
    st.divider()
    st.caption("Terminal v3.5 | Professional Edition")

# --- 4. THE COMMAND CENTER ---
if cards_df is not None:
    st.title("🏛️ Executive Financial Terminal")
    
    # Financial KPI Logic
    total_debt = cards_df['Total Current Balance'].sum()
    total_limit = cards_df['Credit Limit'].sum()
    utilization = (total_debt / total_limit) * 100
    monthly_burn = bills_df[bills_df['Active'] == 'Yes']['Amount'].sum()
    
    # Metrics Bar
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOTAL LIABILITIES", f"${total_debt:,.2f}")
    m2.metric("AVG UTILIZATION", f"{utilization:.1f}%")
    m3.metric("MONTHLY BURN", f"${monthly_burn:,.2f}")
    m4.metric("STRATEGY", "Avalanche", "High Interest Focus")

    st.divider()

    tabs = st.tabs(["📈 PERFORMANCE", "🛡️ RESERVES", "📅 OPERATIONS"])

    with tabs[0]:
        st.subheader("Revenue Velocity vs. Liability Reduction")
        # Payoff projection (Approximation based on $1,344 surplus)
        proj_vals = [total_debt - (i * 1344) for i in range(5)]
        months = ['MAR', 'APR', 'MAY', 'JUN', 'JUL']
        fig = go.Figure(go.Scatter(x=months, y=[max(0, p) for p in proj_vals], 
                                 mode='lines+markers', line=dict(color='#0EA5E9', width=4), fill='tozeroy'))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("Cash Reserve Management")
        est_rev = target_daily * 30
        tax_res = est_rev * (tax_reserve_pct / 100)
        net_surplus = est_rev - tax_res - monthly_burn
        
        r1, r2, r3 = st.columns(3)
        r1.metric("EST. MONTHLY REV", f"${est_rev:,.2f}")
        r2.metric("TAX/MAINT RESERVE", f"${tax_res:,.2f}")
        r3.metric("NET FOR DEBT", f"${max(0, net_surplus):,.2f}")
        st.caption(f"Note: Setting aside {tax_reserve_pct}% covers self-employment taxes and vehicle upkeep.")

    with tabs[2]:
        st.subheader("Tactical Bill Schedule")
        active_bills = bills_df[bills_df['Active'] == 'Yes'].sort_values('Due Day')
        st.dataframe(active_bills[['Bill Name', 'Amount', 'Due Day', 'Pay Via']], use_container_width=True)

else:
    st.warning("Awaiting Data Feed synchronization...")
