import streamlit as st
import pandas as pd
import datetime

# This must be the first Streamlit command
st.set_page_config(page_title="STRATEGIC CAPITAL TERMINAL", layout="wide")

# Initialize all session state variables at the very beginning
def init_session_state():
    """Initialize all session state variables"""
    
    # Cards data
    if 'cards_df' not in st.session_state:
        st.session_state.cards_df = pd.DataFrame({
            'Card': ['Card1', 'Card2', 'Card3', 'Card4', 'Card5'],
            'Bank': ['Navy Federal', 'Indigo 3069', 'Indigo 1448', 'Milestone 5093', 'Destiny 3992'],
            'Limit': [1500, 500, 1000, 500, 1000],
            'Balance': [1500.10, 632.81, 599.40, 489.81, 944.27]
        })
    
    # Bills data
    if 'bills_df' not in st.session_state:
        st.session_state.bills_df = pd.DataFrame({
            'Bill Name': ['Storage 1', 'Storage 2', 'Storage 3', 'Storage 4', 'Intuit', 'Cell Phone'],
            'Amount': [478, 109, 180, 98, 75, 80],
            'Due Day': [1, 1, 1, 1, 20, 5],
            'Pay Via': ['Card1', 'Card1', 'Card2', 'Card2', 'Card2', 'Card3']
        })
    
    # Revenue data
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
    
    # Revenue history for undo
    if 'revenue_history' not in st.session_state:
        st.session_state.revenue_history = []

# Call initialization
init_session_state()

# App title
st.title("🏛️ Strategic Capital Terminal")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 DASHBOARD", "💳 CARDS", "📅 BILLS", "💰 REVENUE"])

# --- DASHBOARD TAB ---
with tab1:
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
with tab2:
    st.header("Credit Card Management")
    
    # Data editor for cards
    edited_cards = st.data_editor(
        st.session_state.cards_df,
        num_rows="dynamic",
        use_container_width=True,
        key="cards_editor"
    )
    st.session_state.cards_df = edited_cards
    
    if st.button("Save Cards", key="save_cards"):
        st.success("Cards saved successfully!")

# --- BILLS TAB ---
with tab3:
    st.header("Bill Management")
    
    # Data editor for bills
    edited_bills = st.data_editor(
        st.session_state.bills_df,
        num_rows="dynamic",
        use_container_width=True,
        key="bills_editor"
    )
    st.session_state.bills_df = edited_bills
    
    if st.button("Save Bills", key="save_bills"):
        st.success("Bills saved successfully!")

# --- REVENUE TAB ---
with tab4:
    st.header("💰 Revenue Tracker")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("↩️ Undo", key="undo_revenue"):
            if st.session_state.revenue_history:
                st.session_state.revenue_df = st.session_state.revenue_history.pop()
                st.rerun()
            else:
                st.warning("No more undos available")
    
    with col2:
        if st.button("🔄 Update", key="update_revenue"):
            df = st.session_state.revenue_df.copy()
            df['Difference'] = df['Earnings'] - df['Goal']
            df['Status'] = df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
            st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
            st.session_state.revenue_df = df
            st.rerun()
    
    # Data editor for revenue
    edited_revenue = st.data_editor(
        st.session_state.revenue_df,
        num_rows="dynamic",
        use_container_width=True,
        key="revenue_editor",
        column_config={
            "Day": st.column_config.TextColumn("Day", width="small"),
            "Date": st.column_config.TextColumn("Date", width="small"),
            "Hours": st.column_config.NumberColumn(
                "Hours", 
                min_value=0.0,
                max_value=24.0,
                step=0.01,
                format="%.2f"
            ),
            "Earnings": st.column_config.NumberColumn(
                "Earnings ($)", 
                min_value=0.0,
                step=0.01,
                format="$%.2f"
            ),
            "Goal": st.column_config.NumberColumn(
                "Goal ($)", 
                min_value=0.0,
                step=0.01,
                format="$%.2f"
            ),
            "Difference": st.column_config.NumberColumn(
                "Diff ($)", 
                disabled=True, 
                format="$%.2f"
            ),
            "Status": st.column_config.TextColumn(
                "Status", 
                disabled=True
            )
        },
        hide_index=True
    )
    
    # Auto-update calculations when data changes
    if 'last_revenue_state' not in st.session_state:
        st.session_state.last_revenue_state = edited_revenue.to_dict()
    else:
        if edited_revenue.to_dict() != st.session_state.last_revenue_state:
            edited_revenue['Difference'] = edited_revenue['Earnings'] - edited_revenue['Goal']
            edited_revenue['Status'] = edited_revenue['Difference'].apply(
                lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal'
            )
            st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
            st.session_state.revenue_df = edited_revenue
            st.session_state.last_revenue_state = edited_revenue.to_dict()
    
    # Summary section
    st.markdown("---")
    st.subheader("📊 Summary")
    
    # Calculate totals
    total_hours = edited_revenue['Hours'].sum()
    total_earnings = edited_revenue['Earnings'].sum()
    total_goal = edited_revenue['Goal'].sum()
    total_diff = total_earnings - total_goal
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Hours", f"{total_hours:.2f}")
    col2.metric("Total Earnings", f"${total_earnings:,.2f}")
    col3.metric("Total Goal", f"${total_goal:,.2f}")
    
    if total_diff >= 0:
        col4.metric("Net vs Goal", f"+${total_diff:,.2f}", delta=f"+${total_diff:,.2f}")
    else:
        col4.metric("Net vs Goal", f"-${abs(total_diff):,.2f}", delta=f"-${abs(total_diff):,.2f}", delta_color="inverse")
    
    # Performance metrics
    days_above = len(edited_revenue[edited_revenue['Earnings'] >= edited_revenue['Goal']])
    days_below = len(edited_revenue[edited_revenue['Earnings'] < edited_revenue['Goal']])
    success_rate = (days_above / len(edited_revenue) * 100) if len(edited_revenue) > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Days Above Goal", f"{days_above}")
    col2.metric("Days Below Goal", f"{days_below}")
    col3.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Add Week button
    if st.button("📅 Add Week", key="add_week"):
        # Save current state for undo
        st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_date = datetime.datetime.now()
        
        week_rows = []
        for i, day in enumerate(days):
            week_date = current_date + datetime.timedelta(days=i)
            week_rows.append({
                'Day': day,
                'Date': week_date.strftime("%Y-%m-%d"),
                'Hours': 0.0,
                'Earnings': 0.0,
                'Goal': 175.0
            })
        
        week_df = pd.DataFrame(week_rows)
        week_df['Difference'] = week_df['Earnings'] - week_df['Goal']
        week_df['Status'] = week_df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
        
        st.session_state.revenue_df = pd.concat([st.session_state.revenue_df, week_df], ignore_index=True)
        st.rerun()
