import streamlit as st
import pandas as pd
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="STRATEGIC CAPITAL TERMINAL", layout="wide")

# --- INITIALIZE SESSION STATE WITH SAMPLE DATA ---
if 'cards_df' not in st.session_state:
    st.session_state.cards_df = pd.DataFrame({
        'Card': ['Card1', 'Card2', 'Card3', 'Card4', 'Card5'],
        'Bank': ['Navy Federal', 'Indigo 3069', 'Indigo 1448', 'Milestone 5093', 'Destiny 3992'],
        'Limit': [1500, 500, 1000, 500, 1000],
        'Balance': [1500.10, 632.81, 599.40, 489.81, 944.27]
    })

if 'bills_df' not in st.session_state:
    st.session_state.bills_df = pd.DataFrame({
        'Bill Name': ['Storage 1', 'Storage 2', 'Storage 3', 'Storage 4', 'Intuit', 'Cell Phone'],
        'Amount': [478, 109, 180, 98, 75, 80],
        'Due Day': [1, 1, 1, 1, 20, 5],
        'Pay Via': ['Card1', 'Card1', 'Card2', 'Card2', 'Card2', 'Card3']
    })

if 'revenue_df' not in st.session_state:
    data = {
        'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'Date': ['2026-03-02', '2026-03-03', '2026-03-04', '2026-03-05', '2026-03-06', '2026-03-07', '2026-03-08'],
        'Hours': [8.53, 0, 0, 0, 0, 0, 0],
        'Earnings': [224.70, 0, 0, 0, 0, 0, 0],
        'Goal': [150, 150, 150, 150, 150, 150, 150]
    }
    df = pd.DataFrame(data)
    df['Difference'] = df['Earnings'] - df['Goal']
    df['Status'] = df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
    st.session_state.revenue_df = df
    st.session_state.revenue_history = []

# --- MAIN APP ---
st.title("🏛️ Strategic Capital Terminal")

# Create tabs
tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS", "📅 BILLS", "💰 REVENUE"])

# --- DASHBOARD TAB ---
with tabs[0]:
    st.header("Financial Dashboard")
    
    # Overview Section
    st.subheader("📈 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    total_limit = st.session_state.cards_df['Limit'].sum()
    total_balance = st.session_state.cards_df['Balance'].sum()
    available = total_limit - total_balance
    utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
    
    col1.metric("Total Credit Limit", f"${total_limit:,.2f}")
    col2.metric("Total Balance", f"${total_balance:,.2f}")
    col3.metric("Available Credit", f"${available:,.2f}")
    col4.metric("Utilization", f"{utilization:.1f}%")
    
    # Revenue Section
    st.subheader("🚖 Revenue")
    col1, col2, col3, col4 = st.columns(4)
    
    total_hours = st.session_state.revenue_df['Hours'].sum()
    total_earnings = st.session_state.revenue_df['Earnings'].sum()
    total_goal = st.session_state.revenue_df['Goal'].sum()
    avg_hourly = total_earnings / total_hours if total_hours > 0 else 0
    
    col1.metric("Total Hours", f"{total_hours:.2f}")
    col2.metric("Total Earnings", f"${total_earnings:,.2f}")
    col3.metric("Goal vs Actual", f"${total_earnings - total_goal:,.2f}")
    col4.metric("Avg Hourly", f"${avg_hourly:.2f}")
    
    # Bills Section
    st.subheader("📋 Bills")
    col1, col2, col3 = st.columns(3)
    
    total_bills = st.session_state.bills_df['Amount'].sum()
    col1.metric("Total Bills", f"${total_bills:,.2f}")
    col2.metric("# of Bills", f"{len(st.session_state.bills_df)}")
    col3.metric("Avg Bill", f"${total_bills/len(st.session_state.bills_df):,.2f}")
    
    # Cash Flow
    st.subheader("💰 Cash Flow")
    col1, col2, col3 = st.columns(3)
    
    net_cash = total_earnings - total_bills
    col1.metric("Monthly Revenue", f"${total_earnings:,.2f}")
    col2.metric("Monthly Bills", f"${total_bills:,.2f}")
    
    if net_cash >= 0:
        col3.metric("Net Cash Flow", f"+${net_cash:,.2f}")
    else:
        col3.metric("Net Cash Flow", f"-${abs(net_cash):,.2f}")

# --- CARDS TAB ---
with tabs[1]:
    st.header("Credit Card Management")
    edited_cards = st.data_editor(
        st.session_state.cards_df,
        num_rows="dynamic",
        use_container_width=True,
        key="cards_editor"
    )
    st.session_state.cards_df = edited_cards

# --- BILLS TAB ---
with tabs[2]:
    st.header("Bill Management")
    edited_bills = st.data_editor(
        st.session_state.bills_df,
        num_rows="dynamic",
        use_container_width=True,
        key="bills_editor"
    )
    st.session_state.bills_df = edited_bills

# --- REVENUE TAB ---
with tabs[3]:
    st.header("💰 Revenue Tracker")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("↩️ Undo"):
            if st.session_state.revenue_history:
                st.session_state.revenue_df = st.session_state.revenue_history.pop()
                st.rerun()
    
    def update_revenue():
        if 'revenue_editor' in st.session_state:
            df = st.session_state.revenue_editor
            df['Difference'] = df['Earnings'] - df['Goal']
            df['Status'] = df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
            st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
            st.session_state.revenue_df = df
    
    edited_revenue = st.data_editor(
        st.session_state.revenue_df,
        num_rows="dynamic",
        use_container_width=True,
        key="revenue_editor",
        on_change=update_revenue,
        column_config={
            "Day": st.column_config.TextColumn("Day"),
            "Date": st.column_config.TextColumn("Date"),
            "Hours": st.column_config.NumberColumn("Hours", format="%.2f"),
            "Earnings": st.column_config.NumberColumn("Earnings ($)", format="$%.2f"),
            "Goal": st.column_config.NumberColumn("Goal ($)", format="$%.2f"),
            "Difference": st.column_config.NumberColumn("Diff ($)", disabled=True, format="$%.2f"),
            "Status": st.column_config.TextColumn("Status", disabled=True)
        },
        hide_index=True
    )
    
    # Summary
    st.markdown("---")
    st.subheader("📊 Summary")
    
    total_hours = edited_revenue['Hours'].sum()
    total_earnings = edited_revenue['Earnings'].sum()
    total_goal = edited_revenue['Goal'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Hours", f"{total_hours:.2f}")
    col2.metric("Total Earnings", f"${total_earnings:,.2f}")
    col3.metric("Total Goal", f"${total_goal:,.2f}")
