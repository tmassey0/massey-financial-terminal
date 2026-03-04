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

# --- 2. DATA CLEANING UTILITY ---
def clean_currency(column):
    """Removes $, commas, and converts to numeric, handling errors gracefully."""
    return pd.to_numeric(column.replace('[\$,]', '', regex=True), errors='coerce').fillna(0)

# --- 3. THE DATA ENGINE ---
@st.cache_data
def load_data():
    try:
        cards = pd.read_excel("Terrance Credit Card 1.xlsx", sheet_name="Credit Cards", skiprows=1)
        uber = pd.read_excel("Terrance Uber Tracker.xlsx", sheet_name="March", skiprows=3)
        
        # Strip spaces from column names
        cards.columns = [str(c).strip() for c in cards.columns]
        uber.columns = [str(c).strip() for c in uber.columns]
        
        return cards, uber
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        return None, None

cards_df, uber_df = load_data()

# --- 4. ROBUST MAPPING & CONVERSION ---
if cards_df is not None and uber_df is not None:
    # Identify key columns using fuzzy search
    earn_col = next((c for c in uber_df.columns if "Earnings" in c or "Gross" in c), None)
    goal_col = next((c for c in uber_df.columns if "Goal" in c or "Target" in c), None)
    date_col = next((c for c in uber_df.columns if "Date" in c or "Day" in c), None)
    
    bal_col = next((c for c in cards_df.columns if "Balance" in c or "Current" in c), None)
    limit_col = next((c for c in cards_df.columns if "Limit" in c), None)

    if earn_col and goal_col:
        # SCRUB THE DATA: Force numeric conversion to stop the TypeError
        uber_df[earn_col] = clean_currency(uber_df[earn_col].astype(str))
        uber_df[goal_col] = clean_currency(uber_df[goal_col].astype(str))
        
        # Calculate Variance (+/-) and Status
        uber_df['Variance'] = uber_df[earn_col] - uber_df[goal_col]
        uber_df['Goal Met'] = uber_df['Variance'] >= 0

    if bal_col and limit_col:
        # Scrub Card Data
        cards_df[bal_col] = clean_currency(cards_df[bal_col].astype(str))
        cards_df[limit_col] = clean_currency(cards_df[limit_col].astype(str))
        
        # Auto-calculate Available Credit & Utilization
        cards_df['Available Credit'] = cards_df[limit_col] - cards_df[bal_col]
        cards_df['Util %'] = (cards_df[bal_col] / cards_df[limit_col]) * 100
        
        def set_status(u):
            if u > 90: return "🔴 MAXED"
            if u > 30: return "🟡 OVER TARGET"
            return "🟢 HEALTHY"
        cards_df['Status'] = cards_df['Util %'].apply(set_status)

# --- 5. THE COMMAND CENTER ---
if cards_df is not None and uber_df is not None:
    st.title("🏛️ Massey Strategic Capital Terminal")
    
    # Portfolio Scoreboard
    m1, m2, m3, m4 = st.columns(4)
    latest = uber_df.iloc[-1]
    m1.metric("LATEST GROSS", f"${latest[earn_col]:,.2f}", delta=f"{latest['Variance']:+,.2f}")
    m2.metric("MTD VARIANCE", f"${uber_df['Variance'].sum():+,.2f}")
    m3.metric("PORTFOLIO LIQUIDITY", f"${cards_df['Available Credit'].sum():,.2f}")
    m4.metric("GLOBAL UTILIZATION", f"{(cards_df[bal_col].sum() / cards_df[limit_col].sum())*100:.1f}%")

    st.divider()

    t1, t2 = st.tabs(["📊 REVENUE PERFORMANCE", "💳 LIQUIDITY MATRIX"])
    
    with t1:
        # Performance Graph
        fig = go.Figure()
        fig.add_trace(go.Bar(x=uber_df[date_col], y=uber_df[earn_col], name="Actual", marker_color='#38BDF8'))
        fig.add_trace(go.Scatter(x=uber_df[date_col], y=uber_df[goal_col], name="Goal", line=dict(color='#F97316', dash='dash')))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        # Card Matrix with Status & Available Credit
        st.dataframe(
            cards_df[['Bank Name', 'Status', bal_col, limit_col, 'Available Credit', 'Util %']]
            .sort_values('Util %', ascending=False)
            .style.format({'Util %': '{:.1f}%', bal_col: '${:,.2f}', limit_col: '${:,.2f}', 'Available Credit': '${:,.2f}'}),
            use_container_width=True, hide_index=True
        )
else:
    st.info("Awaiting Data Feed synchronization...")
