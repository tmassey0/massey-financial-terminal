import streamlit as st
import pandas as pd
import plotly.express as px
import os
import datetime

# --- 1. BRANDING & UI CONFIG ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- CHECK FILES ---
st.sidebar.header("📁 Data Files")
files = os.listdir()
st.sidebar.write("Files found:", files)

# --- 2. DATA LOAD ENGINE ---
def load_and_fix(file, sheet, skip, cols):
    try:
        st.sidebar.write(f"Loading: {file} / {sheet}")
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        
        # For Uber sheets, we need to be more careful
        if "Uber Tracker" in file:
            # Filter to actual data rows (where Date has data)
            df = df[df.iloc[:, 1].notna() & (df.iloc[:, 1] != '')]
            if len(df.columns) >= 7:
                df = df.iloc[:, :7]  # Take first 7 columns
                df.columns = ['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status']
            else:
                # Handle case with fewer columns
                new_cols = ['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status']
                df = df.reindex(columns=new_cols[:len(df.columns)])
        else:
            df.columns = [str(c).strip() for c in df.columns]
        
        # Convert numeric columns
        for col in df.columns:
            if col in ['Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Amount', 'Balance', 'Limit']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.sidebar.error(f"Error loading {sheet}: {e}")
        return pd.DataFrame(columns=cols)

# --- 3. PERSISTENT MEMORY ---
if 'cards' not in st.session_state:
    st.session_state.cards = load_and_fix("Terrance Credit Card 1.xlsx", "Credit Cards", 1, 
                                          ["Bank Name", "Balance", "Limit", "APR", "Active"])
if 'bills' not in st.session_state:
    st.session_state.bills = load_and_fix("Terrance Credit Card 1.xlsx", "Bill Master List", 1, 
                                          ["Bill Name", "Amount", "Due Day", "Pay Via", "Category", "Active"])

# Load Uber data - get all sheets
uber_sheets = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

if 'uber_current' not in st.session_state:
    # Default to March
    try:
        df = pd.read_excel("Terrance Uber Tracker.xlsx", sheet_name="March", skiprows=3)
        # Filter to actual data rows
        df = df[df.iloc[:, 1].notna() & (df.iloc[:, 1] != '')]
        if len(df.columns) >= 7:
            df = df.iloc[:, :7]
            df.columns = ['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status']
            # Convert numeric columns
            for col in ['Hours', 'Daily Earnings', 'Daily Goal', 'Difference']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            # Calculate initial differences
            df['Difference'] = df['Daily Earnings'] - df['Daily Goal']
            df['Status'] = df['Difference'].apply(lambda x: "✅ Goal Met" if x >= 0 else "⚠️ Below Goal")
        st.session_state.uber_current = df
        st.session_state.uber_month = "March"
    except Exception as e:
        st.sidebar.error(f"Error loading Uber data: {e}")
        st.session_state.uber_current = pd.DataFrame(columns=['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status'])
        st.session_state.uber_month = "March"

# --- 4. THE COMMAND CENTER ---
st.title("🏛️ Massey Strategic Capital Terminal")

# Define tabs FIRST before using them
tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS & LIQUIDITY", "📅 BILL MASTER", "🚖 UBER PERFORMANCE"])

# --- DASHBOARD ---
with tabs[0]:
    c = st.session_state.cards
    
    # Find balance column
    bal_col = None
    for col in c.columns:
        if 'Balance' in col or 'M3' in str(col) or 'Current' in str(col) or 'Total Current' in str(col):
            bal_col = col
            break
    
    # Find limit column
    lim_col = None
    for col in c.columns:
        if 'Limit' in col or 'C3' in str(col) or 'Credit' in str(col):
            lim_col = col
            break
    
    m1, m2, m3 = st.columns(3)
    if bal_col and lim_col and bal_col in c.columns and lim_col in c.columns:
        try:
            b = pd.to_numeric(c[bal_col], errors='coerce').fillna(0).sum()
            l = pd.to_numeric(c[lim_col], errors='coerce').fillna(0).sum()
            m1.metric("TOTAL LIABILITIES", f"${b:,.2f}")
            m2.metric("AVAILABLE CREDIT", f"${(l - b):,.2f}")
            util = (b/l)*100 if l > 0 else 0
            m3.metric("UTILIZATION", f"{util:.1f}%")
        except Exception as e:
            m1.metric("TOTAL LIABILITIES", "$0.00")
            m2.metric("AVAILABLE CREDIT", "$0.00")
            m3.metric("UTILIZATION", "0%")
            st.sidebar.error(f"Dashboard error: {e}")
    else:
        m1.metric("TOTAL LIABILITIES", "$0.00")
        m2.metric("AVAILABLE CREDIT", "$0.00")
        m3.metric("UTILIZATION", "0%")
        st.info("Add cards in the CARDS tab to see metrics")

