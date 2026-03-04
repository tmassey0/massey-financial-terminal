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
def load_and_fix(file, sheet, skip, cols):
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        # For Uber sheets, we need to be more careful
        if "Uber Tracker" in file:
            # Find the actual data rows (where Date and Hours are populated)
            df = df[df.iloc[:, 1].notna()]  # Keep rows where Date column has data
            df.columns = ['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status']
            df = df.reset_index(drop=True)
        else:
            df.columns = [str(c).strip() for c in df.columns]
        return df.fillna(0)
    except Exception as e:
        print(f"Error loading {sheet}: {e}")
        return pd.DataFrame(columns=cols)

# --- 3. PERSISTENT MEMORY ---
if 'cards' not in st.session_state:
    st.session_state.cards = load_and_fix("Terrance Credit Card 1.xlsx", "Credit Cards", 1, ["Bank Name", "Balance", "Limit"])
if 'bills' not in st.session_state:
    st.session_state.bills = load_and_fix("Terrance Credit Card 1.xlsx", "Bill Master List", 1, ["Bill Name", "Amount"])
if 'uber' not in st.session_state:
    # Load March data
    df = pd.read_excel("Terrance Uber Tracker.xlsx", sheet_name="March", skiprows=3)
    # Filter to actual data rows (where Date is populated)
    df = df[df.iloc[:, 1].notna() & (df.iloc[:, 1] != '')]
    df = df.iloc[:, :7]  # Take first 7 columns
    df.columns = ['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status']
    # Convert numeric columns
    for col in ['Hours', 'Daily Earnings', 'Daily Goal', 'Difference']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    st.session_state.uber = df

# --- 4. THE COMMAND CENTER ---
st.title("🏛️ Massey Strategic Capital Terminal")

tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS & LIQUIDITY", "📅 BILL MASTER", "🚖 UBER PERFORMANCE"])

# --- DASHBOARD ---
with tabs[0]:
    c = st.session_state.cards
    bal_col = next((col for col in c.columns if 'Balance' in col or 'Current Balance' in col or 'M3' in str(col)), None)
    lim_col = next((col for col in c.columns if 'Limit' in col or 'Credit Limit' in col or 'C3' in str(col)), None)
    
    m1, m2, m3 = st.columns(3)
    if bal_col and lim_col:
        try:
            b = pd.to_numeric(c[bal_col], errors='coerce').sum()
            l = pd.to_numeric(c[lim_col], errors='coerce').sum()
            m1.metric("TOTAL LIABILITIES", f"${b:,.2f}")
            m2.metric("AVAILABLE CREDIT", f"${(l - b):,.2f}")
            m3.metric("UTILIZATION", f"{(b/l)*100:.1f}%" if l > 0 else "0%")
        except:
            m1.metric("TOTAL LIABILITIES", "$0.00")
            m2.metric("AVAILABLE CREDIT", "$0.00")
            m3.metric("UTILIZATION", "0%")

# --- CARDS ---
with tabs[1]:
    st.subheader("💳 Manage Portfolio")
    st.session_state.cards = st.data_editor(st.session_state.cards, num_rows="dynamic", use_container_width=True, key="ce_final")
    if st.button("💾 Save Cards", key="save_cards"): 
        st.success("Cards saved!")
        st.rerun()

# --- BILLS ---
with tabs[2]:
    st.subheader("📋 Manage Bills")
    st.session_state.bills = st.data_editor(st.session_state.bills, num_rows="dynamic", use_container_width=True, key="be_final")
    if st.button("💾 Save Bills", key="save_bills"): 
        st.success("Bills saved!")
        st.rerun()

