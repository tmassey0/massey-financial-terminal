import streamlit as st
import pandas as pd
import datetime
import calendar

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
    
    # Accounts data (formerly Bills) - ALL 13 BILLS from the spreadsheet
    if 'accounts_df' not in st.session_state:
        # Create the accounts dataframe with all 13 bills
        accounts_data = {
            'Account Name': [
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
            'Auto Pay': ['No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No'],
            'Notification': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
            'Active': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'Yes']
        }
        st.session_state.accounts_df = pd.DataFrame(accounts_data)
    
    # Payment Calendar
    if 'payment_calendar' not in st.session_state:
        # Create initial payment calendar
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        st.session_state.payment_calendar = create_payment_calendar(current_month, current_year)
    
    # Notification settings
    if 'notification_settings' not in st.session_state:
        st.session_state.notification_settings = {
            'email_notifications': False,
            'sms_notifications': False,
            'days_before_due': 3,
            'notification_email': '',
            'notification_phone': ''
        }
    
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

def create_payment_calendar(month, year):
    """Create a payment calendar for the specified month"""
    # Get active accounts
    active_accounts = st.session_state.accounts_df[st.session_state.accounts_df['Active'] == 'Yes']
    
    # Create calendar entries
    calendar_entries = []
    for _, account in active_accounts.iterrows():
        due_day = account['Due Day']
        # Handle month-end due dates
        last_day = calendar.monthrange(year, month)[1]
        if due_day > last_day:
            due_day = last_day
        
        due_date = datetime.date(year, month, due_day)
        
        # Calculate notification date
        notification_date = due_date - datetime.timedelta(days=st.session_state.notification_settings['days_before_due'])
        
        calendar_entries.append({
            'Account': account['Account Name'],
            'Amount': account['Amount'],
            'Due Date': due_date,
            'Pay Via': account['Pay Via'],
            'Category': account['Category'],
            'Late Fee': account['Late Fee'],
            'Auto Pay': account['Auto Pay'],
            'Notification': account['Notification'],
            'Status': 'Upcoming',
            'Payment Date': None,
            'Notes': '',
            'Notification Date': notification_date if account['Notification'] == 'Yes' else None
        })
    
    # Sort by due date
    calendar_df = pd.DataFrame(calendar_entries)
    if not calendar_df.empty:
        calendar_df = calendar_df.sort_values('Due Date')
    
    return calendar_df

# Call initialization
init_session_state()

# App title
st.title("🏛️ Strategic Capital Terminal")