# --- CARDS ---
with tabs[1]:
    st.subheader("💳 Manage Portfolio")
    st.info("Edit your credit cards below. Add new rows with the (+) button.")
    
    edited_cards = st.data_editor(
        st.session_state.cards, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="ce_final",
        column_config={
            "Balance": st.column_config.NumberColumn(format="$%.2f"),
            "Limit": st.column_config.NumberColumn(format="$%.2f"),
            "APR": st.column_config.NumberColumn(format="%.2f%%"),
        }
    )
    st.session_state.cards = edited_cards
    
    if st.button("💾 Save Cards", key="save_cards"): 
        st.success("Cards saved to session!")
        st.rerun()

# --- BILLS ---
with tabs[2]:
    st.subheader("📋 Manage Bills")
    st.info("Edit your monthly bills below. Add new rows with the (+) button.")
    
    edited_bills = st.data_editor(
        st.session_state.bills, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="be_final",
        column_config={
            "Amount": st.column_config.NumberColumn(format="$%.2f"),
        }
    )
    st.session_state.bills = edited_bills
    
    if st.button("💾 Save Bills", key="save_bills"): 
        st.success("Bills saved to session!")
        st.rerun()

# --- UBER PERFORMANCE (WITH AUTO-CALCULATION) ---
with tabs[3]:
    st.subheader("🚖 Edit Uber Performance")
    
    # Month selector
    selected_month = st.selectbox("Select Month", uber_sheets, index=2, key="uber_month_selector")
    
    # Load selected month if changed
    if selected_month != st.session_state.uber_month:
        try:
            df = pd.read_excel("Terrance Uber Tracker.xlsx", sheet_name=selected_month, skiprows=3)
            # Filter to actual data rows
            df = df[df.iloc[:, 1].notna() & (df.iloc[:, 1] != '')]
            if len(df.columns) >= 7:
                df = df.iloc[:, :7]
                df.columns = ['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status']
                # Convert numeric columns
                for col in ['Hours', 'Daily Earnings', 'Daily Goal', 'Difference']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                # Calculate initial differences
                df['Difference'] = df['Daily Earnings'] - df['Daily Goal']
                df['Status'] = df['Difference'].apply(lambda x: "✅ Goal Met" if x >= 0 else "⚠️ Below Goal")
            st.session_state.uber_current = df
            st.session_state.uber_month = selected_month
        except Exception as e:
            st.error(f"Error loading {selected_month}: {e}")
    
    st.info(f"📝 Editing {st.session_state.uber_month} 2026. Changes calculate automatically!")
    st.caption("Hours format: 7.04 = 7 hours 4 minutes")
    
    # Week selector
    weeks = ["Week 1 (Days 1-7)", "Week 2 (Days 8-14)", "Week 3 (Days 15-21)", "Week 4 (Days 22-28)", "Week 5 (Days 29+)", "All Weeks"]
    selected_week = st.selectbox("Filter by Week", weeks, key="week_selector")
    
    # Filter based on selection
    uber_df = st.session_state.uber_current.copy()
    if selected_week != "All Weeks" and len(uber_df) > 0:
        if selected_week == "Week 1 (Days 1-7)":
            uber_df = uber_df.iloc[0:min(7, len(uber_df))]
        elif selected_week == "Week 2 (Days 8-14)":
            uber_df = uber_df.iloc[7:min(14, len(uber_df))]
        elif selected_week == "Week 3 (Days 15-21)":
            uber_df = uber_df.iloc[14:min(21, len(uber_df))]
        elif selected_week == "Week 4 (Days 22-28)":
            uber_df = uber_df.iloc[21:min(28, len(uber_df))]
        elif selected_week == "Week 5 (Days 29+)":
            uber_df = uber_df.iloc[28:]
    
    # Create a key that changes with the week to force refresh
    editor_key = f"uber_editor_{selected_week}_{st.session_state.uber_month}"
    
    # Create editable dataframe with on_change callback
    def on_uber_edit():
        # This gets the current state of the editor
        if editor_key in st.session_state and st.session_state[editor_key] is not None:
            edited_data = st.session_state[editor_key]
            
            # Calculate difference and status for each row
            for i, row in edited_data.iterrows():
                earnings = row.get('Daily Earnings', 0)
                goal = row.get('Daily Goal', 175)
                edited_data.at[i, 'Difference'] = earnings - goal
                edited_data.at[i, 'Status'] = "✅ Goal Met" if earnings - goal >= 0 else "⚠️ Below Goal"
            
            # Update the main dataframe
            if selected_week != "All Weeks" and len(uber_df) > 0:
                start_idx = 0
                if selected_week == "Week 1 (Days 1-7)":
                    start_idx = 0
                elif selected_week == "Week 2 (Days 8-14)":
                    start_idx = 7
                elif selected_week == "Week 3 (Days 15-21)":
                    start_idx = 14
                elif selected_week == "Week 4 (Days 22-28)":
                    start_idx = 21
                elif selected_week == "Week 5 (Days 29+)":
                    start_idx = 28
                
                for i, row in edited_data.iterrows():
                    if start_idx + i < len(st.session_state.uber_current):
                        st.session_state.uber_current.iloc[start_idx + i] = row
            else:
                st.session_state.uber_current = edited_data
    
    # Use the editor with on_change
    edited_uber = st.data_editor(
        uber_df,
        num_rows="dynamic",
        use_container_width=True,
        key=editor_key,
        on_change=on_uber_edit,
        column_config={
            "Day": st.column_config.TextColumn("Day", disabled=True, width="small"),
            "Date": st.column_config.DatetimeColumn("Date", disabled=True, format="MM/DD/YYYY", width="small"),
            "Hours": st.column_config.NumberColumn(
                "Hours Worked",
                disabled=False,
                min_value=0.0,
                max_value=24.0,
                step=0.01,
                format="%.2f",
                help="Hours worked (e.g., 7.04 = 7 hours 4 minutes)"
            ),
            "Daily Earnings": st.column_config.NumberColumn(
                "Daily Earnings ($)",
                disabled=False,
                min_value=0.0,
                step=0.01,
                format="$%.2f",
                help="Enter daily earnings"
            ),
            "Daily Goal": st.column_config.NumberColumn(
                "Daily Goal ($)",
                disabled=False,
                min_value=0.0,
                step=0.01,
                format="$%.2f",
                help="Daily earnings goal"
            ),
            "Difference": st.column_config.NumberColumn(
                "Difference ($)",
                disabled=True,  # Auto-calculated
                format="$%.2f"
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                disabled=True  # Auto-calculated
            )
        },
        hide_index=True,
    )
    
    # Manual recalc button as backup
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("🔄 Force Recalculate", key="force_recalc"):
            # Force recalculate all
            for i, row in st.session_state.uber_current.iterrows():
                earnings = row.get('Daily Earnings', 0)
                goal = row.get('Daily Goal', 175)
                st.session_state.uber_current.at[i, 'Difference'] = earnings - goal
                st.session_state.uber_current.at[i, 'Status'] = "✅ Goal Met" if earnings - goal >= 0 else "⚠️ Below Goal"
            st.success("✅ Recalculated all rows!")
            st.rerun()
    
    with col2:
        if st.button("💾 Save All Changes", key="save_uber"):
            st.success(f"💾 Changes saved to {st.session_state.uber_month}!")
            # No need to do anything else since data is already in session_state
    
    # Show week summary with auto-updating totals
    st.markdown("---")
    st.subheader("📊 Real-Time Summary")
    
    # Calculate totals from the CURRENT edited data
    if len(edited_uber) > 0:
        total_hours = edited_uber["Hours"].sum()
        total_earnings = edited_uber["Daily Earnings"].sum()
        total_goal = edited_uber["Daily Goal"].sum()
        total_diff = total_earnings - total_goal
        
        # Create metrics that update automatically
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Hours", f"{total_hours:.2f}")
        m2.metric("Total Earnings", f"${total_earnings:,.2f}")
        m3.metric("Total Goal", f"${total_goal:,.2f}")
        
        # Color code the difference metric
        if total_diff >= 0:
            m4.metric("Net vs Goal", f"+${total_diff:,.2f}", delta=f"+${total_diff:,.2f}")
        else:
            m4.metric("Net vs Goal", f"-${abs(total_diff):,.2f}", delta=f"-${abs(total_diff):,.2f}", delta_color="inverse")
        
        # Show daily breakdown
        with st.expander("📋 Daily Breakdown"):
            # Create a clean display dataframe
            display_df = edited_uber[['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status']].copy()
            display_df['Daily Earnings'] = display_df['Daily Earnings'].apply(lambda x: f"${x:,.2f}")
            display_df['Daily Goal'] = display_df['Daily Goal'].apply(lambda x: f"${x:,.2f}")
            display_df['Difference'] = display_df['Difference'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Add new row button
    st.markdown("---")
    if st.button("➕ Add New Row", key="add_row"):
        # Determine next day
        if len(st.session_state.uber_current) > 0:
            last_date = st.session_state.uber_current['Date'].iloc[-1]
            if isinstance(last_date, pd.Timestamp):
                next_date = last_date + pd.Timedelta(days=1)
            else:
                next_date = datetime.datetime.now()
        else:
            next_date = datetime.datetime.now()
        
        # Determine day name
        day_name = next_date.strftime("%A") if isinstance(next_date, (pd.Timestamp, datetime.datetime)) else "New Day"
        
        new_row = pd.DataFrame({
            'Day': [day_name],
            'Date': [next_date],
            'Hours': [0.0],
            'Daily Earnings': [0.0],
            'Daily Goal': [175.0],
            'Difference': [-175.0],  # Will be recalculated
            'Status': ['⚠️ Below Goal']
        })
        st.session_state.uber_current = pd.concat([st.session_state.uber_current, new_row], ignore_index=True)
        st.rerun()
