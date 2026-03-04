import streamlit as st
import pandas as pd
import os
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="THE STRATEGIC CAPITAL TERMINAL", layout="wide")

# --- SIMPLE CUSTOM CSS ---
st.markdown("""
<style>
    div[data-testid="stMetric"] { 
        background-color: #161B22; 
        border: 1px solid #30363D; 
        border-radius: 8px; 
        padding: 20px; 
    }
    .stButton button {
        width: 100%;
    }
    .dashboard-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# --- CHECK AVAILABLE FILES ---
st.sidebar.header("📁 Data Files")
files = os.listdir()
st.sidebar.write("Files in directory:", files)

# --- SIMPLE DATA LOADING FUNCTION ---
@st.cache_data
def load_excel_file(file_path, sheet_name):
    try:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            # Filter out rows where first column is empty or starts with "Unnamed"
            if not df.empty:
                first_col = df.columns[0]
                df = df[df[first_col].notna() & (~df[first_col].astype(str).str.startswith('Unnamed'))]
            return df
        else:
            st.sidebar.error(f"File not found: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        st.sidebar.error(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

# --- LOAD DATA ---
# Credit Card Data - Filter out empty rows
if 'cards_df' not in st.session_state:
    cards_df = load_excel_file("Terrance Credit Card 1.xlsx", "Credit Cards")
    if not cards_df.empty:
        # Keep only active cards (where first column has actual Card IDs)
        cards_df = cards_df[cards_df.iloc[:, 0].notna()]
        cards_df = cards_df[~cards_df.iloc[:, 0].astype(str).str.contains('Card6|Card7|Card8|Card9|Card10|Card11|Card12|Card13|Card14|Card15', na=False)]
        st.session_state.cards_df = cards_df
    else:
        st.session_state.cards_df = pd.DataFrame()

# Bills Data - Filter out empty rows
if 'bills_df' not in st.session_state:
    bills_df = load_excel_file("Terrance Credit Card 1.xlsx", "Bill Master List")
    if not bills_df.empty:
        # Keep only active bills
        bills_df = bills_df[bills_df.iloc[:, 0].notna()]
        bills_df = bills_df[~bills_df.iloc[:, 0].astype(str).str.contains('Unnamed', na=False)]
        st.session_state.bills_df = bills_df
    else:
        st.session_state.bills_df = pd.DataFrame()

# Revenue Data with undo history
if 'revenue_df' not in st.session_state:
    # Create sample data
    sample_data = {
        'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'Date': ['3/2/2026', '3/3/2026', '3/4/2026', '3/5/2026', '3/6/2026', '3/7/2026', '3/8/2026'],
        'Hours': [8.53, 0, 0, 0, 0, 0, 0],
        'Earnings': [224.70, 0, 0, 0, 0, 0, 0],
        'Goal': [150, 150, 150, 150, 150, 150, 150]
    }
    st.session_state.revenue_df = pd.DataFrame(sample_data)
    st.session_state.revenue_history = []  # For undo functionality
    st.session_state.current_month = "March"

# --- MAIN APP ---
st.title("🏛️ The Strategic Capital Terminal")

# Create tabs
tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS", "📅 BILLS", "💰 REVENUE"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    st.header("Financial Dashboard")
    
    # Top Level Metrics
    st.markdown('<p class="dashboard-header">📈 OVERVIEW</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate card totals
    if not st.session_state.cards_df.empty:
        # Find balance and limit columns
        balance_col = None
        limit_col = None
        
        for col in st.session_state.cards_df.columns:
            if 'Total Current Balance' in str(col) or 'Balance' in str(col):
                balance_col = col
            if 'Credit Limit' in str(col) or 'Limit' in str(col):
                limit_col = col
        
        if balance_col and limit_col:
            total_balance = pd.to_numeric(st.session_state.cards_df[balance_col], errors='coerce').sum()
            total_limit = pd.to_numeric(st.session_state.cards_df[limit_col], errors='coerce').sum()
            available_credit = total_limit - total_balance
            
            col1.metric("Total Credit Limit", f"${total_limit:,.2f}")
            col2.metric("Total Balance", f"${total_balance:,.2f}")
            col3.metric("Available Credit", f"${available_credit:,.2f}")
            
            utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
            col4.metric("Overall Utilization", f"{utilization:.1f}%")
    else:
        col1.metric("Total Credit Limit", "$0.00")
        col2.metric("Total Balance", "$0.00")
        col3.metric("Available Credit", "$0.00")
        col4.metric("Overall Utilization", "0%")
    
    # Revenue Metrics
    st.markdown('<p class="dashboard-header">🚖 REVENUE METRICS</p>', unsafe_allow_html=True)
    
    if not st.session_state.revenue_df.empty:
        # Current month revenue
        total_hours = st.session_state.revenue_df['Hours'].sum()
        total_earnings = st.session_state.revenue_df['Earnings'].sum()
        total_goal = st.session_state.revenue_df['Goal'].sum()
        avg_hourly = total_earnings / total_hours if total_hours > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Hours", f"{total_hours:.2f}")
        col2.metric("Total Earnings", f"${total_earnings:,.2f}")
        col3.metric("Goal vs Actual", f"${total_earnings - total_goal:,.2f}")
        col4.metric("Avg Hourly Rate", f"${avg_hourly:.2f}")
        
        # Days above/below goal
        days_above = len(st.session_state.revenue_df[st.session_state.revenue_df['Earnings'] >= st.session_state.revenue_df['Goal']])
        days_below = len(st.session_state.revenue_df[st.session_state.revenue_df['Earnings'] < st.session_state.revenue_df['Goal']])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Days Above Goal", f"{days_above}")
        col2.metric("Days Below Goal", f"{days_below}")
        col3.metric("Success Rate", f"{(days_above/len(st.session_state.revenue_df)*100):.1f}%" if len(st.session_state.revenue_df) > 0 else "0%")
    else:
        col1.metric("Total Hours", "0")
        col2.metric("Total Earnings", "$0")
        col3.metric("Goal vs Actual", "$0")
        col4.metric("Avg Hourly Rate", "$0")
    
    # Bill Metrics
    st.markdown('<p class="dashboard-header">📋 BILL METRICS</p>', unsafe_allow_html=True)
    
    if not st.session_state.bills_df.empty:
        # Find amount column
        amount_col = None
        for col in st.session_state.bills_df.columns:
            if 'Amount' in str(col):
                amount_col = col
                break
        
        if amount_col:
            total_bills = pd.to_numeric(st.session_state.bills_df[amount_col], errors='coerce').sum()
            
            # Count active bills
            active_col = None
            for col in st.session_state.bills_df.columns:
                if 'Active' in str(col):
                    active_col = col
                    break
            
            if active_col:
                active_bills = len(st.session_state.bills_df[st.session_state.bills_df[active_col] == 'Yes'])
            else:
                active_bills = len(st.session_state.bills_df)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Monthly Bills", f"${total_bills:,.2f}")
            col2.metric("Active Bills", f"{active_bills}")
            col3.metric("Avg Bill Amount", f"${total_bills/active_bills:,.2f}" if active_bills > 0 else "$0")
    else:
        col1.metric("Total Monthly Bills", "$0")
        col2.metric("Active Bills", "0")
        col3.metric("Avg Bill Amount", "$0")
    
    # Cash Flow Overview
    st.markdown('<p class="dashboard-header">💰 CASH FLOW</p>', unsafe_allow_html=True)
    
    if not st.session_state.revenue_df.empty and not st.session_state.bills_df.empty:
        monthly_revenue = st.session_state.revenue_df['Earnings'].sum()
        
        # Find amount column for bills
        amount_col = None
        for col in st.session_state.bills_df.columns:
            if 'Amount' in str(col):
                amount_col = col
                break
        
        if amount_col:
            monthly_bills = pd.to_numeric(st.session_state.bills_df[amount_col], errors='coerce').sum()
            net_cash = monthly_revenue - monthly_bills
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Monthly Revenue", f"${monthly_revenue:,.2f}")
            col2.metric("Monthly Bills", f"${monthly_bills:,.2f}")
            
            if net_cash >= 0:
                col3.metric("Net Cash Flow", f"+${net_cash:,.2f}", delta=f"+${net_cash:,.2f}")
            else:
                col3.metric("Net Cash Flow", f"-${abs(net_cash):,.2f}", delta=f"-${abs(net_cash):,.2f}", delta_color="inverse")
    else:
        col1.metric("Monthly Revenue", "$0")
        col2.metric("Monthly Bills", "$0")
        col3.metric("Net Cash Flow", "$0")

# --- TAB 2: CARDS ---
with tabs[1]:
    st.header("Credit Card Management")
    
    if not st.session_state.cards_df.empty:
        edited_cards = st.data_editor(
            st.session_state.cards_df,
            num_rows="dynamic",
            use_container_width=True,
            key="cards_editor"
        )
        st.session_state.cards_df = edited_cards
        
        if st.button("Save Cards", key="save_cards"):
            st.success("Cards saved!")
    else:
        st.warning("No card data available.")
        if st.button("Create Card Template"):
            template = pd.DataFrame({
                'Card ID': ['Card1', 'Card2', 'Card3', 'Card4', 'Card5'],
                'Bank Name': ['Navy Federal', 'Indigo 3069', 'Indigo 1448', 'Milestone 5093', 'Destiny 3992'],
                'Credit Limit': [1500, 500, 1000, 500, 1000],
                'APR': [0.18, 0.359, 0.359, 0.359, 0.359],
                'Total Current Balance': [1500.1, 632.81, 599.4, 489.81, 944.27],
                'Active': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes']
            })
            st.session_state.cards_df = template
            st.rerun()

# --- TAB 3: BILLS ---
with tabs[2]:
    st.header("Bill Management")
    
    if not st.session_state.bills_df.empty:
        edited_bills = st.data_editor(
            st.session_state.bills_df,
            num_rows="dynamic",
            use_container_width=True,
            key="bills_editor"
        )
        st.session_state.bills_df = edited_bills
        
        if st.button("Save Bills", key="save_bills"):
            st.success("Bills saved!")
    else:
        st.warning("No bill data available.")
        if st.button("Create Bill Template"):
            template = pd.DataFrame({
                'Bill Name': ['Storage 1', 'Storage 2', 'Storage 3', 'Storage 4', 'Intuit', 
                             'Cell Phone', 'Car Payment', 'Car Insurance', 'Gas/Fuel', 'Groceries'],
                'Amount': [478, 109, 180, 98, 75, 80, 785, 0, 200, 400],
                'Due Day': [1, 1, 1, 1, 20, 5, 24, 10, 15, 1],
                'Pay Via': ['Card1', 'Card1', 'Card2', 'Card2', 'Card2', 'Card3', 'Card3', 'Card1', 'Card4', 'Card3'],
                'Category': ['Housing', 'Housing', 'Housing', 'Housing', 'Utilities', 'Phone', 'Auto', 'Auto', 'Auto', 'Health'],
                'Active': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes']
            })
            st.session_state.bills_df = template
            st.rerun()

# --- TAB 4: REVENUE ---
with tabs[3]:
    st.header("💰 Revenue Tracker")
    
    # Month selector
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    selected_month = st.selectbox("Select Month", months, index=2)
    
    st.info(f"Editing {selected_month} 2026 - Changes calculate automatically!")
    
    # Make a copy of the dataframe for editing
    if 'revenue_df' in st.session_state:
        working_df = st.session_state.revenue_df.copy()
    else:
        working_df = pd.DataFrame(columns=['Day', 'Date', 'Hours', 'Earnings', 'Goal'])
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Undo button
        if st.button("↩️ Undo", key="undo_revenue"):
            if st.session_state.revenue_history:
                st.session_state.revenue_df = st.session_state.revenue_history.pop()
                st.success("Undo successful!")
                st.rerun()
            else:
                st.warning("No more undos available")
    
    with col2:
        # Add week button
        if st.button("📅 Add Week", key="add_week"):
            # Save state for undo
            st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            current_date = datetime.datetime.now()
            
            week_rows = []
            for i, day in enumerate(days):
                week_date = current_date + datetime.timedelta(days=i)
                week_rows.append({
                    'Day': day,
                    'Date': week_date.strftime("%m/%d/%Y"),
                    'Hours': 0.0,
                    'Earnings': 0.0,
                    'Goal': 175.0
                })
            
            week_df = pd.DataFrame(week_rows)
            st.session_state.revenue_df = pd.concat([st.session_state.revenue_df, week_df], ignore_index=True)
            st.rerun()
    
    # Define the update function
    def update_revenue_data():
        try:
            if 'revenue_editor' in st.session_state and st.session_state.revenue_editor is not None:
                # Save current state for undo before making changes
                st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
                # Keep only last 10 undo states
                if len(st.session_state.revenue_history) > 10:
                    st.session_state.revenue_history.pop(0)
                
                # Update session state
                st.session_state.revenue_df = st.session_state.revenue_editor
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Display the data editor
    edited_revenue = st.data_editor(
        working_df,
        num_rows="dynamic",
        use_container_width=True,
        key="revenue_editor",
        on_change=update_revenue_data,
        column_config={
            "Day": st.column_config.TextColumn(
                "Day",
                disabled=False,
                width="small"
            ),
            "Date": st.column_config.TextColumn(
                "Date",
                disabled=False,
                width="small"
            ),
            "Hours": st.column_config.NumberColumn(
                "Hours",
                min_value=0.0,
                max_value=24.0,
                step=0.01,
                format="%.2f",
                disabled=False
            ),
            "Earnings": st.column_config.NumberColumn(
                "Earnings ($)",
                min_value=0.0,
                step=0.01,
                format="$%.2f",
                disabled=False
            ),
            "Goal": st.column_config.NumberColumn(
                "Goal ($)",
                min_value=0.0,
                step=0.01,
                format="$%.2f",
                disabled=False
            )
        },
        hide_index=True,
    )
    
    # Summary section
    st.markdown("---")
    st.subheader("📊 Summary")
    
    # Calculate totals
    if not edited_revenue.empty:
        total_hours = edited_revenue['Hours'].sum()
        total_earnings = edited_revenue['Earnings'].sum()
        total_goal = edited_revenue['Goal'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Hours", f"{total_hours:.2f}")
        col2.metric("Total Earnings", f"${total_earnings:,.2f}")
        col3.metric("Total Goal", f"${total_goal:,.2f}")
        
        # Weekly breakdown
        if len(edited_revenue) >= 7:
            with st.expander("📋 Weekly Breakdown"):
                num_weeks = (len(edited_revenue) + 6) // 7
                for week_num in range(num_weeks):
                    start_idx = week_num * 7
                    end_idx = min((week_num + 1) * 7, len(edited_revenue))
                    week_data = edited_revenue.iloc[start_idx:end_idx]
                    
                    st.write(f"**Week {week_num + 1}**")
                    w1, w2, w3 = st.columns(3)
                    w1.metric("Hours", f"{week_data['Hours'].sum():.2f}")
                    w2.metric("Earnings", f"${week_data['Earnings'].sum():,.2f}")
                    w3.metric("Goal", f"${week_data['Goal'].sum():,.2f}")
