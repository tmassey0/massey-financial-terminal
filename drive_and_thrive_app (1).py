import streamlit as st
import pandas as pd
import datetime
import calendar
import time

# Attempt to import gspread – if it fails, we'll use local storage only
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    st.warning("Google Sheets integration not available. Data will not persist across devices.")

st.set_page_config(page_title="STRATEGIC CAPITAL TERMINAL", layout="wide")

# --- HELPER: ensure numeric columns are actually numbers ---
def ensure_numeric(df, columns):
    """Convert given columns to numeric, coercing errors to NaN."""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# --- GOOGLE SHEETS CONNECTION (only if available) ---
@st.cache_resource
def connect_to_gsheets():
    if not GSHEETS_AVAILABLE:
        return None
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = {
            "type": st.secrets["gsheets"]["type"],
            "project_id": st.secrets["gsheets"]["project_id"],
            "private_key_id": st.secrets["gsheets"]["private_key_id"],
            "private_key": st.secrets["gsheets"]["private_key"],
            "client_email": st.secrets["gsheets"]["client_email"],
            "client_id": st.secrets["gsheets"]["client_id"],
            "auth_uri": st.secrets["gsheets"]["auth_uri"],
            "token_uri": st.secrets["gsheets"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gsheets"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gsheets"]["client_x509_cert_url"]
        }
        creds = Credentials.from_service_account_info(credentials, scopes=scope)
        client = gspread.authorize(creds)
        try:
            spreadsheet = client.open('Strategic Capital Terminal Data')
        except:
            spreadsheet = client.create('Strategic Capital Terminal Data')
            spreadsheet.share(st.secrets["gsheets"]["client_email"], perm_type='user', role='writer')
        return spreadsheet
    except:
        return None

# --- AUTO-SAVE FUNCTION ---
def auto_save_to_gsheets(sheet_name, df):
    if st.session_state.spreadsheet is None:
        return False
    try:
        try:
            worksheet = st.session_state.spreadsheet.worksheet(sheet_name)
        except:
            worksheet = st.session_state.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
        df_copy = df.copy()
        for col in df_copy.columns:
            if df_copy[col].dtype == 'object' and len(df_copy) > 0:
                if isinstance(df_copy[col].iloc[0], (datetime.date, datetime.datetime)):
                    df_copy[col] = df_copy[col].astype(str)
        worksheet.clear()
        worksheet.update([df_copy.columns.values.tolist()] + df_copy.values.tolist())
        st.session_state.last_save[sheet_name] = time.time()
        return True
    except:
        return False

# --- LOAD DATA FROM GOOGLE SHEETS ---
def load_from_gsheets(sheet_name, default_df):
    if st.session_state.spreadsheet is None:
        return default_df
    try:
        worksheet = st.session_state.spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            # Try to convert every column to numeric if possible
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
            return df
        return default_df
    except:
        return default_df

