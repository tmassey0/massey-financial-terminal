import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import calendar

# Page config
st.set_page_config(
    page_title="Edible Bill Payment Calendar",
    page_icon="🍽️",
    layout="wide"
)

# Initialize session state
if 'accounts' not in st.session_state:
    # Sample data
    st.session_state.accounts = [
        {"id": "1", "name": "Rent", "amount": 2500.00, "due_day": 1, "category": "Rent/Mortgage", "notes": ""},
        {"id": "2", "name": "Internet", "amount": 85.00, "due_day": 15, "category": "Internet", "notes": "Spectrum"},
        {"id": "3", "name": "Electricity", "amount": 150.00, "due_day": 10, "category": "Utilities", "notes": ""},
        {"id": "4", "name": "Netflix", "amount": 15.99, "due_day": 20, "category": "Subscriptions", "notes": ""},
        {"id": "5", "name": "Phone", "amount": 89.00, "due_day": 25, "category": "Phone", "notes": "Verizon"},
        {"id": "6", "name": "Car Insurance", "amount": 120.00, "due_day": 5, "category": "Insurance", "notes": ""}
    ]

if 'payments' not in st.session_state:
    st.session_state.payments = {}  # Format: {"account_id-month-year": {"paid": bool, "amount": float}}

if 'current_year' not in st.session_state:
    st.session_state.current_year = 2026

if 'selected_month' not in st.session_state:
    st.session_state.selected_month = None

if 'selected_year' not in st.session_state:
    st.session_state.selected_year = None

if 'editing_bill' not in st.session_state:
    st.session_state.editing_bill = None

# Helper functions
def get_payment_key(account_id, month, year):
    return f"{account_id}-{month}-{year}"

def get_bill_amount(account, month, year):
    key = get_payment_key(account["id"], month, year)
    if key in st.session_state.payments and "amount" in st.session_state.payments[key]:
        return st.session_state.payments[key]["amount"]
    return account["amount"]

def is_bill_paid(account_id, month, year):
    key = get_payment_key(account_id, month, year)
    return st.session_state.payments.get(key, {}).get("paid", False)

def set_bill_paid(account_id, month, year, paid):
    key = get_payment_key(account_id, month, year)
    if key not in st.session_state.payments:
        st.session_state.payments[key] = {}
    st.session_state.payments[key]["paid"] = paid

def set_bill_amount(account_id, month, year, amount):
    key = get_payment_key(account_id, month, year)
    if key not in st.session_state.payments:
        st.session_state.payments[key] = {}
    st.session_state.payments[key]["amount"] = amount

def add_account(name, amount, due_day, category, notes=""):
    new_id = str(len(st.session_state.accounts) + 1)
    st.session_state.accounts.append({
        "id": new_id,
        "name": name,
        "amount": amount,
        "due_day": due_day,
        "category": category,
        "notes": notes
    })

def delete_account(account_id):
    st.session_state.accounts = [a for a in st.session_state.accounts if a["id"] != account_id]
    # Clean up payments
    keys_to_delete = []
    for key in st.session_state.payments:
        if key.startswith(f"{account_id}-"):
            keys_to_delete.append(key)
    for key in keys_to_delete:
        del st.session_state.payments[key]

