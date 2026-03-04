import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. BRANDING & UI CONFIG ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. THE DATA ENGINE (SMART VERSION) ---
@st.cache_data
def load_data():
    try:
        # Load Files
        cards = pd.read_excel("Terrance Credit Card 1.xlsx", sheet_name="Credit Cards", skiprows=1)
        
        # We try to load Uber with flexible header detection
        uber = pd.read_excel("Terrance Uber Tracker.xlsx", sheet_name="March", skiprows=3)
        
        # CLEANING: Remove extra spaces from column names
        uber.columns = [str(c).strip() for c in uber.columns]
        cards.columns = [str(c).strip() for c in cards.columns]
        
        return cards, uber
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        return None, None

cards_df, uber_df = load_data()

# --- 3. DYNAMIC COLUMN MAPPING ---
# This part fixes the KeyError by looking for the right columns automatically
if uber_df is not None:
    # Look for the Earnings column
    earnings_col = next((c for c in uber_df.columns if "Earnings" in c or "Gross" in c), None)
    # Look for the Goal column
    goal_col = next((c for c in uber_df.columns if "Goal" in c or "Target" in c), None)
    # Look for the Date column
    date_col = next((c for c in uber_df.columns if "Date" in c or "Day" in c), None)

    if not earnings_col or not goal_col:
        st.warning("🔎 **Column Mismatch Detected**")
        st.write("The app couldn't find 'Gross Earnings' or 'Daily Goal'. Here is what it found instead:")
        st.code(list(uber_df.columns))
        st.stop() # Stops the app here so you can see the diagnostic
    
    # Perform Calculations using the found columns
    uber_df['Variance'] = uber_df[earnings_col] - uber_df[goal_col]
    uber_df['Goal Met'] = uber_df['Variance'] >= 0

# --- 4. THE COMMAND CENTER ---
if cards_df is not None and uber_df is not None:
    st.title("🏛️ Massey Strategic Capital Terminal")
    
    # Portfolio Totals
    cards_df['Available'] = cards_df['Credit Limit'] - cards_df['Total Current Balance']
    total_available = cards_df['Available'].sum()
    total_variance = uber_df['Variance'].sum()
    
    # Latest day performance
    latest_day = uber_df.iloc[-1]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("LATEST GROSS", f"${latest_day[earnings_col]:,.2f}", 
              delta=f"{latest_day['Variance']:+,.2f}")
    m2.metric("MTD VARIANCE", f"${total_variance:+,.2f}")
    m3.metric("PORTFOLIO LIQUIDITY", f"${total_available:,.2f}")
    m4.metric("STATUS", "🎯 MET" if latest_day['Goal Met'] else "📉 SHORT")

    st.divider()

    # Performance Graph
    fig = go.Figure()
    fig.add_trace(go.Bar(x=uber_df[date_col], y=uber_df[earnings_col], name="Earnings", marker_color='#38BDF8'))
    fig.add_trace(go.Scatter(x=uber_df[date_col], y=uber_df[goal_col], name="Goal", line=dict(color='#F97316', width=3, dash='dash')))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # Utilization Table
    st.subheader("💳 Credit Utilization & Available Liquidity")
    cards_df['Util %'] = (cards_df['Total Current Balance'] / cards_df['Credit Limit']) * 100
    st.dataframe(cards_df[['Bank Name', 'Available', 'Util %']].sort_values('Util %', ascending=False), use_container_width=True)

else:
    st.info("Awaiting Data Feed Synchronization...")
