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
    
    # Bills data - ALL 13 BILLS from the spreadsheet
    if 'bills_df' not in st.session_state:
        st.session_state.bills_df = pd.DataFrame({
            'Bill Name': [
                'Storage 1', 'Storage 2', 'Storage 3', 'Storage 4', 
                'Intuit', 'Cell Phone', 'Car Payment', 'Car Insurance',
                'Gas/Fuel', 'Groceries', 'Klarna', 'Affirm', 'NTTA'
            ],
            'Amount': [478, 109, 180, 98, 75, 80, 785, 0, 200, 400, 45, 30, 600],
            'Due Day': [1, 1, 1, 1, 20, 5, 24, 10, 15, 1, 15, 20, 15],
            'Pay Via': [
                'Card1', 'Card1', 'Card2', 'Card2', 
                'Card2', 'Card3', 'Card3', 'Card1',
                'Card4', 'Card3', 'Card2', 'Card5', 'Card5'
            ],
            'Category': [
                'Housing', 'Housing', 'Housing', 'Housing',
                'Utilities', 'Phone', 'Auto', 'Auto',
                'Auto', 'Health', 'Entertainment', 'Food', 'Auto'
            ],
            'Late Fee': [40, 25, 25, 20, 0, 25, 39, 25, 0, 0, 25, 0, 25],
            'Grace Days': [5, 5, 5, 5, 0, 0, 10, 10, 0, 0, 0, 0, 30],
            'Active': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes']
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
    
    # Bills Section - Now with all bills
    st.subheader("📋 Bills")
    col1, col2, col3 = st.columns(3)
    
    # Calculate total active bills
    active_bills_df = st.session_state.bills_df[st.session_state.bills_df['Active'] == 'Yes']
    total_bills = active_bills_df['Amount'].sum()
    num_active_bills = len(active_bills_df)
    
    col1.metric("Total Monthly Bills", f"${total_bills:,.2f}")
    col2.metric("Active Bills", f"{num_active_bills}")
    col3.metric("Avg Bill Amount", f"${total_bills/num_active_bills:,.2f}" if num_active_bills > 0 else "$0")
    
    # Category breakdown
    with st.expander("View by Category"):
        category_totals = active_bills_df.groupby('Category')['Amount'].sum().reset_index()
        category_totals.columns = ['Category', 'Total']
        category_totals = category_totals.sort_values('Total', ascending=False)
        st.dataframe(category_totals, use_container_width=True, hide_index=True)
    
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
        key="cards_editor",
        column_config={
            "Card": st.column_config.TextColumn("Card", width="small"),
            "Bank": st.column_config.TextColumn("Bank", width="medium"),
            "Limit": st.column_config.NumberColumn("Credit Limit", format="$%.2f"),
            "Balance": st.column_config.NumberColumn("Current Balance", format="$%.2f")
        }
    )
    st.session_state.cards_df = edited_cards
    
    if st.button("Save Cards", key="save_cards"):
        st.success("Cards saved successfully!")

# --- BILLS TAB ---
with tab3:
    st.header("Bill Management")
    st.info("All 13 monthly bills from your spreadsheet")
    
    # Data editor for bills - Now showing all columns
    edited_bills = st.data_editor(
        st.session_state.bills_df,
        num_rows="dynamic",
        use_container_width=True,
        key="bills_editor",
        column_config={
            "Bill Name": st.column_config.TextColumn("Bill Name", width="medium"),
            "Amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
            "Due Day": st.column_config.NumberColumn("Due Day", min_value=1, max_value=31, step=1),
            "Pay Via": st.column_config.TextColumn("Pay Via", width="small"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Late Fee": st.column_config.NumberColumn("Late Fee ($)", format="$%.2f"),
            "Grace Days": st.column_config.NumberColumn("Grace Days", min_value=0),
            "Active": st.column_config.SelectboxColumn("Active", options=['Yes', 'No'])
        }
    )
    st.session_state.bills_df = edited_bills
    
    # Summary statistics for bills
    col1, col2, col3 = st.columns(3)
    active_bills = edited_bills[edited_bills['Active'] == 'Yes']
    total_active = active_bills['Amount'].sum()
    
    col1.metric("Total Active Bills", f"${total_active:,.2f}")
    col2.metric("Number of Active Bills", f"{len(active_bills)}")
    col3.metric("Total Late Fee Exposure", f"${active_bills['Late Fee'].sum():,.2f}")
    
    if st.button("Save Bills", key="save_bills"):
        st.success("Bills saved successfully!")

# --- REVENUE TAB ---
with tab4:
    st.header("💰 Revenue Tracker")
    
    # Action buttons in columns
    col1, col2, col3 = st.columns([1, 1, 4])
    
    # Undo button
    with col1:
        if st.button("↩️ Undo", key="undo_revenue"):
            if st.session_state.revenue_history:
                st.session_state.revenue_df = st.session_state.revenue_history.pop()
                st.rerun()
            else:
                st.warning("No more undos available")
    
    # Update button
    with col2:
        if st.button("🔄 Update", key="update_revenue"):
            df = st.session_state.revenue_df.copy()
            df['Difference'] = df['Earnings'] - df['Goal']
            df['Status'] = df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
            st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
            if len(st.session_state.revenue_history) > 10:
                st.session_state.revenue_history.pop(0)
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
            if len(st.session_state.revenue_history) > 10:
                st.session_state.revenue_history.pop(0)
            st.session_state.revenue_df = edited_revenue
            st.session_state.last_revenue_state = edited_revenue.to_dict()
    
    # Summary section
    st.markdown("---")
    st.subheader("📊 Summary")
    
    total_hours = edited_revenue['Hours'].sum()
    total_earnings = edited_revenue['Earnings'].sum()
    total_goal = edited_revenue['Goal'].sum()
    total_diff = total_earnings - total_goal
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Hours", f"{total_hours:.2f}")
    col2.metric("Total Earnings", f"${total_earnings:,.2f}")
    col3.metric("Total Goal", f"${total_goal:,.2f}")
    
    if total_diff >= 0:
        col4.metric("Net vs Goal", f"+${total_diff:,.2f}", delta=f"+${total_diff:,.2f}")
    else:
        col4.metric("Net vs Goal", f"-${abs(total_diff):,.2f}", delta=f"-${abs(total_diff):,.2f}", delta_color="inverse")
    
    days_above = len(edited_revenue[edited_revenue['Earnings'] >= edited_revenue['Goal']])
    days_below = len(edited_revenue[edited_revenue['Earnings'] < edited_revenue['Goal']])
    success_rate = (days_above / len(edited_revenue) * 100) if len(edited_revenue) > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Days Above Goal", f"{days_above}")
    col2.metric("Days Below Goal", f"{days_below}")
    col3.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Add Week button
    if st.button("📅 Add Week", key="add_week"):
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