# Month names
month_names = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-header {
        color: white;
        text-align: center;
        padding: 1rem;
        font-size: 2.5rem;
    }
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .month-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .month-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    .month-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .month-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
    }
    .month-total {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .bill-item {
        background: #f8f9fa;
        border-radius: 5px;
        padding: 0.3rem 0.5rem;
        margin-bottom: 0.3rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
        border-left: 3px solid #667eea;
    }
    .bill-item.paid {
        opacity: 0.6;
        border-left-color: #4caf50;
        background: #f1f8e9;
    }
    .bill-item.paid .bill-amount {
        text-decoration: line-through;
        color: #666;
    }
    .bill-name {
        font-weight: 600;
        color: #333;
    }
    .bill-date {
        font-size: 0.75rem;
        color: #666;
    }
    .bill-amount {
        font-weight: bold;
        color: #2e7d32;
    }
    .account-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .account-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .account-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #333;
    }
    .account-category {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.75rem;
    }
    .account-details {
        display: flex;
        justify-content: space-between;
        color: #666;
        font-size: 0.9rem;
    }
    .account-amount {
        color: #2e7d32;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>🍽️ Edible Bill Payment Calendar</h1>", unsafe_allow_html=True)

# Year selector and Add Account button
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("← Previous Year"):
        st.session_state.current_year -= 1
        st.rerun()
with col2:
    st.markdown(f"<h2 style='text-align: center; color: white;'>{st.session_state.current_year}</h2>", unsafe_allow_html=True)
with col3:
    if st.button("Next Year →"):
        st.session_state.current_year += 1
        st.rerun()

# Stats Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container():
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.metric("Total Accounts", len(st.session_state.accounts))
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        avg_amount = sum(a["amount"] for a in st.session_state.accounts) / max(len(st.session_state.accounts), 1)
        st.metric("Monthly Average", f"${avg_amount:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

with col3:
    with st.container():
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        current_month = datetime.now().month - 1
        paid_count = sum(1 for a in st.session_state.accounts 
                        if is_bill_paid(a["id"], current_month, st.session_state.current_year))
        st.metric("Paid This Month", paid_count)
        st.markdown("</div>", unsafe_allow_html=True)

with col4:
    with st.container():
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        today = datetime.now()
        upcoming = 0
        for account in st.session_state.accounts:
            if not is_bill_paid(account["id"], today.month - 1, today.year):
                if account["due_day"] >= today.day and account["due_day"] <= today.day + 7:
                    upcoming += 1
        st.metric("Upcoming (7 days)", upcoming)
        st.markdown("</div>", unsafe_allow_html=True)

# Calendar Grid
st.markdown("### 📅 Calendar View")
calendar_cols = st.columns(3)

for month_idx in range(12):
    with calendar_cols[month_idx % 3]:
        # Get bills for this month
        month_bills = []
        for account in st.session_state.accounts:
            amount = get_bill_amount(account, month_idx, st.session_state.current_year)
            paid = is_bill_paid(account["id"], month_idx, st.session_state.current_year)
            month_bills.append({
                "id": account["id"],
                "name": account["name"],
                "amount": amount,
                "due_day": account["due_day"],
                "paid": paid,
                "category": account["category"]
            })
        
        month_bills.sort(key=lambda x: x["due_day"])
        unpaid_total = sum(b["amount"] for b in month_bills if not b["paid"])
        
        # Month card
        card_html = f"""
        <div class='month-card' onclick=''>
            <div class='month-header'>
                <span class='month-name'>{month_names[month_idx]}</span>
                <span class='month-total'>${unpaid_total:.2f}</span>
            </div>
            <div class='month-bills'>
        """
        
        for bill in month_bills[:3]:
            paid_class = "paid" if bill["paid"] else ""
            card_html += f"""
                <div class='bill-item {paid_class}'>
                    <div>
                        <div class='bill-name'>{bill['name']}</div>
                        <div class='bill-date'>Due: {bill['due_day']}</div>
                    </div>
                    <span class='bill-amount'>${bill['amount']:.2f}</span>
                </div>
            """
        
        if len(month_bills) > 3:
            card_html += f"<div style='text-align: center; color: #667eea;'>+{len(month_bills) - 3} more</div>"
        elif len(month_bills) == 0:
            card_html += "<div class='no-bills'>No bills</div>"
        
        card_html += "</div></div>"
        
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Month view button
        if st.button(f"View {month_names[month_idx]}", key=f"view_{month_idx}"):
            st.session_state.selected_month = month_idx
            st.session_state.selected_year = st.session_state.current_year
            st.rerun()

# Month Detail View (if selected)
if st.session_state.selected_month is not None:
    with st.expander(f"📆 {month_names[st.session_state.selected_month]} {st.session_state.selected_year} Details", expanded=True):
        month = st.session_state.selected_month
        year = st.session_state.selected_year
        
        # Get days in month
        days_in_month = calendar.monthrange(year, month + 1)[1]
        
        # Create daily view
        for day in range(1, days_in_month + 1):
            day_bills = []
            for account in st.session_state.accounts:
                if account["due_day"] == day:
                    amount = get_bill_amount(account, month, year)
                    paid = is_bill_paid(account["id"], month, year)
                    day_bills.append({
                        "id": account["id"],
                        "name": account["name"],
                        "amount": amount,
                        "paid": paid,
                        "category": account["category"]
                    })
            
            if day_bills:
                with st.container():
                    cols = st.columns([1, 4])
                    with cols[0]:
                        st.markdown(f"**Day {day}**")
                    with cols[1]:
                        for bill in day_bills:
                            col_a, col_b, col_c = st.columns([3, 1, 1])
                            with col_a:
                                st.write(f"{bill['name']} ({bill['category']})")
                            with col_b:
                                st.write(f"${bill['amount']:.2f}")
                            with col_c:
                                paid = st.checkbox(
                                    "Paid", 
                                    value=bill["paid"],
                                    key=f"paid_{bill['id']}_{month}_{year}_{day}"
                                )
                                if paid != bill["paid"]:
                                    set_bill_paid(bill["id"], month, year, paid)
                                    st.rerun()
        
        if st.button("Close Month View"):
            st.session_state.selected_month = None
            st.rerun()

# Accounts Management
st.markdown("---")
st.markdown("### 📋 Your Accounts")

# Add Account Form
with st.expander("➕ Add New Account", expanded=False):
    with st.form("add_account_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Account Name")
            amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
        with col2:
            due_day = st.number_input("Due Day (1-31)", min_value=1, max_value=31, step=1)
            category = st.selectbox("Category", [
                "Rent/Mortgage", "Utilities", "Internet", "Phone", 
                "Insurance", "Subscriptions", "Other"
            ])
        notes = st.text_area("Notes (optional)")
        
        if st.form_submit_button("Add Account"):
            if name and amount > 0:
                add_account(name, amount, due_day, category, notes)
                st.success("Account added!")
                st.rerun()
            else:
                st.error("Please fill in all required fields")

# Accounts List
accounts_cols = st.columns(2)
for idx, account in enumerate(st.session_state.accounts):
    with accounts_cols[idx % 2]:
        paid_this_month = is_bill_paid(account["id"], datetime.now().month - 1, datetime.now().year)
        
        card_html = f"""
        <div class='account-card'>
            <div class='account-header'>
                <span class='account-name'>{account['name']}</span>
                <span class='account-category'>{account['category']}</span>
            </div>
            <div class='account-details'>
                <span class='account-amount'>${account['amount']:.2f}</span>
                <span>Due: {account['due_day']}</span>
            </div>
        """
        if account['notes']:
            card_html += f"<div style='font-size: 0.85rem; color: #666; margin-top: 0.5rem;'>{account['notes']}</div>"
        card_html += "</div>"
        
        st.markdown(card_html, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✏️ Edit", key=f"edit_{account['id']}"):
                st.session_state.editing_bill = account
                st.rerun()
        with col2:
            if st.button("🗑️ Delete", key=f"del_{account['id']}"):
                delete_account(account['id'])
                st.rerun()
        with col3:
            paid_status = st.checkbox(
                "Paid this month",
                value=paid_this_month,
                key=f"monthly_paid_{account['id']}"
            )
            if paid_status != paid_this_month:
                set_bill_paid(account['id'], datetime.now().month - 1, datetime.now().year, paid_status)
                st.rerun()

# Edit Bill Modal (simulated with expander)
if st.session_state.editing_bill:
    with st.expander("✏️ Edit Account", expanded=True):
        account = st.session_state.editing_bill
        with st.form("edit_account_form"):
            name = st.text_input("Account Name", value=account["name"])
            amount = st.number_input("Amount ($)", value=account["amount"], min_value=0.0, step=0.01)
            due_day = st.number_input("Due Day", value=account["due_day"], min_value=1, max_value=31)
            category = st.selectbox("Category", 
                ["Rent/Mortgage", "Utilities", "Internet", "Phone", "Insurance", "Subscriptions", "Other"],
                index=["Rent/Mortgage", "Utilities", "Internet", "Phone", "Insurance", "Subscriptions", "Other"].index(account["category"])
            )
            notes = st.text_area("Notes", value=account.get("notes", ""))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Changes"):
                    # Update account
                    for a in st.session_state.accounts:
                        if a["id"] == account["id"]:
                            a["name"] = name
                            a["amount"] = amount
                            a["due_day"] = due_day
                            a["category"] = category
                            a["notes"] = notes
                            break
                    st.session_state.editing_bill = None
                    st.rerun()
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.editing_bill = None
                    st.rerun()