# --- UBER PERFORMANCE (THE FIXED VERSION) ---
with tabs[3]:
    st.subheader("🚖 Edit Uber Performance - March 2026")
    
    # Show week selector
    weeks = ["Week 1 (Mar 2-8)", "Week 2 (Mar 9-15)", "Week 3 (Mar 16-22)", "Week 4 (Mar 23-29)", "All Weeks"]
    selected_week = st.selectbox("Select Week to Edit", weeks, key="week_selector")
    
    # Filter based on selection
    if selected_week != "All Weeks":
        week_data = st.session_state.uber.copy()
        if selected_week == "Week 1 (Mar 2-8)":
            week_data = week_data.iloc[0:7] if len(week_data) >= 7 else week_data
        elif selected_week == "Week 2 (Mar 9-15)":
            week_data = week_data.iloc[7:14] if len(week_data) >= 14 else week_data
        elif selected_week == "Week 3 (Mar 16-22)":
            week_data = week_data.iloc[14:21] if len(week_data) >= 21 else week_data
        elif selected_week == "Week 4 (Mar 23-29)":
            week_data = week_data.iloc[21:28] if len(week_data) >= 28 else week_data
    else:
        week_data = st.session_state.uber.copy()
    
    st.info("📝 Double-click any cell to edit. Hours format: 7.04 = 7 hours 4 minutes")
    
    # Create editable dataframe
    edited_uber = st.data_editor(
        week_data,
        num_rows="dynamic",
        use_container_width=True,
        key="ue_final",
        column_config={
            "Day": st.column_config.TextColumn("Day", disabled=True, width="small"),
            "Date": st.column_config.DatetimeColumn("Date", disabled=True, format="MM/DD/YYYY", width="small"),
            "Hours": st.column_config.NumberColumn(
                "Hours Worked",
                disabled=False,
                min_value=0,
                max_value=24,
                step=0.01,
                format="%.2f",
                help="Hours worked (e.g., 7.04 = 7 hours 4 minutes)"
            ),
            "Daily Earnings": st.column_config.NumberColumn(
                "Daily Earnings ($)",
                disabled=False,
                min_value=0,
                step=0.01,
                format="$%.2f",
                help="Enter daily earnings"
            ),
            "Daily Goal": st.column_config.NumberColumn(
                "Daily Goal ($)",
                disabled=False,
                min_value=0,
                step=0.01,
                format="$%.2f",
                help="Daily earnings goal"
            ),
            "Difference": st.column_config.NumberColumn(
                "Difference ($)",
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
    
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("🧮 Calculate Totals", key="calc_uber"):
            # Calculate difference and status
            edited_uber["Difference"] = edited_uber["Daily Earnings"] - edited_uber["Daily Goal"]
            edited_uber["Status"] = edited_uber["Difference"].apply(lambda x: "Goal Met" if x >= 0 else "Below Goal")
            
            # Update the main dataframe
            if selected_week != "All Weeks":
                # Update only the selected rows in the main dataframe
                start_idx = 0
                if selected_week == "Week 1 (Mar 2-8)":
                    start_idx = 0
                elif selected_week == "Week 2 (Mar 9-15)":
                    start_idx = 7
                elif selected_week == "Week 3 (Mar 16-22)":
                    start_idx = 14
                elif selected_week == "Week 4 (Mar 23-29)":
                    start_idx = 21
                
                for i, row in edited_uber.iterrows():
                    if start_idx + i < len(st.session_state.uber):
                        st.session_state.uber.iloc[start_idx + i] = row
            else:
                st.session_state.uber = edited_uber
            
            # Calculate week totals
            week_total_hours = edited_uber["Hours"].sum()
            week_total_earnings = edited_uber["Daily Earnings"].sum()
            week_total_goal = edited_uber["Daily Goal"].sum()
            
            st.success("✅ Calculations complete!")
            
    with col2:
        if st.button("💾 Save All Changes", key="save_uber"):
            # Save all changes
            if selected_week != "All Weeks":
                start_idx = 0
                if selected_week == "Week 1 (Mar 2-8)":
                    start_idx = 0
                elif selected_week == "Week 2 (Mar 9-15)":
                    start_idx = 7
                elif selected_week == "Week 3 (Mar 16-22)":
                    start_idx = 14
                elif selected_week == "Week 4 (Mar 23-29)":
                    start_idx = 21
                
                for i, row in edited_uber.iterrows():
                    if start_idx + i < len(st.session_state.uber):
                        st.session_state.uber.iloc[start_idx + i] = row
            else:
                st.session_state.uber = edited_uber
            st.success("💾 All changes saved!")
            st.rerun()
    
    # Show week summary
    st.markdown("---")
    st.subheader("📊 Week Summary")
    
    # Calculate totals
    if len(edited_uber) > 0:
        total_hours = edited_uber["Hours"].sum()
        total_earnings = edited_uber["Daily Earnings"].sum()
        total_goal = edited_uber["Daily Goal"].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Hours", f"{total_hours:.2f}")
        m2.metric("Total Earnings", f"${total_earnings:.2f}")
        m3.metric("Total Goal", f"${total_goal:.2f}")
        m4.metric("Net vs Goal", f"${(total_earnings - total_goal):.2f}")
    
    # Add new row button at bottom
    st.markdown("---")
    if st.button("➕ Add New Row", key="add_row"):
        new_row = pd.DataFrame({
            'Day': ['New Day'],
            'Date': [pd.Timestamp.now()],
            'Hours': [0],
            'Daily Earnings': [0],
            'Daily Goal': [175],
            'Difference': [0],
            'Status': ['Below Goal']
        })
        st.session_state.uber = pd.concat([st.session_state.uber, new_row], ignore_index=True)
        st.rerun()
