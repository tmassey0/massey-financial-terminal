import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. BRANDING & UI CONFIG ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA LOAD ENGINE ---
def load_data(file, sheet, skip):
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        # If file is missing, we create the exact structure you need
        return pd.DataFrame(columns=["Date", "Day", "Hours Worked", "Gross Earnings", "Daily Goal"])

# --- 3. PERSISTENT SESSION STATE ---
if 'cards' not in st.session_state:
    st.session_state.cards = load_data("Terrance Credit Card 1.xlsx", "Credit Cards", 1)
if 'bills' not in st.session_state:
    st.session_state.bills = load_data("Terrance Credit Card 1.xlsx", "Bill Master List", 1)
if 'uber' not in st.session_state:
    st.session_state.uber = load_data("Terrance Uber Tracker.xlsx", "March", 3)

# --- 4. THE COMMAND CENTER (YOUR SPECIFIC ORDER) ---
st.title("🏛️ Massey Strategic Capital Terminal")

tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS & LIQUIDITY", "📅 BILL MASTER", "🚖 UBER PERFORMANCE"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    c = st.session_state.cards
    u = st.session_state.uber
    
    # Dynamic Math for Metrics
    bal_col = next((col for col in c.columns if 'Balance' in col), None)
    lim_col = next((col for col in c.columns if 'Limit' in col), None)
    
    m1, m2, m3 = st.columns(3)
    if bal_col and lim_col and not c.empty:
        total_bal = pd.to_numeric(c[bal_col], errors='coerce').sum()
        total_lim = pd.to_numeric(c[lim_col], errors='coerce').sum()
        m1.metric("TOTAL LIABILITIES", f"${total_bal:,.2f}")
        m2.metric("AVAILABLE CREDIT", f"${(total_lim - total_bal):,.2f}")
        m3.metric("PORTFOLIO UTILIZATION", f"{(total_bal/total_lim)*100:.1f}%" if total_lim > 0 else "0%")
    
    st.divider()
    st.subheader("Revenue Velocity")
    earn_col = next((col for col in u.columns if 'Earnings' in col), None)
    if earn_col and not u.empty:
        u_clean = u.copy()
        u_clean[earn_col] = pd.to_numeric(u_clean[earn_col], errors='coerce').fillna(0)
        fig = px.bar(u_clean, x=u_clean.columns[0], y=earn_col, template="plotly_dark", color_discrete_sequence=['#38BDF8'])
        st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: CARDS & LIQUIDITY ---
with tabs[1]:
    st.subheader("Manage Credit Card Portfolio")
    edited_cards = st.data_editor(
        st.session_state.cards,
        num_rows="dynamic",
        use_container_width=True,
        key="cards_editor_v6"
    )
    if st.button("💾 Save Portfolio Updates"):
        st.session_state.cards = edited_cards
        st.success("Card data updated!")

# --- TAB 3: BILL MASTER ---
with tabs[2]:
    st.subheader("Monthly Burn List")
    edited_bills = st.data_editor(
        st.session_state.bills,
        num_rows="dynamic",
        use_container_width=True,
        key="bills_editor_v6"
    )
    if st.button("💾 Save Bill Schedule"):
        st.session_state.bills = edited_bills
        st.success("Bills updated!")

# --- TAB 4: UBER PERFORMANCE (FORCED EDITING) ---
with tabs[3]:
    st.subheader("Daily Earnings & Hours Entry")
    st.info("Instructions: Double-click ANY cell (Hours, Earnings, etc.) to edit. Use the (+) at the bottom for new rows.")
    
    # We explicitly tell Streamlit that these columns should be editable numbers/text
    # This prevents the "locking" behavior you were seeing
    edited_uber = st.data_editor(
        st.session_state.uber,
        num_rows="dynamic",
        use_container_width=True,
        key="uber_editor_v6",
        column_config={
            "Hours Worked": st.column_config.NumberColumn("Hours", format="%.2f"),
            "Gross Earnings": st.column_config.NumberColumn("Earnings ($)", format="$%.2f"),
            "Daily Goal": st.column_config.NumberColumn("Goal ($)", format="$%.2f"),
            "Difference": st.column_config.NumberColumn("Diff ($)", format="$%.2f", disabled=False)
        }
    )
    
    if st.button("💾 Commit Uber Performance"):
        # Before saving, we calculate the Difference automatically for you
        if "Gross Earnings" in edited_uber.columns and "Daily Goal" in edited_uber.columns:
            e = pd.to_numeric(edited_uber["Gross Earnings"], errors='coerce').fillna(0)
            g = pd.to_numeric(edited_uber["Daily Goal"], errors='coerce').fillna(0)
            edited_uber["Difference"] = e - g
            
        st.session_state.uber = edited_uber
        st.success("Uber ledger updated and Difference calculated!")
