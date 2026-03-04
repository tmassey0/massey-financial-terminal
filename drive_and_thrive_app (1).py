
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- SETTINGS & THEME ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL | PORTFOLIO TERMINAL", layout="wide")

st.markdown("""
    <style>
    html, body, [class*="st-at"] {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 20px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom: 2px solid #38BDF8 !important;
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- DATA ENGINE ---
def load_data():
    try:
        cards = pd.read_csv('Terrance Credit Card 1.xlsx - Credit Cards.csv', skiprows=1)
        bills = pd.read_csv('Terrance Credit Card 1.xlsx - Bill Master List.csv', skiprows=1)
        uber_summary = pd.read_csv('Terrance Uber Tracker.xlsx - Year Summary.csv', skiprows=2)
        uber_march = pd.read_csv('Terrance Uber Tracker.xlsx - March.csv', skiprows=3)
        return cards, bills, uber_summary, uber_march
    except:
        return None, None, None, None

cards_df, bills_df, summary_df, march_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("MASSEY CAPITAL")
    st.divider()
    target_daily = st.slider("Daily Revenue Target", 100, 300, 150)
    tax_reserve_pct = st.slider("Tax/Maint. Reserve (%)", 0, 30, 15)
    st.caption("Corporate Terminal v3.0")

# --- MAIN TERMINAL ---
if cards_df is not None:
    st.title("🏛️ Executive Financial Terminal")
    
    total_liabilities = cards_df['Total Current Balance'].sum()
    total_credit_limit = cards_df['Credit Limit'].sum()
    weighted_util = (total_liabilities / total_credit_limit) * 100
    monthly_burn = bills_df[bills_df['Active'] == 'Yes']['Amount'].sum()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOTAL LIABILITIES", f"${total_liabilities:,.2f}")
    m2.metric("AVG UTILIZATION", f"{weighted_util:.1f}%")
    m3.metric("MONTHLY BURN", f"${monthly_burn:,.2f}")
    m4.metric("TARGET APR", "35.9%", "High Interest Risk")

    st.divider()

    tabs = st.tabs(["📊 PERFORMANCE", "💳 LIABILITY MATRIX", "🛡️ RESERVES", "📅 OPERATIONS"])

    with tabs[0]:
        st.subheader("Revenue Velocity vs. Liability Reduction")
        fig = go.Figure()
        projection = [total_liabilities - (i * 1344) for i in range(5)]
        months = ['MAR', 'APR', 'MAY', 'JUN', 'JUL']
        fig.add_trace(go.Scatter(x=months, y=[max(0, p) for p in projection], 
                                 mode='lines+markers', name='Liabilities',
                                 line=dict(color='#0EA5E9', width=4),
                                 fill='tozeroy'))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        st.subheader("Credit Portfolio Analysis")
        cards_df['Util %'] = (cards_df['Total Current Balance'] / cards_df['Credit Limit']) * 100
        st.table(cards_df[['Bank Name', 'Total Current Balance', 'Credit Limit', 'Util %']])

    with tabs[2]:
        st.subheader("Tax & Operational Reserves")
        est_rev = target_daily * 30
        tax_reserve = est_rev * (tax_reserve_pct / 100)
        net_surplus = est_rev - tax_reserve - monthly_burn
        
        c1, c2, c3 = st.columns(3)
        c1.metric("EST. REVENUE", f"${est_rev:,.2f}")
        c2.metric("TAX/MAINT RESERVE", f"${tax_reserve:,.2f}")
        c3.metric("NET FOR DEBT", f"${max(0, net_surplus):,.2f}")

    with tabs[3]:
        st.subheader("Operational Calendar")
        st.dataframe(bills_df[bills_df['Active'] == 'Yes'].sort_values('Due Day')[['Bill Name', 'Amount', 'Due Day']])
else:
    st.error("Data Feeds Not Detected.")
