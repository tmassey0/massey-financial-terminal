import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. BRANDING & UI CONFIG ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

# Corporate "Dark Mode" Styling
st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
    .status-met { color: #00FFCC; font-weight: bold; }
    .status-short { color: #FF4B4B; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data
def load_data():
    try:
        cards = pd.read_excel("Terrance Credit Card 1.xlsx", sheet_name="Credit Cards", skiprows=1)
        # Using March as the active operational month
        uber = pd.read_excel("Terrance Uber Tracker.xlsx", sheet_name="March", skiprows=3)
        return cards, uber
    except:
        return None, None

cards_df, uber_df = load_data()

# --- 3. REVENUE & LIQUIDITY LOGIC ---
if uber_df is not None and cards_df is not None:
    # Clean Uber Data (Handling names based on your spreadsheet)
    uber_df.columns = [c.strip() for c in uber_df.columns]
    
    # CALCULATE REVENUE VELOCITY
    # Assuming columns: 'Date', 'Gross Earnings', 'Daily Goal'
    uber_df['Variance'] = uber_df['Gross Earnings'] - uber_df['Daily Goal']
    uber_df['Goal Met'] = uber_df['Variance'] >= 0
    
    # Portfolio Totals
    total_available = (cards_df['Credit Limit'] - cards_df['Total Current Balance']).sum()
    total_variance = uber_df['Variance'].sum()

# --- 4. THE COMMAND CENTER ---
if cards_df is not None:
    st.title("🏛️ Massey Strategic Capital Terminal")
    
    # TOP ROW: THE SCOREBOARD
    m1, m2, m3, m4 = st.columns(4)
    
    # Latest day performance
    latest_day = uber_df.iloc[-1]
    status_text = "🎯 GOAL MET" if latest_day['Goal Met'] else "📉 SHORTFALL"
    status_color = "normal" if latest_day['Goal Met'] else "inverse"
    
    m1.metric("LATEST GROSS", f"${latest_day['Gross Earnings']:,.2f}", 
              delta=f"{latest_day['Variance']:+,.2f}", delta_color=status_color)
    m2.metric("MTD VARIANCE", f"${total_variance:+,.2f}", help="Total performance vs. goals for the month")
    m3.metric("PORTFOLIO LIQUIDITY", f"${total_available:,.2f}", help="Total Available Credit")
    m4.metric("REVENUE STATUS", status_text)

    st.divider()

    # --- PERFORMANCE VISUALS ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📈 Revenue Velocity (Gross vs. Goal)")
        # Daily Performance Chart
        fig_perf = go.Figure()
        fig_perf.add_trace(go.Bar(x=uber_df['Date'], y=uber_df['Gross Earnings'], name="Actual Earnings", marker_color='#38BDF8'))
        fig_perf.add_trace(go.Scatter(x=uber_df['Date'], y=uber_df['Daily Goal'], name="Daily Goal", line=dict(color='#F97316', width=3, dash='dash')))
        fig_perf.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified")
        st.plotly_chart(fig_perf, use_container_width=True)

    with col_right:
        st.subheader("💳 Liquidity & Status")
        # Utilization & Available Credit Matrix
        cards_df['Available'] = cards_df['Credit Limit'] - cards_df['Total Current Balance']
        cards_df['Util %'] = (cards_df['Total Current Balance'] / cards_df['Credit Limit']) * 100
        
        # Display the Matrix
        st.dataframe(
            cards_df[['Bank Name', 'Available', 'Util %']].sort_values('Util %', ascending=False),
            use_container_width=True, hide_index=True
        )

    # --- THE LOG ---
    st.subheader("📅 Uber Performance Ledger")
    # Professional table with Goal Status
    def highlight_status(val):
        color = '#00FFCC' if val == True else '#FF4B4B'
        return f'color: {color}'

    styled_uber = uber_df[['Date', 'Gross Earnings', 'Daily Goal', 'Variance', 'Goal Met']].style.applymap(highlight_status, subset=['Goal Met']).format({'Gross Earnings': '${:,.2f}', 'Daily Goal': '${:,.2f}', 'Variance': '${:+,.2f}'})
    st.dataframe(styled_uber, use_container_width=True, hide_index=True)

else:
    st.error("⚠️ DATA SYNC FAILED: Ensure your Excel files are uploaded to GitHub.")