# Initialize all session state variables
def init_session_state():
    if 'spreadsheet' not in st.session_state:
        st.session_state.spreadsheet = connect_to_gsheets() if GSHEETS_AVAILABLE else None
        st.session_state.last_save = {}
    
    if 'notification_settings' not in st.session_state:
        st.session_state.notification_settings = {
            'email_notifications': False,
            'sms_notifications': False,
            'days_before_due': 3,
            'notification_email': '',
            'notification_phone': ''
        }
    
    # Default cards data with all necessary fields
    default_cards_df = pd.DataFrame({
        'Card': ['Card1', 'Card2', 'Card3', 'Card4', 'Card5'],
        'Bank': ['Navy Federal', 'Indigo 3069', 'Indigo 1448', 'Milestone 5093', 'Destiny 3992'],
        'Limit': [1500, 500, 1000, 500, 1000],
        'Balance': [1500.10, 632.81, 599.40, 489.81, 944.27],
        'APR': [0.18, 0.359, 0.359, 0.359, 0.359],
        'Statement Day': [24, 9, 26, 9, 26],
        'Due Day': [21, 8, 25, 8, 25],
        'Credit Report Day': [24, 9, 26, 9, 26],
        'Active': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes']
    })
    
    default_accounts_data = {
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
        'Auto Pay': ['No'] * 13,
        'Notification': ['Yes'] * 13,
        'Active': ['Yes'] * 13
    }
    default_accounts_df = pd.DataFrame(default_accounts_data)
    
    default_revenue_data = {
        'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'Date': ['2026-03-02', '2026-03-03', '2026-03-04', '2026-03-05', '2026-03-06', '2026-03-07', '2026-03-08'],
        'Hours': [8.53, 0, 0, 0, 0, 0, 0],
        'Earnings': [224.70, 0, 0, 0, 0, 0, 0],
        'Goal': [150, 150, 150, 150, 150, 150, 150]
    }
    default_revenue_df = pd.DataFrame(default_revenue_data)
    default_revenue_df['Difference'] = default_revenue_df['Earnings'] - default_revenue_df['Goal']
    default_revenue_df['Status'] = default_revenue_df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
    
    today = datetime.date.today()
    default_ledger_data = {
        'Date': [
            today - datetime.timedelta(days=10),
            today - datetime.timedelta(days=9),
            today - datetime.timedelta(days=8),
            today - datetime.timedelta(days=7),
            today - datetime.timedelta(days=6),
            today - datetime.timedelta(days=5),
            today - datetime.timedelta(days=4),
            today - datetime.timedelta(days=3),
        ],
        'Description': [
            'Opening Balance',
            'Uber Earnings - Week 1',
            'Gas Station',
            'Walmart - Groceries',
            'Uber Earnings - Week 2',
            'Restaurant',
            'Amazon - Household',
            'Pharmacy'
        ],
        'Category': [
            'Balance Forward',
            'Income',
            'Transportation',
            'Shopping',
            'Income',
            'Dining',
            'Shopping',
            'Health'
        ],
        'Debit': [5000.00, 875.50, 0, 0, 942.30, 0, 0, 0],
        'Credit': [0, 0, 45.67, 89.32, 0, 32.50, 67.89, 15.43],
        'Payment Method': [
            'Cash',
            'Bank Transfer',
            'Card1',
            'Card2',
            'Bank Transfer',
            'Cash',
            'Card3',
            'Card4'
        ],
        'Notes': [
            'Starting balance',
            'Week 1 earnings',
            'Filled up tank',
            'Groceries and supplies',
            'Week 2 earnings',
            'Lunch with friends',
            'Household items',
            'Prescription'
        ]
    }
    default_ledger_df = pd.DataFrame(default_ledger_data)
    default_ledger_df['Balance'] = default_ledger_df['Debit'].cumsum() - default_ledger_df['Credit'].cumsum()
    
    # Load data from Google Sheets (if available)
    if 'cards_df' not in st.session_state:
        st.session_state.cards_df = load_from_gsheets('Cards', default_cards_df) if st.session_state.spreadsheet else default_cards_df
    
    if 'accounts_df' not in st.session_state:
        st.session_state.accounts_df = load_from_gsheets('Accounts', default_accounts_df) if st.session_state.spreadsheet else default_accounts_df
    
    if 'revenue_df' not in st.session_state:
        st.session_state.revenue_df = load_from_gsheets('Revenue', default_revenue_df) if st.session_state.spreadsheet else default_revenue_df
    
    if 'ledger_df' not in st.session_state:
        st.session_state.ledger_df = load_from_gsheets('Ledger', default_ledger_df) if st.session_state.spreadsheet else default_ledger_df
    
    # Calendar
    if 'calendar_df' not in st.session_state:
        current_date = datetime.datetime.now()
        st.session_state.calendar_df = create_calendar_safe(current_date.month, current_date.year)
    
    # Revenue history for undo (stays in session only)
    if 'revenue_history' not in st.session_state:
        st.session_state.revenue_history = []
    
    # Ledger categories
    if 'ledger_categories' not in st.session_state:
        st.session_state.ledger_categories = [
            'Income', 'Balance Forward',
            'Transportation', 'Shopping', 'Dining', 'Health', 'Entertainment',
            'Utilities', 'Housing', 'Auto', 'Food', 'Personal Care',
            'Gifts', 'Education', 'Travel', 'Insurance', 'Subscriptions',
            'Miscellaneous'
        ]

def create_calendar_safe(month, year):
    try:
        if 'accounts_df' not in st.session_state or st.session_state.accounts_df.empty:
            return pd.DataFrame()
        accounts_df = st.session_state.accounts_df
        if 'Active' not in accounts_df.columns:
            return pd.DataFrame()
        active_accounts = accounts_df[accounts_df['Active'] == 'Yes']
        if active_accounts.empty:
            return pd.DataFrame()
        days_before_due = st.session_state.notification_settings.get('days_before_due', 3)
        calendar_entries = []
        for _, account in active_accounts.iterrows():
            try:
                due_day = account['Due Day']
                last_day = calendar.monthrange(year, month)[1]
                if due_day > last_day:
                    due_day = last_day
                due_date = datetime.date(year, month, due_day)
                notification_date = due_date - datetime.timedelta(days=days_before_due)
                calendar_entries.append({
                    'Account': account.get('Account Name', 'Unknown'),
                    'Amount': account.get('Amount', 0),
                    'Due Date': due_date,
                    'Pay Via': account.get('Pay Via', ''),
                    'Category': account.get('Category', ''),
                    'Late Fee': account.get('Late Fee', 0),
                    'Auto Pay': account.get('Auto Pay', 'No'),
                    'Notification': account.get('Notification', 'Yes'),
                    'Status': 'Upcoming',
                    'Payment Date': None,
                    'Notes': '',
                    'Notify By': notification_date if account.get('Notification') == 'Yes' else None
                })
            except:
                continue
        if calendar_entries:
            calendar_df = pd.DataFrame(calendar_entries)
            return calendar_df.sort_values('Due Date')
        return pd.DataFrame()
    except:
        return pd.DataFrame()

