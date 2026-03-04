import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# --- 1. EXECUTIVE UI CONFIGURATION ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

# Custom Professional Theme
st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { 
        background-color: #161B22; 
        border: 1px solid #30363D; 
        border-radius: 10px; 
        padding: 20px !important; 
    }
    .stTabs [aria-selected="true"] { 
        color: #38BDF8 !important; 
        border-bottom: 2px solid #38BDF8 !important; 
    }
    .main-header { font-size: 2.5rem; font-weight: 700; color: #38BDF8; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.2rem; color: #94A3B8; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. THE "HYPER-CLEAN" DATA ENGINE ---
def force_numeric(series):
    """Aggressively converts values to numbers, stripping symbols and handling errors."""
    def clean_val(val):
        if pd.isna(val) or val == "" or str(val).strip() == "-": return 0.0
        cleaned = re.sub(r'[^0-9.\-]', '', str(val))
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    return series.apply(clean_val)

@st.cache_data
def load_and_sync_data():
    try:
        # Load all sheets to capture "Everything"
        cards = pd.read_excel("Terrance Credit Card 1.xlsx", sheet_name="Credit Cards", skiprows=1)
        bills = pd.read_excel("Terrance Credit Card 1.xlsx", sheet_name="Bill Master List", skiprows=1)
        uber = pd.read_excel("Terrance Uber Tracker.xlsx", sheet_name="March", skiprows=3)
        
        # Clean header spaces
        for df in [cards, bills, uber]:
            df.columns = [str(c).strip() for c in df.columns]
            
        return cards, bills, uber
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        return None, None, None

cards_raw, bills_raw, uber_raw = load_and_sync_data()

# --- 3. THE INTELLIGENCE LAYER ---
if cards_raw is not None and uber_raw is not None:
    # --- A. Credit Card Intelligence ---
    cards = cards_raw.copy()
    # Find key columns dynamically
    bal_col = next((c for c in cards.columns if "Balance" in c or "Current" in c), "Balance")
    limit_col = next((c for c in cards.columns if "Limit" in c), "Limit")
    
    # Force Numbers
    cards[bal_col] = force_numeric(cards[bal_col])
    cards[limit_col] = force_numeric(cards[limit_col])
    
    # Calculations
    cards['Available Credit'] = cards[limit_col] - cards[bal_col]
    cards['Utilization %'] = (cards[bal_col] / cards[limit_col].replace(0, 1)) * 100
    
    def set_status(u):
        if u >= 90: return "🔴 MAXED"
        if u > 30: return "🟡 OVER TARGET"
        return "🟢 HEALTHY"
    cards['Status'] = cards['Utilization %'].apply(set_status)

    # --- B. Uber Performance Intelligence ---
    uber = uber_raw.copy()
    earn_col = next((c for c in uber.columns if "Earnings" in c or "Gross" in c), "Gross Earnings")
    goal_col = next((c for c in uber.columns if "Goal" in c or "Target" in c), "Daily Goal")
    date_col = next((c for c in uber.columns if "Date" in c), "Date")

    uber[earn_col] = force_numeric(uber[earn_col])
    uber[goal_col] = force_numeric(uber[goal_col])
    uber['Variance'] = uber[earn_col] - uber[goal_col]
    uber['Goal Status'] = uber['Variance'].apply(lambda x: "🎯 MET" if x >= 0 else "📉 SHORT")

# --- 4. THE COMMAND CENTER ---
if cards_raw is not None:
    st.markdown('<div class="main-header">🏛️ Massey Strategic Capital</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Consolidated Financial & Operational Terminal</div>', unsafe_allow_html=True)

    # TOP LINE METRICS
    m1, m2, m3, m4 = st.columns(4)
    total_avail = cards['Available Credit'].sum()
    total_util = (cards[bal_col].sum() / cards[limit_col].sum()) * 100
    mtd_variance = uber['Variance'].sum()
    
    m1.metric("TOTAL LIQUIDITY", f"${total_avail:,.2f}", help="Total Available Credit across all cards")
    m2.metric("AVG UTILIZATION", f"{total_util:.1f}%")
    m3.metric("UBER MTD VARIANCE", f"${mtd_variance:+,.2f}", delta_color="normal" if mtd_variance >= 0 else "inverse")
    m4.metric("ACTIVE BILL LOAD", f"${bills_raw[bills_raw['Active']=='Yes']['Amount'].sum():,.2f}")

    st.divider()

    # --- TABS FOR EVERYTHING ---
    tabs = st.tabs(["💳 CREDIT PORTFOLIO", "📈 UBER PERFORMANCE", "📅 BILL MASTER LIST"])

    with tabs[0]:
        st.subheader("Total Card Liquidity & Utilization Status")
        # Visual Heatmap
        fig_util = px.bar(
            cards.sort_values('Utilization %', ascending=False),
            x='Bank Name', y='Utilization %', text='Utilization %',
            color='Utilization %', color_continuous_scale=['#00FFCC', '#F97316', '#FF4B4B'],
            range_color=[0, 100]
        )
        fig_util.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_util.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_util, use_container_width=True)

        # The Table with "Everything"
        st.write("### Detailed Liability Matrix")
        st.dataframe(
            cards[['Bank Name', 'Status', bal_col, limit_col, 'Available Credit', 'Utilization %', 'APR', 'Due Day']]
            .sort_values('Utilization %', ascending=False)
            .style.format({'Utilization %': '{:.1f}%', bal_col: '${:,.2f}', limit_col: '${:,.2f}', 'Available Credit': '${:,.2f}'}),
            use_container_width=True, hide_index=True
        )

    with tabs[1]:
        st.subheader("Daily Revenue Velocity vs. Goal")
        # Daily Chart
        fig_uber = go.Figure()
        fig_uber.add_trace(go.Bar(x=uber[date_col], y=uber[earn_col], name="Earnings", marker_color='#38BDF8'))
        fig_uber.add_trace(go.Scatter(x=uber[date_col], y=uber[goal_col], name="Goal", line=dict(color='#F97316', dash='dash', width=3)))
        fig_uber.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_uber, use_container_width=True)

        st.write("### Uber Performance Ledger")
        st.dataframe(
            uber[[date_col, earn_col, goal_col, 'Variance', 'Goal Status']]
            .style.format({earn_col: '${:,.2f}', goal_col: '${:,.2f}', 'Variance': '${:+,.2f}'}),
            use_container_width=True, hide_index=True
        )

    with tabs[2]:
        st.subheader("Master Bill Schedule (Arbitrage Load)")
        active_only = st.checkbox("Show Only Active Bills", value=True)
        display_bills = bills_raw[bills_raw['Active'] == 'Yes'] if active_only else bills_raw
        
        st.dataframe(
            display_bills.sort_values('Due Day'),
            use_container_width=True, hide_index=True
        )
else:
    st.info("Awaiting Data Feed Synchronization. Ensure Excel files are uploaded to GitHub.")