# Create tabs - changed "BILLS" to "ACCOUNTS"
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 DASHBOARD", "💳 CARDS", "📋 ACCOUNTS", "📅 PAYMENT CALENDAR", "💰 REVENUE"])

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
    
    # Accounts Section (formerly Bills)
    st.subheader("📋 Accounts")
    col1, col2, col3 = st.columns(3)
    
    # Calculate total active accounts
    active_accounts_df = st.session_state.accounts_df[st.session_state.accounts_df['Active'] == 'Yes']
    total_accounts = active_accounts_df['Amount'].sum()
    num_active_accounts = len(active_accounts_df)
    
    col1.metric("Total Monthly Accounts", f"${total_accounts:,.2f}")
    col2.metric("Active Accounts", f"{num_active_accounts}")
    col3.metric("Avg Account Amount", f"${total_accounts/num_active_accounts:,.2f}" if num_active_accounts > 0 else "$0")
    
    # Show all accounts in an expander
    with st.expander("📋 All Accounts List"):
        display_accounts = active_accounts_df[['Account Name', 'Amount', 'Due Day', 'Pay Via', 'Category']].copy()
        display_accounts['Amount'] = display_accounts['Amount'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(display_accounts, use_container_width=True, hide_index=True)
    
    # Category breakdown
    with st.expander("📊 Category Breakdown"):
        category_totals = active_accounts_df.groupby('Category')['Amount'].sum().reset_index()
        category_totals.columns = ['Category', 'Total']
        category_totals = category_totals.sort_values('Total', ascending=False)
        category_totals['Total'] = category_totals['Total'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(category_totals, use_container_width=True, hide_index=True)
    
    # Cash Flow
    st.subheader("💰 Cash Flow")
    col1, col2, col3 = st.columns(3)
    
    net_cash = total_earnings - total_accounts
    col1.metric("Monthly Revenue", f"${total_earnings:,.2f}")
    col2.metric("Monthly Accounts", f"${total_accounts:,.2f}")
    
    if net_cash >= 0:
        col3.metric("Net Cash Flow", f"+${net_cash:,.2f}")
    else:
        col3.metric("Net Cash Flow", f"-${abs(net_cash):,.2f}")
    
    # Upcoming Payments from Calendar
    st.subheader("📅 Upcoming Payments")
    upcoming = st.session_state.payment_calendar[
        (st.session_state.payment_calendar['Due Date'] >= datetime.date.today()) &
        (st.session_state.payment_calendar['Status'] == 'Upcoming')
    ].head(5)
    
    if not upcoming.empty:
        for _, payment in upcoming.iterrows():
            days_until = (payment['Due Date'] - datetime.date.today()).days
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            col1.write(f"**{payment['Account']}**")
            col2.write(f"${payment['Amount']:,.2f}")
            col3.write(f"Due: {payment['Due Date'].strftime('%m/%d')}")
            if days_until <= st.session_state.notification_settings['days_before_due']:
                col4.warning(f"⚠️ {days_until} days")
            else:
                col4.write(f"{days_until} days")
    else:
        st.info("No upcoming payments")

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

# --- ACCOUNTS TAB (formerly BILLS) ---
with tab3:
    st.header("Account Management")
    st.info("📋 All 13 monthly accounts - Edit as needed")
    
    # Show account count
    total_accounts = len(st.session_state.accounts_df)
    active_accounts_count = len(st.session_state.accounts_df[st.session_state.accounts_df['Active'] == 'Yes'])
    st.write(f"**Total Accounts:** {total_accounts} | **Active Accounts:** {active_accounts_count}")
    
    # Data editor for accounts
    edited_accounts = st.data_editor(
        st.session_state.accounts_df,
        num_rows="dynamic",
        use_container_width=True,
        key="accounts_editor",
        column_config={
            "Account Name": st.column_config.TextColumn("Account Name", width="medium"),
            "Amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
            "Due Day": st.column_config.NumberColumn("Due Day", min_value=1, max_value=31, step=1),
            "Pay Via": st.column_config.TextColumn("Pay Via", width="small"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Late Fee": st.column_config.NumberColumn("Late Fee ($)", format="$%.2f"),
            "Grace Days": st.column_config.NumberColumn("Grace Days", min_value=0),
            "Auto Pay": st.column_config.SelectboxColumn("Auto Pay", options=['Yes', 'No']),
            "Notification": st.column_config.SelectboxColumn("Notification", options=['Yes', 'No']),
            "Active": st.column_config.SelectboxColumn("Active", options=['Yes', 'No'])
        }
    )
    st.session_state.accounts_df = edited_accounts
    
    # Update payment calendar when accounts change
    current_date = datetime.datetime.now()
    st.session_state.payment_calendar = create_payment_calendar(current_date.month, current_date.year)
    
    # Summary statistics for accounts
    st.markdown("---")
    st.subheader("📊 Account Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    active_accounts = edited_accounts[edited_accounts['Active'] == 'Yes']
    inactive_accounts = edited_accounts[edited_accounts['Active'] == 'No']
    
    total_active = active_accounts['Amount'].sum()
    total_inactive = inactive_accounts['Amount'].sum()
    
    col1.metric("Total Active Accounts", f"${total_active:,.2f}")
    col2.metric("Total Inactive Accounts", f"${total_inactive:,.2f}")
    col3.metric("Number Active", f"{len(active_accounts)}")
    col4.metric("Number Inactive", f"{len(inactive_accounts)}")
    
    # Late fee exposure
    st.subheader("⚠️ Late Fee Exposure")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Late Fee Risk", f"${active_accounts['Late Fee'].sum():,.2f}")
    col2.metric("Accounts with Late Fees", f"{len(active_accounts[active_accounts['Late Fee'] > 0])}")
    col3.metric("Avg Late Fee", f"${active_accounts[active_accounts['Late Fee'] > 0]['Late Fee'].mean():,.2f}" if len(active_accounts[active_accounts['Late Fee'] > 0]) > 0 else "$0")
    
    # Auto-pay summary
    st.subheader("🤖 Auto-Pay Status")
    col1, col2 = st.columns(2)
    auto_pay_count = len(active_accounts[active_accounts['Auto Pay'] == 'Yes'])
    col1.metric("Accounts on Auto-Pay", f"{auto_pay_count}")
    col2.metric("Manual Payments", f"{len(active_accounts) - auto_pay_count}")
    
    # Accounts by category
    with st.expander("📊 Accounts by Category"):
        category_summary = active_accounts.groupby('Category').agg({
            'Amount': ['sum', 'count']
        }).round(2)
        category_summary.columns = ['Total Amount', 'Number of Accounts']
        category_summary['Total Amount'] = category_summary['Total Amount'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(category_summary, use_container_width=True)
    
    # Accounts by card
    with st.expander("💳 Accounts by Card"):
        card_summary = active_accounts.groupby('Pay Via').agg({
            'Amount': ['sum', 'count']
        }).round(2)
        card_summary.columns = ['Total Amount', 'Number of Accounts']
        card_summary['Total Amount'] = card_summary['Total Amount'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(card_summary, use_container_width=True)
    
    if st.button("Save Accounts", key="save_accounts"):
        st.success("Accounts saved successfully!")

# --- PAYMENT CALENDAR TAB ---
with tab4:
    st.header("📅 Editable Payment Calendar")
    
    # Month and year selector
    col1, col2, col3 = st.columns([1, 1, 2])
    current_date = datetime.datetime.now()
    
    with col1:
        selected_month = st.selectbox(
            "Month",
            range(1, 13),
            index=current_date.month - 1,
            format_func=lambda x: calendar.month_name[x]
        )
    
    with col2:
        selected_year = st.number_input("Year", min_value=2024, max_value=2030, value=current_date.year)
    
    # Update calendar when month/year changes
    if st.button("📅 Load Month", key="load_month"):
        st.session_state.payment_calendar = create_payment_calendar(selected_month, selected_year)
        st.rerun()
    
    # Notification Settings
    with st.expander("🔔 Notification Settings"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.notification_settings['email_notifications'] = st.checkbox(
                "Enable Email Notifications",
                value=st.session_state.notification_settings['email_notifications']
            )
            if st.session_state.notification_settings['email_notifications']:
                st.session_state.notification_settings['notification_email'] = st.text_input(
                    "Email Address",
                    value=st.session_state.notification_settings['notification_email']
                )
        
        with col2:
            st.session_state.notification_settings['sms_notifications'] = st.checkbox(
                "Enable SMS Notifications",
                value=st.session_state.notification_settings['sms_notifications']
            )
            if st.session_state.notification_settings['sms_notifications']:
                st.session_state.notification_settings['notification_phone'] = st.text_input(
                    "Phone Number",
                    value=st.session_state.notification_settings['notification_phone']
                )
        
        st.session_state.notification_settings['days_before_due'] = st.slider(
            "Days Before Due to Notify",
            min_value=1,
            max_value=14,
            value=st.session_state.notification_settings['days_before_due']
        )
        
        if st.button("Save Notification Settings"):
            st.success("Notification settings saved!")
            # Recreate calendar to update notification dates
            st.session_state.payment_calendar = create_payment_calendar(selected_month, selected_year)
            st.rerun()
    
    # Display payment calendar
    if not st.session_state.payment_calendar.empty:
        # Add color coding for due dates
        def color_due_date(row):
            days_until = (row['Due Date'] - datetime.date.today()).days
            if row['Status'] == 'Paid':
                return ['background-color: #28a74520'] * len(row)
            elif days_until < 0:
                return ['background-color: #dc354520'] * len(row)  # Past due
            elif days_until <= st.session_state.notification_settings['days_before_due']:
                return ['background-color: #ffc10720'] * len(row)  # Approaching due
            return [''] * len(row)
        
        # Editable calendar
        st.subheader(f"Payment Schedule - {calendar.month_name[selected_month]} {selected_year}")
        
        edited_calendar = st.data_editor(
            st.session_state.payment_calendar,
            num_rows="dynamic",
            use_container_width=True,
            key="calendar_editor",
            column_config={
                "Account": st.column_config.TextColumn("Account", disabled=True),
                "Amount": st.column_config.NumberColumn("Amount", format="$%.2f", disabled=True),
                "Due Date": st.column_config.DateColumn("Due Date", disabled=True),
                "Pay Via": st.column_config.TextColumn("Pay Via", width="small"),
                "Category": st.column_config.TextColumn("Category", width="small", disabled=True),
                "Late Fee": st.column_config.NumberColumn("Late Fee", format="$%.2f", disabled=True),
                "Auto Pay": st.column_config.SelectboxColumn("Auto Pay", options=['Yes', 'No']),
                "Notification": st.column_config.SelectboxColumn("Notify", options=['Yes', 'No']),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=['Upcoming', 'Paid', 'Skipped', 'Pending']
                ),
                "Payment Date": st.column_config.DateColumn("Payment Date"),
                "Notes": st.column_config.TextColumn("Notes"),
                "Notification Date": st.column_config.DateColumn("Notify By", disabled=True)
            },
            hide_index=True
        )
        
        # Update accounts when calendar changes
        if not edited_calendar.equals(st.session_state.payment_calendar):
            st.session_state.payment_calendar = edited_calendar
            st.rerun()
        
        # Summary stats
        st.markdown("---")
        st.subheader("📊 Payment Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_due = edited_calendar[edited_calendar['Status'] == 'Upcoming']['Amount'].sum()
        total_paid = edited_calendar[edited_calendar['Status'] == 'Paid']['Amount'].sum()
        upcoming_count = len(edited_calendar[edited_calendar['Status'] == 'Upcoming'])
        paid_count = len(edited_calendar[edited_calendar['Status'] == 'Paid'])
        
        col1.metric("Total Due", f"${total_due:,.2f}")
        col2.metric("Total Paid", f"${total_paid:,.2f}")
        col3.metric("Upcoming Payments", f"{upcoming_count}")
        col4.metric("Completed Payments", f"{paid_count}")
        
        # Upcoming notifications
        st.subheader("🔔 Upcoming Notifications")
        today = datetime.date.today()
        upcoming_notifications = edited_calendar[
            (edited_calendar['Notification'] == 'Yes') &
            (edited_calendar['Notification Date'] <= today) &
            (edited_calendar['Status'] == 'Upcoming')
        ]
        
        if not upcoming_notifications.empty:
            for _, notification in upcoming_notifications.iterrows():
                days_until = (notification['Due Date'] - today).days
                st.warning(
                    f"**{notification['Account']}** - "
                    f"${notification['Amount']:,.2f} due in {days_until} days "
                    f"({notification['Due Date'].strftime('%m/%d')})"
                )
        else:
            st.info("No upcoming notifications")
        
        # Mark as paid button
        if st.button("✅ Mark Selected as Paid"):
            # This would need checkbox selection - simplified version
            st.info("Select rows and mark status as 'Paid' in the editor")
    
    else:
        st.info("No active accounts to display in calendar")

# --- REVENUE TAB ---
with tab5:
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
