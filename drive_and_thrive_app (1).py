import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# --- 1. BRANDING & UI CONFIG ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. ADVANCED DATA SCRUBBING ---
def force_numeric(series):
    """Aggressively converts a series to numeric, stripping all non-digit characters except decimals."""
    def clean_val(val):
        if pd.isna(val): return 0
        # Remove anything that isn't a digit, a period, or a minus sign
        cleaned = re.sub(r'[^0-9.\-]', '', str(val))
        try:
            return float(cleaned) if cleaned else 0
        except ValueError:
            return 0
    return series.apply(clean_val)

# --- 3. THE DATA ENGINE ---
@st.cache_data
def load_data():
    try:
        # File paths must match your GitHub uploads
        cards = pd.read_excel("Terrance Credit Card 1.xlsx", sheet_name="Credit Cards", skiprows=1)
        uber = pd.read_excel("Terrance Uber Tracker.xlsx", sheet_name="March", skiprows=3)
        
        # Normalize column names
        cards.columns = [str(c).strip() for c in cards.columns]
        uber.columns = [str(c).strip() for c in uber.columns]
        
        return cards, uber
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        return None, None

cards_df, uber_df = load_data()

# --- 4. ROBUST LOGIC & STATUS CALCULATIONS ---
if cards_df is not None and uber_df is not None:
    # Fuzzy Search for Columns
    earn_col = next((c for c in uber_df.columns if "Earnings" in c or "Gross" in c), None)
    goal_col = next((c for c in uber_df.columns if "Goal" in c or "Target" in c), None)
    date_col = next((c for c in uber_df.columns if "Date" in c or "Day" in c), None)
    
    bal_col = next((c for c in cards_df.columns if "Balance" in c or "Current" in c), None)
    limit_col = next((c for c in cards_df.columns if "Limit" in c), None)

    # 4A. Clean Uber Data & Calculate Variance
    if earn_col and goal_col:
        uber_df[earn_col] = force_numeric(uber_df[earn_col])
        uber_df[goal_col] = force_numeric(uber_df[goal_col])
        uber_df['Variance'] = uber_df[earn_col] - uber_df[goal_col]
        uber_df['Goal Met'] = uber_df['Variance'] >= 0

    # 4B. Clean Card Data & Calculate Liquidity/Status
    if bal_col and limit_col:
        cards_df[bal_col] = force_numeric(cards_df[bal_col])
        cards_df[limit_col] = force_numeric(cards_df[limit_col])
        
        # Auto-Calculations
        cards_df['Available Credit'] = cards_df[limit_col] - cards_df[bal_col]
        # Avoid division by zero
        cards_df['Util %'] = (cards_df[bal_col] / cards_df[limit_col].replace(0, 1)) * 100
        
        def set_status(u):
            if u >= 90: return "🔴 MAXED"
            if u > 30: return "🟡 OVER TARGET"
            return "🟢 HEALTHY"
        cards_df['Status'] = cards_df['Util %'].apply(set_status)

# --- 5. THE COMMAND CENTER ---
if cards_df is not None and uber_df is not None:
    st.title("🏛️ Massey Strategic Capital Terminal")
    
    # Portfolio Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    latest = uber_df[uber_df[earn_col] > 0].iloc[-1] if not uber_df[uber_df[earn_col] > 0].empty else uber_df.iloc[-1]
    
    m1.metric("LATEST GROSS", f"${latest[earn_col]:,.2f}", delta=f"{latest['Variance']:+,.2f}")
    m2.metric("MTD VARIANCE", f"${uber_df['Variance'].sum():+,.2f}")
    m3.metric("TOTAL AVAILABLE CREDIT", f"${cards_df['Available Credit'].sum():,.2f}")
    m4.metric("GLOBAL UTILIZATION", f"{(cards_df[bal_col].sum() / cards_df[limit_col].replace(0,1).sum())*100:.1f}%")

    st.divider()

    t1, t2 = st.tabs(["📊 REVENUE VELOCITY", "💳 LIQUIDITY MATRIX"])
    
    with t1:
        # Performance Graph (Earnings vs Goal)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=uber_df[date_col], y=uber_df[earn_col], name="Actual", marker_color='#38BDF8'))
        fig.add_trace(go.Scatter(x=uber_df[date_col], y=uber_df[goal_col], name="Goal", line=dict(color='#F97316', dash='dash', width=3)))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        # Enhanced Table with Status & Auto-Available Credit
        st.dataframe(
            cards_df[['Bank Name', 'Status', bal_col, limit_col, 'Available Credit', 'Util %']]
            .sort_values('Util %', ascending=False)
            .style.format({'Util %': '{:.1f}%', bal_col: '${:,.2f}', limit_col: '${:,.2f}', 'Available Credit': '${:,.2f}'}),
            use_container_width=True, hide_index=True
        )
else:
    st.info("Awaiting Data Feed synchronization...")
