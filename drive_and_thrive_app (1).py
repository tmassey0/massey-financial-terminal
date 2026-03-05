import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
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
    
    # Accounts Payable (what you owe)
    st.session_state.accounts_payable = [
        {"id": "ap1", "name": "Truck Payment", "amount": 850.00, "due_date": "2026-03-15", "category": "Loan", "vendor": "Ford Credit", "paid": False},
        {"id": "ap2", "name": "Fuel Card", "amount": 1250.00, "due_date": "2026-03-10", "category": "Fuel", "vendor": "FleetCor", "paid": False},
        {"id": "ap3", "name": "Insurance", "amount": 450.00, "due_date": "2026-03-20", "category": "Insurance", "vendor": "Progressive", "paid": True},
        {"id": "ap4", "name": "Truck Repair", "amount": 675.00, "due_date": "2026-03-25", "category": "Maintenance", "vendor": "Speedco", "paid": False},
    ]
    
    # Accounts Receivable (what others owe you)
    st.session_state.accounts_receivable = [
        {"id": "ar1", "name": "ABC Logistics", "amount": 3200.00, "due_date": "2026-03-05", "job": "Cross-country load", "customer": "ABC Logistics", "paid": False},
        {"id": "ar2", "name": "XYZ Shipping", "amount": 1850.00, "due_date": "2026-03-12", "job": "Local delivery", "customer": "XYZ Shipping", "paid": False},
        {"id": "ar3", "name": "123 Transport", "amount": 2750.00, "due_date": "2026-03-18", "job": "Refrigerated load", "customer": "123 Transport", "paid": True},
        {"id": "ar4", "name": "Fast Freight", "amount": 1950.00, "due_date": "2026-03-22", "job": "Express delivery", "customer": "Fast Freight", "paid": False},
    ]
    
    # Revenue entries
    st.session_state.revenue = [
        {"date": "2026-03-01", "description": "Load #1234", "amount": 2450.00, "customer": "ABC Logistics"},
        {"date": "2026-03-02", "description": "Load #1235", "amount": 1875.00, "customer": "XYZ Shipping"},
        {"date": "2026-03-03", "description": "Load #1236", "amount": 3120.00, "customer": "123 Transport"},
    ]
    
    # Calendar events (editable)
    st.session_state.calendar_events = [
        {"id": "cal1", "title": "Oil Change - Pete 579", "date": "2026-03-10", "type": "maintenance", "notes": "Due at 15,000 miles"},
        {"id": "cal2", "title": "DOT Inspection Due", "date": "2026-03-15", "type": "compliance", "notes": "Annual inspection"},
        {"id": "cal3", "title": "Load Pickup - Chicago", "date": "2026-03-08", "type": "dispatch", "notes": "Pick up at 0800"},
        {"id": "cal4", "title": "Payment Due - Truck Loan", "date": "2026-03-15", "type": "financial", "notes": "$850"},
        {"id": "cal5", "title": "Fuel Card Statement", "date": "2026-03-20", "type": "financial", "notes": "Review and pay"},
    ]

