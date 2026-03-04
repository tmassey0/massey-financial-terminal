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

# Uber Data - Start with a simple dataframe
if 'uber_df' not in st.session_state:
    # Create sample data for demonstration
    sample_data = {
        'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'Date': [datetime.date(2026, 3, 2), datetime.date(2026, 3, 3), datetime.date(2026, 3, 4), 
                 datetime.date(2026, 3, 5), datetime.date(2026, 3, 6), datetime.date(2026, 3, 7), 
                 datetime.date(2026, 3, 8)],
        'Hours': [8.53, 0, 0, 0, 0, 0, 0],
        'Daily Earnings': [224.70, 0, 0, 0, 0, 0, 0],
        'Daily Goal': [150, 150, 150, 150, 150, 150, 150],
        'Difference': [74.70, -150, -150, -150, -150, -150, -150],
        'Status': ['Goal Met', 'Below Goal', 'Below Goal', 'Below Goal', 'Below Goal', 'Below Goal', 'Below Goal']
    }
    st.session_state.uber_df = pd.DataFrame(sample_data)
    st.session_state.current_month = "March"

# --- MAIN APP ---
st.title("🏛️ Massey Strategic Capital Terminal")

# Create tabs
tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS", "📅 BILLS", "🚖 UBER"])

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
        st.info("Load card data to see metrics")

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
        
        if st.button("Save Cards"):
            st.success("Cards saved!")
    else:
        st.warning("No card data available. Please check the Excel file.")

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
        
        if st.button("Save Bills"):
            st.success("Bills saved!")
    else:
        st.warning("No bill data available. Please check the Excel file.")

# --- TAB 4: UBER ---
with tabs[3]:
    st.header("Uber Earnings Tracker")
    
    # Month selector
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    selected_month = st.selectbox("Select Month", months, index=2)
    
    st.info(f"Editing {selected_month} 2026 - Changes calculate automatically!")
    
    # Create editor with auto-calculation
    def update_uber_data():
        if 'uber_editor' in st.session_state:
            df = st.session_state.uber_editor
            # Calculate difference and status
            df['Difference'] = df['Daily Earnings'] - df['Daily Goal']
            df['Status'] = df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
            st.session_state.uber_df = df
    
    # Display the data editor
    edited_uber = st.data_editor(
        st.session_state.uber_df,
        num_rows="dynamic",
        use_container_width=True,
        key="uber_editor",
        on_change=update_uber_data,
        column_config={
            "Day": st.column_config.TextColumn("Day", disabled=True),
            "Date": st.column_config.DateColumn("Date", disabled=False, format="MM/DD/YYYY"),
            "Hours": st.column_config.NumberColumn("Hours", min_value=0.0, max_value=24.0, step=0.01, format="%.2f"),
            "Daily Earnings": st.column_config.NumberColumn("Earnings ($)", min_value=0.0, step=0.01, format="$%.2f"),
            "Daily Goal": st.column_config.NumberColumn("Goal ($)", min_value=0.0, step=0.01, format="$%.2f"),
            "Difference": st.column_config.NumberColumn("Diff ($)", disabled=True, format="$%.2f"),
            "Status": st.column_config.TextColumn("Status", disabled=True)
        },
        hide_index=True,
    )
    
    # Summary section
    st.markdown("---")
    st.subheader("Weekly Summary")
    
    # Calculate totals
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
    
    # Add new row button
    if st.button("➕ Add New Day"):
        new_row = pd.DataFrame({
            'Day': ['New Day'],
            'Date': [datetime.date.today()],
            'Hours': [0.0],
            'Daily Earnings': [0.0],
            'Daily Goal': [175.0],
            'Difference': [-175.0],
            'Status': ['Below Goal']
        })
        st.session_state.uber_df = pd.concat([st.session_state.uber_df, new_row], ignore_index=True)
        st.rerun()
