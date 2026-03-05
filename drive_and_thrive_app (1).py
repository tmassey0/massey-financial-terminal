import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import calendar

# Page config
st.set_page_config(
    page_title="Drive & Thrive Financial Terminal",
    page_icon="🚛",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    
    # Sample accounts data (formerly bills)
    st.session_state.accounts = [
        {"date": "2026-03-01", "description": "Truck Payment", "amount": 850.00, "category": "Loan", "paid": False},
        {"date": "2026-03-05", "description": "Fuel Card", "amount": 1250.00, "category": "Fuel", "paid": False},
        {"date": "2026-03-10", "description": "Insurance", "amount": 450.00, "category": "Insurance", "paid": True},
        {"date": "2026-03-15", "description": "Truck Repair", "amount": 675.00, "category": "Maintenance", "paid": False},
    ]
    
    # Sample revenue data
    st.session_state.revenue = [
        {"date": "2026-03-01", "description": "Load #1234", "amount": 2450.00, "customer": "ABC Logistics"},
        {"date": "2026-03-02", "description": "Load #1235", "amount": 1875.00, "customer": "XYZ Shipping"},
        {"date": "2026-03-03", "description": "Load #1236", "amount": 3120.00, "customer": "123 Transport"},
    ]
    
    # Cards data
    st.session_state.cards = [
        {"card_type": "Fuel", "card_number": "**** 1234", "balance": 450.00, "limit": 2000.00, "due_date": "2026-03-15"},
        {"card_type": "Fuel", "card_number": "**** 5678", "balance": 780.00, "limit": 2000.00, "due_date": "2026-03-20"},
        {"card_type": "Fleet", "card_number": "**** 9012", "balance": 1250.00, "limit": 5000.00, "due_date": "2026-03-10"},
        {"card_type": "Fuel", "card_number": "**** 3456", "balance": 320.00, "limit": 2000.00, "due_date": "2026-03-25"},
    ]
    
    # Calendar events
    st.session_state.calendar_events = [
        {"date": "2026-03-10", "event": "Oil Change - Pete 579", "type": "Maintenance"},
        {"date": "2026-03-15", "event": "DOT Inspection Due", "type": "Compliance"},
        {"date": "2026-03-08", "event": "Load Pickup - Chicago", "type": "Dispatch"},
        {"date": "2026-03-20", "event": "Fuel Card Statement", "type": "Financial"},
    ]

# Custom CSS - ORIGINAL BACKGROUND
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .card-item {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #ff6b35;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 style='color: white;'>🚛 Drive & Thrive Financial Terminal</h1>", unsafe_allow_html=True)

# Create tabs in CORRECT ORDER: Dashboard, Cards, Accounts, Revenue, Calendar
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "💳 Cards", "💰 Accounts", "📈 Revenue", "📅 Calendar"])