init_session_state()

st.title("🏛️ Strategic Capital Terminal")
if st.session_state.spreadsheet:
    st.caption("✅ Cloud-synced across all devices - Changes save automatically")
else:
    st.caption("⚠️ Local mode only - Data will not persist across devices. Configure Google Sheets for sync.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 DASHBOARD", "💳 CARDS", "📋 ACCOUNTS", "💰 REVENUE", "📒 LEDGER", "📅 CALENDAR"
])

# --- DASHBOARD TAB ---
with tab1:
    st.header("Financial Dashboard")
    
    st.subheader("📈 Overview")
    col1, col2, col3, col4 = st.columns(4)
    if not st.session_state.cards_df.empty:
        # Ensure numeric before summing
        cards = st.session_state.cards_df.copy()
        cards = ensure_numeric(cards, ['Limit', 'Balance'])
        total_limit = cards['Limit'].sum()
        total_balance = cards['Balance'].sum()
        available = total_limit - total_balance
        utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
        col1.metric("Total Credit Limit", f"${total_limit:,.2f}")
        col2.metric("Total Balance", f"${total_balance:,.2f}")
        col3.metric("Available Credit", f"${available:,.2f}")
        col4.metric("Utilization", f"{utilization:.1f}%")
    else:
        col1.metric("Total Credit Limit", "$0.00")
        col2.metric("Total Balance", "$0.00")
        col3.metric("Available Credit", "$0.00")
        col4.metric("Utilization", "0%")
    
    st.subheader("🚖 Revenue")
    col1, col2, col3, col4 = st.columns(4)
    if not st.session_state.revenue_df.empty:
        revenue = st.session_state.revenue_df.copy()
        revenue = ensure_numeric(revenue, ['Hours', 'Earnings', 'Goal'])
        total_hours = revenue['Hours'].sum()
        total_earnings = revenue['Earnings'].sum()
        total_goal = revenue['Goal'].sum()
        avg_hourly = total_earnings / total_hours if total_hours > 0 else 0
        col1.metric("Total Hours", f"{total_hours:.2f}")
        col2.metric("Total Earnings", f"${total_earnings:,.2f}")
        col3.metric("Goal vs Actual", f"${total_earnings - total_goal:,.2f}")
        col4.metric("Avg Hourly", f"${avg_hourly:.2f}")
    else:
        col1.metric("Total Hours", "0")
        col2.metric("Total Earnings", "$0")
        col3.metric("Goal vs Actual", "$0")
        col4.metric("Avg Hourly", "$0")
    
    st.subheader("📋 Accounts")
    col1, col2, col3 = st.columns(3)
    if not st.session_state.accounts_df.empty:
        accounts = st.session_state.accounts_df.copy()
        accounts = ensure_numeric(accounts, ['Amount', 'Due Day', 'Late Fee', 'Grace Days'])
        active_accounts_df = accounts[accounts['Active'] == 'Yes']
        total_accounts = active_accounts_df['Amount'].sum()
        num_active_accounts = len(active_accounts_df)
        col1.metric("Total Monthly Accounts", f"${total_accounts:,.2f}")
        col2.metric("Active Accounts", f"{num_active_accounts}")
        col3.metric("Avg Account Amount", f"${total_accounts/num_active_accounts:,.2f}" if num_active_accounts > 0 else "$0")
        
        with st.expander("📋 All Accounts List"):
            display_accounts = active_accounts_df[['Account Name', 'Amount', 'Due Day', 'Pay Via', 'Category']].copy()
            display_accounts['Amount'] = display_accounts['Amount'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_accounts, use_container_width=True, hide_index=True)
        
        with st.expander("📊 Category Breakdown"):
            category_totals = active_accounts_df.groupby('Category')['Amount'].sum().reset_index()
            category_totals.columns = ['Category', 'Total']
            category_totals = category_totals.sort_values('Total', ascending=False)
            category_totals['Total'] = category_totals['Total'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(category_totals, use_container_width=True, hide_index=True)
    else:
        col1.metric("Total Monthly Accounts", "$0")
        col2.metric("Active Accounts", "0")
        col3.metric("Avg Account Amount", "$0")
    
    st.subheader("📒 Current Financial Position")
    col1, col2, col3 = st.columns(3)
    if not st.session_state.ledger_df.empty:
        ledger = st.session_state.ledger_df.copy()
        ledger = ensure_numeric(ledger, ['Debit', 'Credit'])
        current_balance = ledger['Balance'].iloc[-1]
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        month_transactions = ledger[
            (pd.to_datetime(ledger['Date']).dt.month == current_month) &
            (pd.to_datetime(ledger['Date']).dt.year == current_year)
        ]
        month_income = month_transactions['Debit'].sum()
        month_expenses = month_transactions['Credit'].sum()
        col1.metric("Current Balance", f"${current_balance:,.2f}")
        col2.metric("MTD Income", f"${month_income:,.2f}")
        col3.metric("MTD Expenses", f"${month_expenses:,.2f}")
    else:
        col1.metric("Current Balance", "$0")
        col2.metric("MTD Income", "$0")
        col3.metric("MTD Expenses", "$0")
    
    st.subheader("📅 Upcoming Payments")
    if 'calendar_df' in st.session_state and not st.session_state.calendar_df.empty:
        upcoming = st.session_state.calendar_df[
            (st.session_state.calendar_df['Due Date'] >= datetime.date.today()) &
            (st.session_state.calendar_df['Status'] == 'Upcoming')
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
    else:
        st.info("No upcoming payments")

# --- CARDS TAB (enhanced with due dates and danger level) ---
with tab2:
    st.header("Credit Card Management")
    
    def get_danger_level(util):
        if util < 0.1:
            return "✅ Safe"
        elif util < 0.3:
            return "⚠️ Warning"
        elif util < 0.5:
            return "🔶 Caution"
        else:
            return "🚨 DANGER"
    
    # Prepare display DataFrame
    display_cards = st.session_state.cards_df.copy()
    if not display_cards.empty:
        # Ensure numeric for calculations
        display_cards = ensure_numeric(display_cards, ['Limit', 'Balance'])
        display_cards['Utilization'] = (display_cards['Balance'] / display_cards['Limit'] * 100).round(1)
        display_cards['Danger Level'] = display_cards['Utilization'].apply(lambda x: get_danger_level(x/100))
    
    edited_cards = st.data_editor(
        display_cards,
        num_rows="dynamic",
        use_container_width=True,
        key="cards_editor",
        column_config={
            "Card": st.column_config.TextColumn("Card", width="small"),
            "Bank": st.column_config.TextColumn("Bank", width="medium"),
            "Limit": st.column_config.NumberColumn("Credit Limit", format="$%.2f"),
            "Balance": st.column_config.NumberColumn("Current Balance", format="$%.2f"),
            "APR": st.column_config.NumberColumn("APR (%)", format="%.2f"),
            "Statement Day": st.column_config.NumberColumn("Statement Day", min_value=1, max_value=31),
            "Due Day": st.column_config.NumberColumn("Due Day", min_value=1, max_value=31),
            "Credit Report Day": st.column_config.NumberColumn("Credit Report Day", min_value=1, max_value=31),
            "Active": st.column_config.SelectboxColumn("Active", options=['Yes', 'No']),
            "Utilization": st.column_config.TextColumn("Utilization %", disabled=True),
            "Danger Level": st.column_config.TextColumn("Status", disabled=True)
        }
    )
    
    save_cols = ['Card', 'Bank', 'Limit', 'Balance', 'APR', 'Statement Day', 'Due Day', 'Credit Report Day', 'Active']
    if not edited_cards.empty:
        edited_cards = edited_cards[save_cols]
    
    # --- FIX: ensure numeric columns after edit ---
    if not edited_cards.equals(st.session_state.cards_df):
        st.session_state.cards_df = edited_cards
        # Force numeric conversion on key columns
        numeric_cols = ['Limit', 'Balance', 'APR', 'Statement Day', 'Due Day', 'Credit Report Day']
        st.session_state.cards_df = ensure_numeric(st.session_state.cards_df, numeric_cols)
        if st.session_state.spreadsheet:
            auto_save_to_gsheets('Cards', st.session_state.cards_df)
    
    st.markdown("---")
    st.subheader("📊 Card Summary")
    if not st.session_state.cards_df.empty:
        # Use a clean copy for calculations
        cards_summary = st.session_state.cards_df.copy()
        cards_summary = ensure_numeric(cards_summary, ['Limit', 'Balance'])
        total_limit = cards_summary['Limit'].sum()
        total_balance = cards_summary['Balance'].sum()
        available = total_limit - total_balance
        utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
        col1.metric("Total Limit", f"${total_limit:,.2f}")
        col2.metric("Total Balance", f"${total_balance:,.2f}")
        col3.metric("Available Credit", f"${available:,.2f}")
        col4.metric("Overall Utilization", f"{utilization:.1f}%")
        
        danger_counts = {}
        for _, row in cards_summary.iterrows():
            # Safe extraction and division
            limit_val = row['Limit'] if pd.notna(row['Limit']) else 0
            balance_val = row['Balance'] if pd.notna(row['Balance']) else 0
            if limit_val > 0:
                util = balance_val / limit_val
            else:
                util = 0
            level = get_danger_level(util)
            danger_counts[level] = danger_counts.get(level, 0) + 1
        
        st.write("**Card Status Breakdown:**")
        cols = st.columns(len(danger_counts))
        for i, (level, count) in enumerate(danger_counts.items()):
            cols[i].metric(level, count)
    else:
        st.info("No card data")

# --- ACCOUNTS TAB ---
with tab3:
    st.header("Account Management")
    st.info("📋 All 13 monthly accounts - Edit as needed")
    
    if not st.session_state.accounts_df.empty:
        total_accounts = len(st.session_state.accounts_df)
        active_accounts_count = len(st.session_state.accounts_df[st.session_state.accounts_df['Active'] == 'Yes'])
        st.write(f"**Total Accounts:** {total_accounts} | **Active Accounts:** {active_accounts_count}")
        
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
        
        # --- FIX: ensure numeric columns after edit ---
        if not edited_accounts.equals(st.session_state.accounts_df):
            st.session_state.accounts_df = edited_accounts
            numeric_cols = ['Amount', 'Due Day', 'Late Fee', 'Grace Days']
            st.session_state.accounts_df = ensure_numeric(st.session_state.accounts_df, numeric_cols)
            if st.session_state.spreadsheet:
                auto_save_to_gsheets('Accounts', st.session_state.accounts_df)
            current_date = datetime.datetime.now()
            st.session_state.calendar_df = create_calendar_safe(current_date.month, current_date.year)
        
        st.markdown("---")
        st.subheader("📊 Account Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        # Use cleaned data
        accounts_summary = st.session_state.accounts_df.copy()
        accounts_summary = ensure_numeric(accounts_summary, ['Amount', 'Late Fee'])
        active_accounts = accounts_summary[accounts_summary['Active'] == 'Yes']
        inactive_accounts = accounts_summary[accounts_summary['Active'] == 'No']
        total_active = active_accounts['Amount'].sum()
        total_inactive = inactive_accounts['Amount'].sum()
        col1.metric("Total Active Accounts", f"${total_active:,.2f}")
        col2.metric("Total Inactive Accounts", f"${total_inactive:,.2f}")
        col3.metric("Number Active", f"{len(active_accounts)}")
        col4.metric("Number Inactive", f"{len(inactive_accounts)}")
        
        st.subheader("⚠️ Late Fee Exposure")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Late Fee Risk", f"${active_accounts['Late Fee'].sum():,.2f}")
        col2.metric("Accounts with Late Fees", f"{len(active_accounts[active_accounts['Late Fee'] > 0])}")
        avg_late = active_accounts[active_accounts['Late Fee'] > 0]['Late Fee'].mean() if len(active_accounts[active_accounts['Late Fee'] > 0]) > 0 else 0
        col3.metric("Avg Late Fee", f"${avg_late:,.2f}")
        
        st.subheader("🤖 Auto-Pay Status")
        col1, col2 = st.columns(2)
        auto_pay_count = len(active_accounts[active_accounts['Auto Pay'] == 'Yes'])
        col1.metric("Accounts on Auto-Pay", f"{auto_pay_count}")
        col2.metric("Manual Payments", f"{len(active_accounts) - auto_pay_count}")
        
        with st.expander("📊 Accounts by Category"):
            category_summary = active_accounts.groupby('Category').agg({
                'Amount': ['sum', 'count']
            }).round(2)
            category_summary.columns = ['Total Amount', 'Number of Accounts']
            category_summary['Total Amount'] = category_summary['Total Amount'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(category_summary, use_container_width=True)
        
        with st.expander("💳 Accounts by Card"):
            card_summary = active_accounts.groupby('Pay Via').agg({
                'Amount': ['sum', 'count']
            }).round(2)
            card_summary.columns = ['Total Amount', 'Number of Accounts']
            card_summary['Total Amount'] = card_summary['Total Amount'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(card_summary, use_container_width=True)
        
        if st.button("Save Accounts", key="save_accounts"):
            st.success("Accounts saved successfully!")
    else:
        st.warning("No account data available")

# --- REVENUE TAB (fixed auto-update + navigation instructions) ---
with tab4:
    st.header("💰 Revenue Tracker")
    st.info(
        "**Navigation:** Press **Tab** to move **right** (Hours → Earnings → Goal → next row's Hours). "
        "Press **Enter** to move **down**. Difference and Status update automatically."
    )
    
    edited_revenue = st.data_editor(
        st.session_state.revenue_df,
        num_rows="dynamic",
        use_container_width=True,
        key="revenue_editor",
        column_config={
            "Day": st.column_config.TextColumn("Day", width="small"),
            "Date": st.column_config.TextColumn("Date", width="small"),
            "Hours": st.column_config.NumberColumn("Hours", format="%.2f"),
            "Earnings": st.column_config.NumberColumn("Earnings ($)", format="$%.2f"),
            "Goal": st.column_config.NumberColumn("Goal ($)", format="$%.2f"),
            "Difference": st.column_config.NumberColumn("Diff ($)", disabled=True, format="$%.2f"),
            "Status": st.column_config.TextColumn("Status", disabled=True)
        },
        hide_index=True
    )
    
    # If data changed, recalc derived columns, update session state, save, and rerun
    if not edited_revenue.equals(st.session_state.revenue_df):
        # Ensure numeric columns before calculations
        edited_revenue = ensure_numeric(edited_revenue, ['Hours', 'Earnings', 'Goal'])
        edited_revenue['Difference'] = edited_revenue['Earnings'] - edited_revenue['Goal']
        edited_revenue['Status'] = edited_revenue['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
        st.session_state.revenue_df = edited_revenue
        if st.session_state.spreadsheet:
            auto_save_to_gsheets('Revenue', st.session_state.revenue_df)
        st.rerun()  # Immediately refresh to show updated columns
    
    # Summary
    st.markdown("---")
    st.subheader("📊 Summary")
    
    df_display = st.session_state.revenue_df.copy()
    df_display = ensure_numeric(df_display, ['Hours', 'Earnings', 'Goal'])
    total_hours = df_display['Hours'].sum()
    total_earnings = df_display['Earnings'].sum()
    total_goal = df_display['Goal'].sum()
    total_diff = total_earnings - total_goal
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Hours", f"{total_hours:.2f}")
    col2.metric("Total Earnings", f"${total_earnings:,.2f}")
    col3.metric("Total Goal", f"${total_goal:,.2f}")
    if total_diff >= 0:
        col4.metric("Net vs Goal", f"+${total_diff:,.2f}", delta=f"+${total_diff:,.2f}")
    else:
        col4.metric("Net vs Goal", f"-${abs(total_diff):,.2f}", delta=f"-${abs(total_diff):,.2f}", delta_color="inverse")
    
    days_above = len(df_display[df_display['Earnings'] >= df_display['Goal']])
    days_below = len(df_display[df_display['Earnings'] < df_display['Goal']])
    success_rate = (days_above / len(df_display) * 100) if len(df_display) > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Days Above Goal", f"{days_above}")
    col2.metric("Days Below Goal", f"{days_below}")
    col3.metric("Success Rate", f"{success_rate:.1f}%")
    
    # Weekly breakdown
    if len(df_display) >= 7:
        with st.expander("📋 Weekly Breakdown"):
            df = df_display.copy()
            num_weeks = (len(df) + 6) // 7
            for week_num in range(num_weeks):
                start_idx = week_num * 7
                end_idx = min((week_num + 1) * 7, len(df))
                week_data = df.iloc[start_idx:end_idx]
                st.write(f"**Week {week_num + 1}**")
                w1, w2, w3, w4 = st.columns(4)
                w1.metric("Hours", f"{week_data['Hours'].sum():.2f}")
                w2.metric("Earnings", f"${week_data['Earnings'].sum():,.2f}")
                w3.metric("Goal", f"${week_data['Goal'].sum():,.2f}")
                week_diff = week_data['Earnings'].sum() - week_data['Goal'].sum()
                if week_diff >= 0:
                    w4.metric("Net", f"+${week_diff:,.2f}", delta=f"+${week_diff:,.2f}")
                else:
                    w4.metric("Net", f"-${abs(week_diff):,.2f}", delta=f"-${abs(week_diff):,.2f}", delta_color="inverse")
    
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
        week_df = ensure_numeric(week_df, ['Hours', 'Earnings', 'Goal'])
        week_df['Difference'] = week_df['Earnings'] - week_df['Goal']
        week_df['Status'] = week_df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
        st.session_state.revenue_df = pd.concat([st.session_state.revenue_df, week_df], ignore_index=True)
        if st.session_state.spreadsheet:
            auto_save_to_gsheets('Revenue', st.session_state.revenue_df)
        st.rerun()

# --- LEDGER TAB (auto-save on change) ---
with tab5:
    st.header("📒 Accounting Ledger")
    st.info("Double-Entry Style: Debits (Income In) | Credits (Expenses Out) | Running Balance")
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("➕ Income", key="add_income"):
            new_row = pd.DataFrame({
                'Date': [datetime.date.today()],
                'Description': ['New Income'],
                'Category': ['Income'],
                'Debit': [0.00],
                'Credit': [0.00],
                'Payment Method': ['Bank Transfer'],
                'Notes': ['']
            })
            new_row = ensure_numeric(new_row, ['Debit', 'Credit'])
            st.session_state.ledger_df = pd.concat([st.session_state.ledger_df, new_row], ignore_index=True)
            st.session_state.ledger_df = st.session_state.ledger_df.sort_values('Date')
            st.session_state.ledger_df['Balance'] = st.session_state.ledger_df['Debit'].cumsum() - st.session_state.ledger_df['Credit'].cumsum()
            if st.session_state.spreadsheet:
                auto_save_to_gsheets('Ledger', st.session_state.ledger_df)
            st.rerun()
    with col2:
        if st.button("💸 Expense", key="add_expense"):
            new_row = pd.DataFrame({
                'Date': [datetime.date.today()],
                'Description': ['New Expense'],
                'Category': ['Miscellaneous'],
                'Debit': [0.00],
                'Credit': [0.00],
                'Payment Method': ['Cash'],
                'Notes': ['']
            })
            new_row = ensure_numeric(new_row, ['Debit', 'Credit'])
            st.session_state.ledger_df = pd.concat([st.session_state.ledger_df, new_row], ignore_index=True)
            st.session_state.ledger_df = st.session_state.ledger_df.sort_values('Date')
            st.session_state.ledger_df['Balance'] = st.session_state.ledger_df['Debit'].cumsum() - st.session_state.ledger_df['Credit'].cumsum()
            if st.session_state.spreadsheet:
                auto_save_to_gsheets('Ledger', st.session_state.ledger_df)
            st.rerun()
    
    filter_option = st.selectbox("Filter by", ["All Time", "This Month", "Last Month", "This Year"])
    filtered_df = st.session_state.ledger_df.copy()
    # Ensure numeric for filters (though dates are fine)
    filtered_df = ensure_numeric(filtered_df, ['Debit', 'Credit'])
    if filter_option == "This Month":
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['Date']).dt.month == current_month) &
            (pd.to_datetime(filtered_df['Date']).dt.year == current_year)
        ]
    elif filter_option == "Last Month":
        last_month = datetime.datetime.now().month - 1
        if last_month == 0:
            last_month = 12
        current_year = datetime.datetime.now().year
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['Date']).dt.month == last_month) &
            (pd.to_datetime(filtered_df['Date']).dt.year == current_year)
        ]
    elif filter_option == "This Year":
        current_year = datetime.datetime.now().year
        filtered_df = filtered_df[pd.to_datetime(filtered_df['Date']).dt.year == current_year]
    
    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values('Date')
        filtered_df['Balance'] = filtered_df['Debit'].cumsum() - filtered_df['Credit'].cumsum()
    
    edited_ledger = st.data_editor(
        filtered_df,
        num_rows="dynamic",
        use_container_width=True,
        key="ledger_editor",
        column_config={
            "Date": st.column_config.DateColumn("Date", min_value=datetime.date(2020,1,1), max_value=datetime.date(2030,12,31), format="MM/DD/YYYY", required=True),
            "Description": st.column_config.TextColumn("Description", width="medium", required=True),
            "Category": st.column_config.SelectboxColumn("Category", width="medium", options=st.session_state.ledger_categories, required=True),
            "Debit": st.column_config.NumberColumn("Debit (Income) $", min_value=0.0, step=0.01, format="$%.2f"),
            "Credit": st.column_config.NumberColumn("Credit (Expense) $", min_value=0.0, step=0.01, format="$%.2f"),
            "Payment Method": st.column_config.SelectboxColumn("Payment Method", width="small", options=['Cash','Bank Transfer','Card1','Card2','Card3','Card4','Card5','Debit','Other']),
            "Notes": st.column_config.TextColumn("Notes", width="large"),
            "Balance": st.column_config.NumberColumn("Running Balance", disabled=True, format="$%.2f")
        },
        hide_index=True
    )
    
    if not edited_ledger.equals(st.session_state.ledger_df):
        edited_ledger = ensure_numeric(edited_ledger, ['Debit', 'Credit'])
        edited_ledger = edited_ledger.sort_values('Date')
        edited_ledger['Balance'] = edited_ledger['Debit'].cumsum() - edited_ledger['Credit'].cumsum()
        st.session_state.ledger_df = edited_ledger
        if st.session_state.spreadsheet:
            auto_save_to_gsheets('Ledger', st.session_state.ledger_df)
    
    st.markdown("---")
    st.subheader("📊 Ledger Summary")
    col1, col2, col3, col4 = st.columns(4)
    if not st.session_state.ledger_df.empty:
        ledger_summary = st.session_state.ledger_df.copy()
        ledger_summary = ensure_numeric(ledger_summary, ['Debit', 'Credit'])
        current_balance = ledger_summary['Balance'].iloc[-1]
        total_debits = ledger_summary['Debit'].sum()
        total_credits = ledger_summary['Credit'].sum()
        transaction_count = len(ledger_summary)
        col1.metric("Current Balance", f"${current_balance:,.2f}")
        col2.metric("Total Income (Debits)", f"${total_debits:,.2f}")
        col3.metric("Total Expenses (Credits)", f"${total_credits:,.2f}")
        col4.metric("# of Transactions", f"{transaction_count}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💰 Income by Category")
            income_summary = ledger_summary[ledger_summary['Debit'] > 0].groupby('Category').agg({'Debit':['sum','count']}).round(2)
            if not income_summary.empty:
                income_summary.columns = ['Total', '# of Transactions']
                income_summary = income_summary.sort_values('Total', ascending=False)
                income_summary['Total'] = income_summary['Total'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(income_summary, use_container_width=True)
            else:
                st.info("No income transactions")
        with col2:
            st.subheader("💸 Expenses by Category")
            expense_summary = ledger_summary[ledger_summary['Credit'] > 0].groupby('Category').agg({'Credit':['sum','count']}).round(2)
            if not expense_summary.empty:
                expense_summary.columns = ['Total', '# of Transactions']
                expense_summary = expense_summary.sort_values('Total', ascending=False)
                expense_summary['Total'] = expense_summary['Total'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(expense_summary, use_container_width=True)
            else:
                st.info("No expense transactions")
    else:
        col1.metric("Current Balance", "$0")
        col2.metric("Total Income", "$0")
        col3.metric("Total Expenses", "$0")
        col4.metric("# of Transactions", "0")

# --- CALENDAR TAB ---
with tab6:
    st.header("📅 Editable Calendar")
    
    col1, col2, col3 = st.columns([1,1,2])
    current_date = datetime.datetime.now()
    with col1:
        selected_month = st.selectbox("Month", range(1,13), index=current_date.month-1, format_func=lambda x: calendar.month_name[x])
    with col2:
        selected_year = st.number_input("Year", min_value=2024, max_value=2030, value=current_date.year)
    
    if st.button("📅 Load Month", key="load_month"):
        st.session_state.calendar_df = create_calendar_safe(selected_month, selected_year)
        st.rerun()
    
    with st.expander("🔔 Notification Settings"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.notification_settings['email_notifications'] = st.checkbox("Enable Email Notifications", value=st.session_state.notification_settings['email_notifications'])
            if st.session_state.notification_settings['email_notifications']:
                st.session_state.notification_settings['notification_email'] = st.text_input("Email Address", value=st.session_state.notification_settings['notification_email'])
        with col2:
            st.session_state.notification_settings['sms_notifications'] = st.checkbox("Enable SMS Notifications", value=st.session_state.notification_settings['sms_notifications'])
            if st.session_state.notification_settings['sms_notifications']:
                st.session_state.notification_settings['notification_phone'] = st.text_input("Phone Number", value=st.session_state.notification_settings['notification_phone'])
        st.session_state.notification_settings['days_before_due'] = st.slider("Days Before Due to Notify", min_value=1, max_value=14, value=st.session_state.notification_settings['days_before_due'])
        if st.button("Save Notification Settings"):
            st.success("Notification settings saved!")
            st.session_state.calendar_df = create_calendar_safe(selected_month, selected_year)
            st.rerun()
    
    if 'calendar_df' in st.session_state and not st.session_state.calendar_df.empty:
        st.subheader(f"Schedule - {calendar.month_name[selected_month]} {selected_year}")
        edited_calendar = st.data_editor(
            st.session_state.calendar_df,
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
                "Auto Pay": st.column_config.SelectboxColumn("Auto Pay", options=['Yes','No']),
                "Notification": st.column_config.SelectboxColumn("Notify", options=['Yes','No']),
                "Status": st.column_config.SelectboxColumn("Status", options=['Upcoming','Paid','Skipped','Pending']),
                "Payment Date": st.column_config.DateColumn("Payment Date"),
                "Notes": st.column_config.TextColumn("Notes"),
                "Notify By": st.column_config.DateColumn("Notify By", disabled=True)
            },
            hide_index=True
        )
        if not edited_calendar.equals(st.session_state.calendar_df):
            st.session_state.calendar_df = edited_calendar
        
        st.markdown("---")
        st.subheader("📊 Summary")
        col1, col2, col3, col4 = st.columns(4)
        total_due = edited_calendar[edited_calendar['Status'] == 'Upcoming']['Amount'].sum()
        total_paid = edited_calendar[edited_calendar['Status'] == 'Paid']['Amount'].sum()
        upcoming_count = len(edited_calendar[edited_calendar['Status'] == 'Upcoming'])
        paid_count = len(edited_calendar[edited_calendar['Status'] == 'Paid'])
        col1.metric("Total Due", f"${total_due:,.2f}")
        col2.metric("Total Paid", f"${total_paid:,.2f}")
        col3.metric("Upcoming", f"{upcoming_count}")
        col4.metric("Completed", f"{paid_count}")
        
        st.subheader("🔔 Upcoming Notifications")
        today = datetime.date.today()
        upcoming_notifications = edited_calendar[
            (edited_calendar['Notification'] == 'Yes') &
            (edited_calendar['Notify By'] <= today) &
            (edited_calendar['Status'] == 'Upcoming')
        ]
        if not upcoming_notifications.empty:
            for _, notification in upcoming_notifications.iterrows():
                days_until = (notification['Due Date'] - today).days
                st.warning(f"**{notification['Account']}** - ${notification['Amount']:,.2f} due in {days_until} days ({notification['Due Date'].strftime('%m/%d')})")
        else:
            st.info("No upcoming notifications")
    else:
        st.info("No active accounts to display in calendar")
