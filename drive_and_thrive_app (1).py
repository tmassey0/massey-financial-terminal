import streamlit as st
import pandas as pd
import os
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

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
            return df
        else:
            st.sidebar.error(f"File not found: {file_path}")
            return pd.DataFrame()
    except Exception as e:
        st.sidebar.error(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

# --- LOAD DATA ---
# Credit Card Data
if 'cards_df' not in st.session_state:
    cards_df = load_excel_file("Terrance Credit Card 1.xlsx", "Credit Cards")
    if not cards_df.empty:
        st.session_state.cards_df = cards_df
    else:
        st.session_state.cards_df = pd.DataFrame()

# Bills Data
if 'bills_df' not in st.session_state:
    bills_df = load_excel_file("Terrance Credit Card 1.xlsx", "Bill Master List")
    if not bills_df.empty:
        st.session_state.bills_df = bills_df
    else:
        st.session_state.bills_df = pd.DataFrame()

# Uber Data with undo history
if 'uber_df' not in st.session_state:
    # Create sample data for demonstration with clear column names
    sample_data = {
        'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'Date': ['3/2/2026', '3/3/2026', '3/4/2026', '3/5/2026', '3/6/2026', '3/7/2026', '3/8/2026'],
        'Hours': [8.53, 0, 0, 0, 0, 0, 0],
        'Daily Earnings': [224.70, 0, 0, 0, 0, 0, 0],
        'Daily Goal': [150, 150, 150, 150, 150, 150, 150],
        'Difference': [74.70, -150, -150, -150, -150, -150, -150],
        'Status': ['Goal Met', 'Below Goal', 'Below Goal', 'Below Goal', 'Below Goal', 'Below Goal', 'Below Goal']
    }
    st.session_state.uber_df = pd.DataFrame(sample_data)
    st.session_state.uber_history = []  # For undo functionality
    st.session_state.current_month = "March"

# --- MAIN APP ---
st.title("🏛️ Massey Strategic Capital Terminal")

# Create tabs - renamed "UBER" to "REVENUE"
tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS", "📅 BILLS", "💰 REVENUE"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    st.header("Financial Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    # Calculate totals from cards
    if not st.session_state.cards_df.empty:
        # Try to find balance and limit columns
        balance_cols = [col for col in st.session_state.cards_df.columns if 'Balance' in str(col)]
        limit_cols = [col for col in st.session_state.cards_df.columns if 'Limit' in str(col)]
        
        if balance_cols and limit_cols:
            balance_col = balance_cols[0]
            limit_col = limit_cols[0]
            
            total_balance = pd.to_numeric(st.session_state.cards_df[balance_col], errors='coerce').sum()
            total_limit = pd.to_numeric(st.session_state.cards_df[limit_col], errors='coerce').sum()
            
            col1.metric("Total Balance", f"${total_balance:,.2f}")
            col2.metric("Total Credit Limit", f"${total_limit:,.2f}")
            
            utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
            col3.metric("Utilization", f"{utilization:.1f}%")
        else:
            col1.metric("Total Balance", "$0.00")
            col2.metric("Total Credit Limit", "$0.00")
            col3.metric("Utilization", "0%")
    else:
        col1.metric("Total Balance", "$0.00")
        col2.metric("Total Credit Limit", "$0.00")
        col3.metric("Utilization", "0%")
        st.info("Add cards in the CARDS tab to see metrics")

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
        st.warning("No card data available. You can add cards manually.")
        # Create empty template for cards
        if st.button("Create Card Template"):
            template = pd.DataFrame({
                'Card ID': ['Card1', 'Card2'],
                'Bank Name': ['Navy Federal', 'Indigo'],
                'Credit Limit': [1500, 500],
                'APR': [0.18, 0.359],
                'Current Balance': [1500, 632.81],
                'Active': ['Yes', 'Yes']
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
        st.warning("No bill data available. You can add bills manually.")
        # Create empty template for bills
        if st.button("Create Bill Template"):
            template = pd.DataFrame({
                'Bill Name': ['Storage 1', 'Storage 2'],
                'Amount': [478, 109],
                'Due Day': [1, 1],
                'Pay Via': ['Card1', 'Card1'],
                'Category': ['Housing', 'Housing'],
                'Active': ['Yes', 'Yes']
            })
            st.session_state.bills_df = template
            st.rerun()

# --- TAB 4: REVENUE (formerly UBER) ---
with tabs[3]:
    st.header("💰 Revenue Tracker (Uber Earnings)")
    
    # Month selector
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    selected_month = st.selectbox("Select Month", months, index=2)
    
    st.info(f"Editing {selected_month} 2026 - Changes calculate automatically!")
    
    # Make a copy of the dataframe for editing
    if 'uber_df' in st.session_state:
        working_df = st.session_state.uber_df.copy()
    else:
        working_df = pd.DataFrame(columns=['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status'])
    
    # Define the update function with error handling
    def update_uber_data():
        try:
            if 'uber_editor' in st.session_state and st.session_state.uber_editor is not None:
                df = st.session_state.uber_editor
                
                # Check if required columns exist
                required_cols = ['Daily Earnings', 'Daily Goal']
                if all(col in df.columns for col in required_cols):
                    # Save current state for undo before making changes
                    st.session_state.uber_history.append(st.session_state.uber_df.copy())
                    # Keep only last 10 undo states
                    if len(st.session_state.uber_history) > 10:
                        st.session_state.uber_history.pop(0)
                    
                    # Calculate difference
                    df['Difference'] = df['Daily Earnings'] - df['Daily Goal']
                    
                    # Calculate status
                    df['Status'] = df['Difference'].apply(
                        lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal'
                    )
                    
                    # Update session state
                    st.session_state.uber_df = df
        except Exception as e:
            st.error(f"Error in calculation: {e}")
    
    # Action buttons in columns
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    
    with col1:
        # Undo button
        if st.button("↩️ Undo", key="undo_uber"):
            if st.session_state.uber_history:
                st.session_state.uber_df = st.session_state.uber_history.pop()
                st.success("Undo successful!")
                st.rerun()
            else:
                st.warning("No more undos available")
    
    with col2:
        # Manual update button
        if st.button("🔄 Update", key="update_uber"):
            if not working_df.empty:
                # Save state for undo
                st.session_state.uber_history.append(st.session_state.uber_df.copy())
                
                working_df['Difference'] = working_df['Daily Earnings'] - working_df['Daily Goal']
                working_df['Status'] = working_df['Difference'].apply(
                    lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal'
                )
                st.session_state.uber_df = working_df
                st.success("Calculations updated!")
                st.rerun()
    
    with col3:
        # Add single day
        if st.button("➕ Add Day", key="add_day"):
            # Save state for undo
            st.session_state.uber_history.append(st.session_state.uber_df.copy())
            
            new_row = pd.DataFrame({
                'Day': ['New Day'],
                'Date': [datetime.datetime.now().strftime("%m/%d/%Y")],
                'Hours': [0.0],
                'Daily Earnings': [0.0],
                'Daily Goal': [175.0],
                'Difference': [-175.0],
                'Status': ['⚠️ Below Goal']
            })
            st.session_state.uber_df = pd.concat([st.session_state.uber_df, new_row], ignore_index=True)
            st.rerun()
    
    with col4:
        # Add full week
        if st.button("📅 Add Week", key="add_week"):
            # Save state for undo
            st.session_state.uber_history.append(st.session_state.uber_df.copy())
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            current_date = datetime.datetime.now()
            
            week_rows = []
            for i, day in enumerate(days):
                week_date = current_date + datetime.timedelta(days=i)
                week_rows.append({
                    'Day': day,
                    'Date': week_date.strftime("%m/%d/%Y"),
                    'Hours': 0.0,
                    'Daily Earnings': 0.0,
                    'Daily Goal': 175.0,
                    'Difference': -175.0,
                    'Status': '⚠️ Below Goal'
                })
            
            week_df = pd.DataFrame(week_rows)
            st.session_state.uber_df = pd.concat([st.session_state.uber_df, week_df], ignore_index=True)
            st.rerun()
    
    # Display the data editor
    edited_uber = st.data_editor(
        working_df,
        num_rows="dynamic",
        use_container_width=True,
        key="uber_editor",
        on_change=update_uber_data,
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
            "Daily Earnings": st.column_config.NumberColumn(
                "Earnings ($)",
                min_value=0.0,
                step=0.01,
                format="$%.2f",
                disabled=False
            ),
            "Daily Goal": st.column_config.NumberColumn(
                "Goal ($)",
                min_value=0.0,
                step=0.01,
                format="$%.2f",
                disabled=False
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
        hide_index=True,
    )
    
    # Summary section
    st.markdown("---")
    st.subheader("📊 Weekly Summary")
    
    # Calculate totals from the current dataframe
    if not edited_uber.empty:
        try:
            total_hours = edited_uber['Hours'].sum()
            total_earnings = edited_uber['Daily Earnings'].sum()
            total_goal = edited_uber['Daily Goal'].sum()
            total_diff = total_earnings - total_goal
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Hours", f"{total_hours:.2f}")
            col2.metric("Total Earnings", f"${total_earnings:,.2f}")
            col3.metric("Total Goal", f"${total_goal:,.2f}")
            
            if total_diff >= 0:
                col4.metric("Net vs Goal", f"+${total_diff:,.2f}", delta=f"+${total_diff:,.2f}")
            else:
                col4.metric("Net vs Goal", f"-${abs(total_diff):,.2f}", delta=f"-${abs(total_diff):,.2f}", delta_color="inverse")
            
            # Show week-by-week breakdown
            if len(edited_uber) >= 7:
                with st.expander("📋 Week-by-Week Breakdown"):
                    num_weeks = (len(edited_uber) + 6) // 7
                    for week_num in range(num_weeks):
                        start_idx = week_num * 7
                        end_idx = min((week_num + 1) * 7, len(edited_uber))
                        week_data = edited_uber.iloc[start_idx:end_idx]
                        
                        st.write(f"**Week {week_num + 1}**")
                        week_cols = st.columns(4)
                        week_cols[0].metric("Week Hours", f"{week_data['Hours'].sum():.2f}")
                        week_cols[1].metric("Week Earnings", f"${week_data['Daily Earnings'].sum():,.2f}")
                        week_cols[2].metric("Week Goal", f"${week_data['Daily Goal'].sum():,.2f}")
                        week_diff = week_data['Daily Earnings'].sum() - week_data['Daily Goal'].sum()
                        week_cols[3].metric("Week Net", f"${week_diff:,.2f}")
                        
        except Exception as e:
            st.error(f"Error calculating totals: {e}")