# Custom CSS
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1a2a3a 0%, #2c3e50 100%);
    }
    
    /* Cards */
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #ff6b35;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Calendar styles */
    .calendar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .weekday-header {
        text-align: center;
        font-weight: bold;
        color: #ff6b35;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .calendar-day {
        min-height: 100px;
        background: #f8f9fa;
        border-radius: 8px;
        padding: 8px;
        border: 1px solid #e0e0e0;
        transition: all 0.2s;
    }
    
    .calendar-day:hover {
        background: #fff3e0;
        border-color: #ff6b35;
        cursor: pointer;
    }
    
    .calendar-day.empty {
        background: transparent;
        border: 1px dashed #e0e0e0;
    }
    
    .day-number {
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
    }
    
    .calendar-event {
        background: #ff6b35;
        color: white;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 0.7rem;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .calendar-event:hover {
        transform: scale(1.02);
        background: #ff5722;
    }
    
    .calendar-event.maintenance { background: #f39c12; }
    .calendar-event.compliance { background: #3498db; }
    .calendar-event.dispatch { background: #2ecc71; }
    .calendar-event.financial { background: #e74c3c; }
    
    /* Account cards */
    .account-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .account-card.payable {
        border-left-color: #e74c3c;
    }
    
    .account-card.receivable {
        border-left-color: #2ecc71;
    }
    
    .account-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .account-name {
        font-weight: bold;
        color: #333;
    }
    
    .account-amount {
        font-weight: bold;
        color: #2ecc71;
    }
    
    .account-amount.negative {
        color: #e74c3c;
    }
    
    .badge {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: bold;
    }
    
    .badge.paid {
        background: #d4edda;
        color: #155724;
    }
    
    .badge.unpaid {
        background: #f8d7da;
        color: #721c24;
    }
    
    .badge.overdue {
        background: #ffc107;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<h1 style='color: white;'>🚛 Drive & Thrive Financial Terminal</h1>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<p style='color: white; text-align: right;'>{datetime.now().strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📅 Calendar", "💰 Accounts", "📈 Revenue"])

# ============================================================================
# TAB 1: DASHBOARD
# ============================================================================
with tab1:
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    total_receivable = sum(item["amount"] for item in st.session_state.accounts_receivable if not item["paid"])
    total_payable = sum(item["amount"] for item in st.session_state.accounts_payable if not item["paid"])
    total_revenue = sum(item["amount"] for item in st.session_state.revenue)
    cash_flow = total_revenue - total_payable
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Accounts Receivable", f"${total_receivable:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Accounts Payable", f"${total_payable:,.2f}", delta=f"-${total_payable:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Monthly Revenue", f"${total_revenue:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Cash Flow", f"${cash_flow:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        # Payables vs Receivables Pie Chart
        fig = go.Figure(data=[go.Pie(
            labels=['Receivables', 'Payables'],
            values=[total_receivable, total_payable],
            marker_colors=['#2ecc71', '#e74c3c']
        )])
        fig.update_layout(title='Accounts Overview', height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Upcoming Payments Bar Chart
        upcoming = []
        for item in st.session_state.accounts_payable:
            if not item["paid"]:
                upcoming.append({
                    "name": item["name"],
                    "amount": item["amount"],
                    "due": item["due_date"]
                })
        
        if upcoming:
            df_upcoming = pd.DataFrame(upcoming)
            fig = go.Figure(data=[go.Bar(
                x=df_upcoming['name'],
                y=df_upcoming['amount'],
                marker_color='#ff6b35'
            )])
            fig.update_layout(title='Upcoming Payments', height=350, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No upcoming payments")

# ============================================================================
# TAB 2: CALENDAR (EDITABLE)
# ============================================================================
with tab2:
    st.markdown("## 📅 Editable Calendar")
    
    # Calendar controls
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    
    with col1:
        if st.button("◀ Previous Month"):
            st.session_state.calendar_month = (st.session_state.get('calendar_month', datetime.now().month) - 2) % 12 + 1
    with col2:
        if st.button("Next Month ▶"):
            st.session_state.calendar_month = (st.session_state.get('calendar_month', datetime.now().month)) % 12 + 1
    with col3:
        selected_date = st.date_input("Jump to date", datetime.now())
    with col4:
        if st.button("➕ Add Event"):
            st.session_state.show_add_event = True
    
    # Get current month/year
    today = datetime.now()
    month = st.session_state.get('calendar_month', today.month)
    year = today.year
    
    # Month and Year display
    st.markdown(f"### {calendar.month_name[month]} {year}")
    
    # Calendar grid
    cal = calendar.monthcalendar(year, month)
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Weekday headers
    cols = st.columns(7)
    for i, weekday in enumerate(weekdays):
        with cols[i]:
            st.markdown(f"<div class='weekday-header'>{weekday}</div>", unsafe_allow_html=True)
    
    # Calendar days
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown("<div class='calendar-day empty'></div>", unsafe_allow_html=True)
                else:
                    # Get events for this day
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    day_events = [e for e in st.session_state.calendar_events if e["date"] == date_str]
                    
                    # Create day cell
                    day_html = f"<div class='calendar-day' onclick=''>"
                    day_html += f"<div class='day-number'>{day}</div>"
                    
                    for event in day_events:
                        day_html += f"<div class='calendar-event {event['type']}' title='{event['notes']}'>{event['title']}</div>"
                    
                    day_html += "</div>"
                    st.markdown(day_html, unsafe_allow_html=True)
                    
                    # Edit button for the day
                    if st.button(f"✏️ Edit {month}/{day}", key=f"edit_day_{month}_{day}"):
                        st.session_state.editing_date = date_str
                        st.rerun()
    
    # Event Editor Modal (using expander as modal replacement)
    if st.session_state.get('show_add_event') or st.session_state.get('editing_date'):
        with st.expander("📝 Edit Calendar Events", expanded=True):
            date_to_edit = st.session_state.get('editing_date', selected_date.strftime('%Y-%m-%d'))
            
            st.markdown(f"### Events for {date_to_edit}")
            
            # Show existing events for this date
            date_events = [e for e in st.session_state.calendar_events if e["date"] == date_to_edit]
            
            for i, event in enumerate(date_events):
                col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 1])
                with col1:
                    new_title = st.text_input("Title", value=event["title"], key=f"title_{event['id']}")
                with col2:
                    new_type = st.selectbox("Type", 
                        ["maintenance", "compliance", "dispatch", "financial"],
                        index=["maintenance", "compliance", "dispatch", "financial"].index(event["type"]),
                        key=f"type_{event['id']}")
                with col3:
                    new_notes = st.text_input("Notes", value=event["notes"], key=f"notes_{event['id']}")
                with col4:
                    if st.button("💾", key=f"save_{event['id']}"):
                        # Update event
                        for e in st.session_state.calendar_events:
                            if e["id"] == event["id"]:
                                e["title"] = new_title
                                e["type"] = new_type
                                e["notes"] = new_notes
                                break
                        st.success("Updated!")
                        st.rerun()
                with col5:
                    if st.button("🗑️", key=f"del_{event['id']}"):
                        st.session_state.calendar_events = [e for e in st.session_state.calendar_events if e["id"] != event["id"]]
                        st.rerun()
            
            # Add new event form
            st.markdown("---")
            st.markdown("#### Add New Event")
            with st.form("add_event_form"):
                new_title = st.text_input("Event Title")
                new_type = st.selectbox("Event Type", ["maintenance", "compliance", "dispatch", "financial"])
                new_notes = st.text_input("Notes")
                
                if st.form_submit_button("Add Event"):
                    new_event = {
                        "id": f"cal{len(st.session_state.calendar_events) + 1}",
                        "title": new_title,
                        "date": date_to_edit,
                        "type": new_type,
                        "notes": new_notes
                    }
                    st.session_state.calendar_events.append(new_event)
                    st.session_state.show_add_event = False
                    st.session_state.editing_date = None
                    st.success("Event added!")
                    st.rerun()
            
            if st.button("Close Editor"):
                st.session_state.show_add_event = False
                st.session_state.editing_date = None
                st.rerun()

# ============================================================================
# TAB 3: ACCOUNTS (Payable & Receivable)
# ============================================================================
with tab3:
    st.markdown("## 💰 Accounts")
    
    col1, col2 = st.columns(2)
    
    # Accounts Payable
    with col1:
        st.markdown("### 💸 Accounts Payable (What You Owe)")
        
        # Add new payable
        with st.expander("➕ Add New Payable"):
            with st.form("add_payable"):
                name = st.text_input("Bill Name")
                amount = st.number_input("Amount", min_value=0.0, step=10.0)
                due_date = st.date_input("Due Date")
                category = st.selectbox("Category", ["Loan", "Fuel", "Insurance", "Maintenance", "Other"])
                vendor = st.text_input("Vendor")
                
                if st.form_submit_button("Add Payable"):
                    new_id = f"ap{len(st.session_state.accounts_payable) + 1}"
                    st.session_state.accounts_payable.append({
                        "id": new_id,
                        "name": name,
                        "amount": amount,
                        "due_date": due_date.strftime('%Y-%m-%d'),
                        "category": category,
                        "vendor": vendor,
                        "paid": False
                    })
                    st.success("Added!")
                    st.rerun()
        
        # List payables
        for payable in st.session_state.accounts_payable:
            due_date = datetime.strptime(payable["due_date"], '%Y-%m-%d')
            is_overdue = due_date < datetime.now() and not payable["paid"]
            
            with st.container():
                col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
                
                with col_a:
                    status_emoji = "✅" if payable["paid"] else "⏳"
                    st.markdown(f"{status_emoji} **{payable['name']}**")
                    st.caption(f"{payable['vendor']} • {payable['category']}")
                
                with col_b:
                    st.markdown(f"**${payable['amount']:,.2f}**")
                    st.caption(f"Due: {payable['due_date']}")
                
                with col_c:
                    if is_overdue:
                        st.markdown("🔴 **OVERDUE**")
                    else:
                        days_left = (due_date - datetime.now()).days
                        st.caption(f"{days_left} days left")
                
                with col_d:
                    paid = st.checkbox("Paid", value=payable["paid"], key=f"payable_paid_{payable['id']}")
                    if paid != payable["paid"]:
                        payable["paid"] = paid
                        st.rerun()
                    
                    if st.button("🗑️", key=f"del_payable_{payable['id']}"):
                        st.session_state.accounts_payable = [p for p in st.session_state.accounts_payable if p["id"] != payable["id"]]
                        st.rerun()
    
    # Accounts Receivable
    with col2:
        st.markdown("### 💵 Accounts Receivable (What You're Owed)")
        
        # Add new receivable
        with st.expander("➕ Add New Receivable"):
            with st.form("add_receivable"):
                name = st.text_input("Job/Invoice Name")
                amount = st.number_input("Amount", min_value=0.0, step=10.0)
                due_date = st.date_input("Due Date")
                customer = st.text_input("Customer")
                job = st.text_input("Job Description")
                
                if st.form_submit_button("Add Receivable"):
                    new_id = f"ar{len(st.session_state.accounts_receivable) + 1}"
                    st.session_state.accounts_receivable.append({
                        "id": new_id,
                        "name": name,
                        "amount": amount,
                        "due_date": due_date.strftime('%Y-%m-%d'),
                        "customer": customer,
                        "job": job,
                        "paid": False
                    })
                    st.success("Added!")
                    st.rerun()
        
        # List receivables
        for receivable in st.session_state.accounts_receivable:
            due_date = datetime.strptime(receivable["due_date"], '%Y-%m-%d')
            is_overdue = due_date < datetime.now() and not receivable["paid"]
            
            with st.container():
                col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
                
                with col_a:
                    status_emoji = "✅" if receivable["paid"] else "⏳"
                    st.markdown(f"{status_emoji} **{receivable['name']}**")
                    st.caption(f"{receivable['customer']} • {receivable['job']}")
                
                with col_b:
                    st.markdown(f"**${receivable['amount']:,.2f}**")
                    st.caption(f"Due: {receivable['due_date']}")
                
                with col_c:
                    if is_overdue:
                        st.markdown("🔴 **OVERDUE**")
                    else:
                        days_left = (due_date - datetime.now()).days
                        st.caption(f"{days_left} days left")
                
                with col_d:
                    paid = st.checkbox("Paid", value=receivable["paid"], key=f"receivable_paid_{receivable['id']}")
                    if paid != receivable["paid"]:
                        receivable["paid"] = paid
                        st.rerun()
                    
                    if st.button("🗑️", key=f"del_receivable_{receivable['id']}"):
                        st.session_state.accounts_receivable = [r for r in st.session_state.accounts_receivable if r["id"] != receivable["id"]]
                        st.rerun()

# ============================================================================
# TAB 4: REVENUE
# ============================================================================
with tab4:
    st.markdown("## 📈 Revenue Tracker")
    
    # Add Revenue Entry
    with st.expander("➕ Add Revenue Entry"):
        with st.form("add_revenue"):
            col1, col2 = st.columns(2)
            with col1:
                rev_date = st.date_input("Date")
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
    df_revenue = pd.DataFrame(st.session_state.revenue)
    if not df_revenue.empty:
        df_revenue['date'] = pd.to_datetime(df_revenue['date'])
        df_revenue = df_revenue.sort_values('date', ascending=False)
        
        # Monthly summary
        st.markdown("### Monthly Summary")
        df_revenue['month'] = df_revenue['date'].dt.strftime('%Y-%m')
        monthly_summary = df_revenue.groupby('month')['amount'].sum().reset_index()
        
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure(data=[go.Bar(
                x=monthly_summary['month'],
                y=monthly_summary['amount'],
                marker_color='#2ecc71'
            )])
            fig.update_layout(title='Monthly Revenue', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Customer breakdown
            customer_summary = df_revenue.groupby('customer')['amount'].sum().reset_index()
            fig = go.Figure(data=[go.Pie(
                labels=customer_summary['customer'],
                values=customer_summary['amount']
            )])
            fig.update_layout(title='Revenue by Customer', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Revenue table
        st.markdown("### Revenue Entries")
        st.dataframe(
            df_revenue[['date', 'description', 'customer', 'amount']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No revenue entries yet. Add your first revenue entry above.")