# ============================================================================
# TAB 1: DASHBOARD (Original)
# ============================================================================
with tab1:
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    total_due = sum(item["amount"] for item in st.session_state.accounts if not item["paid"])
    total_revenue = sum(item["amount"] for item in st.session_state.revenue)
    total_card_balance = sum(item["balance"] for item in st.session_state.cards)
    cash_flow = total_revenue - total_due - total_card_balance
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Accounts Due", f"${total_due:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Card Balances", f"${total_card_balance:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Monthly Revenue", f"${total_revenue:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Cash Flow", f"${cash_flow:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent Activity Section
    st.markdown("---")
    st.markdown("### Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Recent Accounts")
        df_accounts = pd.DataFrame(st.session_state.accounts)
        if not df_accounts.empty:
            df_accounts = df_accounts.sort_values('date', ascending=False).head(3)
            for _, row in df_accounts.iterrows():
                status = "✅" if row['paid'] else "⏳"
                st.markdown(f"{status} **{row['description']}** - ${row['amount']:,.2f} ({row['date']})")
    
    with col2:
        st.markdown("#### Recent Revenue")
        df_revenue = pd.DataFrame(st.session_state.revenue)
        if not df_revenue.empty:
            df_revenue = df_revenue.sort_values('date', ascending=False).head(3)
            for _, row in df_revenue.iterrows():
                st.markdown(f"💰 **{row['description']}** - ${row['amount']:,.2f} ({row['customer']})")
    
    # Charts Row
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Accounts by Category Pie Chart
        if df_accounts is not None and not df_accounts.empty:
            category_sum = df_accounts.groupby('category')['amount'].sum().reset_index()
            fig = go.Figure(data=[go.Pie(
                labels=category_sum['category'],
                values=category_sum['amount'],
                hole=0.3,
                marker_colors=['#ff6b35', '#ff8c5a', '#ffad7a', '#ffce9a']
            )])
            fig.update_layout(title='Accounts by Category', height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue Bar Chart
        if df_revenue is not None and not df_revenue.empty:
            fig = go.Figure(data=[go.Bar(
                x=df_revenue['description'],
                y=df_revenue['amount'],
                marker_color='#2ecc71'
            )])
            fig.update_layout(title='Revenue by Load', height=350, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 2: CARDS (Original)
# ============================================================================
with tab2:
    st.markdown("## 💳 Cards")
    
    # Card Statistics
    total_balance = sum(card["balance"] for card in st.session_state.cards)
    total_limit = sum(card["limit"] for card in st.session_state.cards)
    utilization = (total_balance / total_limit * 100) if total_limit > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Balance", f"${total_balance:,.2f}")
    col2.metric("Total Limit", f"${total_limit:,.2f}")
    col3.metric("Utilization", f"{utilization:.1f}%")
    
    st.markdown("---")
    
    # Add Card Form
    with st.expander("➕ Add New Card"):
        with st.form("add_card"):
            col1, col2 = st.columns(2)
            with col1:
                card_type = st.selectbox("Card Type", ["Fuel", "Fleet", "Corporate", "Other"])
                card_number = st.text_input("Card Number (last 4 digits)", max_chars=4)
            with col2:
                balance = st.number_input("Current Balance", min_value=0.0, step=10.0)
                limit = st.number_input("Credit Limit", min_value=0.0, step=100.0)
            due_date = st.date_input("Due Date", value=datetime.now())
            
            if st.form_submit_button("Add Card"):
                st.session_state.cards.append({
                    "card_type": card_type,
                    "card_number": f"**** {card_number}" if card_number else "**** ****",
                    "balance": balance,
                    "limit": limit,
                    "due_date": due_date.strftime('%Y-%m-%d')
                })
                st.success("Card added!")
                st.rerun()
    
    # Display Cards
    for idx, card in enumerate(st.session_state.cards):
        with st.container():
            st.markdown(f"""
            <div class='card-item'>
                <div style='display: flex; justify-content: space-between;'>
                    <span><strong>{card['card_type']} Card</strong> {card['card_number']}</span>
                    <span style='color: #ff6b35;'><strong>${card['balance']:,.2f}</strong></span>
                </div>
                <div style='display: flex; justify-content: space-between; font-size: 0.9rem; color: #666;'>
                    <span>Limit: ${card['limit']:,.2f}</span>
                    <span>Due: {card['due_date']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([0.9, 0.1])
            with col2:
                if st.button("🗑️", key=f"del_card_{idx}"):
                    st.session_state.cards.pop(idx)
                    st.rerun()

# ============================================================================
# TAB 3: ACCOUNTS (Original - renamed from Bills)
# ============================================================================
with tab3:
    st.markdown("## 💰 Accounts")
    
    # Add Account Section
    with st.expander("➕ Add New Account"):
        with st.form("add_account"):
            col1, col2 = st.columns(2)
            
            with col1:
                acc_date = st.date_input("Due Date", value=datetime.now())
                acc_desc = st.text_input("Description")
            
            with col2:
                acc_amount = st.number_input("Amount", min_value=0.0, step=10.0)
                acc_category = st.selectbox("Category", ["Loan", "Fuel", "Insurance", "Maintenance", "Other"])
            
            if st.form_submit_button("Add Account"):
                st.session_state.accounts.append({
                    "date": acc_date.strftime('%Y-%m-%d'),
                    "description": acc_desc,
                    "amount": acc_amount,
                    "category": acc_category,
                    "paid": False
                })
                st.success("Account added!")
                st.rerun()
    
    # Accounts Table
    if st.session_state.accounts:
        df_accounts = pd.DataFrame(st.session_state.accounts)
        df_accounts['date'] = pd.to_datetime(df_accounts['date'])
        df_accounts = df_accounts.sort_values('date')
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_paid = st.checkbox("Show paid accounts", value=True)
        
        # Display accounts
        for idx, account in enumerate(st.session_state.accounts):
            if filter_paid or not account['paid']:
                col_a, col_b, col_c, col_d, col_e = st.columns([2, 1, 1.5, 0.8, 0.5])
                
                with col_a:
                    st.markdown(f"**{account['description']}**")
                    st.caption(account['category'])
                
                with col_b:
                    st.markdown(f"**${account['amount']:,.2f}**")
                
                with col_c:
                    st.markdown(f"Due: {account['date']}")
                
                with col_d:
                    paid = st.checkbox("Paid", value=account['paid'], key=f"paid_{idx}")
                    if paid != account['paid']:
                        account['paid'] = paid
                        st.rerun()
                
                with col_e:
                    if st.button("🗑️", key=f"del_acc_{idx}"):
                        st.session_state.accounts.pop(idx)
                        st.rerun()
    else:
        st.info("No accounts yet. Add your first account above.")

# ============================================================================
# TAB 4: REVENUE (Original)
# ============================================================================
with tab4:
    st.markdown("## 📈 Revenue")
    
    # Add Revenue Section
    with st.expander("➕ Add Revenue"):
        with st.form("add_revenue"):
            col1, col2 = st.columns(2)
            
            with col1:
                rev_date = st.date_input("Date", value=datetime.now())
                rev_desc = st.text_input("Description")
            
            with col2:
                rev_amount = st.number_input("Amount", min_value=0.0, step=10.0)
                rev_customer = st.text_input("Customer")
            
            if st.form_submit_button("Add Revenue"):
                st.session_state.revenue.append({
                    "date": rev_date.strftime('%Y-%m-%d'),
                    "description": rev_desc,
                    "amount": rev_amount,
                    "customer": rev_customer
                })
                st.success("Revenue added!")
                st.rerun()
    
    # Revenue Table
    if st.session_state.revenue:
        df_revenue = pd.DataFrame(st.session_state.revenue)
        df_revenue['date'] = pd.to_datetime(df_revenue['date'])
        df_revenue = df_revenue.sort_values('date', ascending=False)
        
        # Summary metrics
        total_rev = df_revenue['amount'].sum()
        avg_rev = df_revenue['amount'].mean()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"${total_rev:,.2f}")
        col2.metric("Average per Load", f"${avg_rev:,.2f}")
        col3.metric("Number of Loads", len(df_revenue))
        
        st.markdown("---")
        
        # Revenue entries
        for idx, rev in enumerate(st.session_state.revenue):
            col_a, col_b, col_c, col_d = st.columns([2, 1, 2, 0.5])
            
            with col_a:
                st.markdown(f"**{rev['description']}**")
            with col_b:
                st.markdown(f"**${rev['amount']:,.2f}**")
            with col_c:
                st.markdown(f"{rev['date']} - {rev['customer']}")
            with col_d:
                if st.button("🗑️", key=f"del_rev_{idx}"):
                    st.session_state.revenue.pop(idx)
                    st.rerun()
    else:
        st.info("No revenue yet. Add your first revenue entry above.")

# ============================================================================
# TAB 5: CALENDAR (New)
# ============================================================================
with tab5:
    st.markdown("## 📅 Calendar")
    
    # Month selector
    col1, col2, col3 = st.columns([1, 2, 1])
    current_month = datetime.now().month
    
    with col1:
        if st.button("◀ Previous"):
            st.session_state.cal_month = (st.session_state.get('cal_month', current_month) - 2) % 12 + 1
            st.rerun()
    
    with col2:
        selected_month = st.selectbox(
            "Select Month",
            options=range(1, 13),
            format_func=lambda x: calendar.month_name[x],
            index=st.session_state.get('cal_month', current_month) - 1
        )
        st.session_state.cal_month = selected_month
    
    with col3:
        if st.button("Next ▶"):
            st.session_state.cal_month = (st.session_state.get('cal_month', current_month)) % 12 + 1
            st.rerun()
    
    # Calendar grid
    year = datetime.now().year
    month = st.session_state.get('cal_month', current_month)
    cal = calendar.monthcalendar(year, month)
    
    # Day headers
    cols = st.columns(7)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for i, day in enumerate(days):
        cols[i].write(f"**{day}**")
    
    # Calendar days
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day != 0:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    events = [e for e in st.session_state.calendar_events if e["date"] == date_str]
                    
                    # Day number
                    st.write(f"**{day}**")
                    
                    # Events
                    for event in events:
                        color = {
                            "Maintenance": "#f39c12",
                            "Compliance": "#3498db",
                            "Dispatch": "#2ecc71",
                            "Financial": "#e74c3c"
                        }.get(event["type"], "#95a5a6")
                        
                        st.markdown(
                            f"<div style='background:{color}; color:white; padding:2px 5px; "
                            f"border-radius:3px; font-size:0.7rem; margin-bottom:2px;'>{event['event']}</div>",
                            unsafe_allow_html=True
                        )
    
    # Add Event Section
    st.markdown("---")
    st.markdown("### Add Calendar Event")
    
    with st.form("add_calendar_event"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            event_date = st.date_input("Date", value=datetime.now())
        with col2:
            event_desc = st.text_input("Event Description")
        with col3:
            event_type = st.selectbox("Type", ["Maintenance", "Compliance", "Dispatch", "Financial", "Personal"])
        
        if st.form_submit_button("Add Event"):
            if event_desc:
                st.session_state.calendar_events.append({
                    "date": event_date.strftime('%Y-%m-%d'),
                    "event": event_desc,
                    "type": event_type
                })
                st.success("Event added!")
                st.rerun()
    
    # Event List
    st.markdown("### Upcoming Events")
    if st.session_state.calendar_events:
        events_df = pd.DataFrame(st.session_state.calendar_events)
        events_df = events_df.sort_values('date')
        
        for idx, row in events_df.iterrows():
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.write(f"**{row['date']}** - {row['event']}")
            with col_b:
                st.write(f"({row['type']})")
            with col_c:
                if st.button("Delete", key=f"del_cal_{idx}"):
                    st.session_state.calendar_events.pop(idx)
                    st.rerun()
    else:
        st.info("No events scheduled")
