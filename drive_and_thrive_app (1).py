import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SETTINGS & THEME ---
# Standard Fortune 500 branding setup
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

# Simplified CSS to avoid TypeError and IndentationErrors
css = """
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
    .stTabs [aria-selected="true"] { color: #38BDF8 !important; border-bottom: 2px solid #38BDF8 !important; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data
def load_data():
    try:
        # UPDATED: Using the exact filenames from your directory
        cards = pd.read_csv('Terrance Credit Card 1.xlsx - Credit Cards.csv', skiprows=1)
        bills = pd.read_csv('Terrance Credit Card 1.xlsx - Bill Master List.csv', skiprows=1)
        uber_march = pd.read_csv('Terrance Uber Tracker.xlsx - March.csv', skiprows=3)
        return cards, bills, uber_march
    except FileNotFoundError as e:
        st.error(f"🔍 File Missing: {e.filename}. Please ensure this exact file is uploaded to GitHub.")
        return None, None, None
    except Exception as e:
        st.error(f"⚠️ System Error: {e}")
        return None, None, None

cards_df, bills_df, march_df = load_data()

# --- 3. SIDEBAR: EXECUTIVE CONTROLS ---
with st.sidebar:
    st.title("MASSEY CAPITAL")
    st.divider()
    st.subheader("Operational Controls")
    target_daily = st.slider("Daily Revenue Target ($)", 100, 300, 150)
    tax_reserve_pct = st.slider("Tax/Maint. Reserve (%)", 0, 30, 15)
    st.divider()
    st.caption("Terminal v3.2 | Corporate Edition")

# --- 4. MAIN TERMINAL ---
if cards_df is not None:
    st.title("🏛️ Executive Financial Terminal")
    st.markdown("##### Portfolio Monitoring & Liquidity Optimization")
    
    # Financial Calculations
    total_liabilities = cards_df['Total Current Balance'].sum()
    total_limit = cards_df['Credit Limit'].sum()
    utilization = (total_liabilities / total_limit) * 100
    monthly_burn = bills_df[bills_df['Active'] == 'Yes']['Amount'].sum()
    
    # KPI Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOTAL LIABILITIES", f"${total_liabilities:,.2f}")
    m2.metric("AVG UTILIZATION", f"{utilization:.1f}%")
    m3.metric("MONTHLY BURN", f"${monthly_burn:,.2f}")
    m4.metric("HIGH APR RISK", "35.9%")

    st.divider()

    tabs = st.tabs(["📊 PERFORMANCE", "💳 LIABILITY MATRIX", "🛡️ RESERVES", "📅 OPERATIONS"])

    with tabs[0]:
        st.subheader("Revenue Velocity vs. Liability Reduction")
        # Payoff projection based on current surplus
        projection = [total_liabilities - (i * 1344) for i in range(5)]
        months = ['MAR', 'APR', 'MAY', 'JUN', 'JUL']
        fig = go.Figure(go.Scatter(x=months, y=[max(0, p) for p in projection], 
                                 mode='lines+markers', name='Liabilities',
                                 line=dict(color='#0EA5E9', width=4), fill='tozeroy'))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("Credit Portfolio Analysis")
        cards_df['Util %'] = (cards_df['Total Current Balance'] / cards_df['Credit Limit']) * 100
        st.table(cards_df[['Bank Name', 'Total Current Balance', 'Credit Limit', 'Util %']])

    with tabs[2]:
        st.subheader("Tax & Operational Reserves")
        est_rev = target_daily * 30
        tax_res = est_rev * (tax_reserve_pct / 100)
        net_surplus = est_rev - tax_res - monthly_burn
        
        r1, r2, r3 = st.columns(3)
        r1.metric("EST. REVENUE", f"${est_rev:,.2f}")
        r2.metric("TAX/MAINT RESERVE", f"${tax_res:,.2f}")
        r3.metric("NET FOR DEBT", f"${max(0, net_surplus):,.2f}")

    with tabs[3]:
        st.subheader("Operational Calendar")
        st.dataframe(bills_df[bills_df['Active'] == 'Yes'].sort_values('Due Day')[['Bill Name', 'Amount', 'Due Day']])
else:
    st.warning("Data feeds not found. Verify your CSV files are uploaded to GitHub.")
