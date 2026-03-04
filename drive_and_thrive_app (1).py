import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# 1. BRANDING & UI CONFIG
# =========================
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")

st.markdown(
    """
    <style>
        html, body, [class*="st-at"] {
            background-color: #0B0E14;
            color: #E2E8F0;
        }
        div[data-testid="stMetric"] {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 20px !important;
        }
        .stTabs [aria-selected="true"] {
            color: #38BDF8 !important;
            border-bottom: 2px solid #38BDF8 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# 2. DATA LOAD ENGINE
# =========================

def load_and_fix(file, sheet, skip, cols):
    """Load Excel sheet, clean columns, fill NaNs; on error show Streamlit error."""
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna(0)
    except Exception as e:
        st.error(f"Error loading {file} / {sheet}: {e}")
        return pd.DataFrame(columns=cols)

# =========================
# 3. PERSISTENT MEMORY
# =========================

# Make sure the .xlsx files are in the SAME folder as this file.
# Filenames must match exactly: Terrance-Credit-Card-1.xlsx, Terrance-Uber-Tracker-2.xlsx

if "cards" not in st.session_state:
    st.session_state.cards = load_and_fix(
        "Terrance-Credit-Card-1.xlsx",
        "Credit Cards",
        1,
        ["Bank Name", "Total Current Balance", "Credit Limit"],
    )

if "bills" not in st.session_state:
    st.session_state.bills = load_and_fix(
        "Terrance-Credit-Card-1.xlsx",
        "Bill Master List",
        1,
        ["Bill Name", "Amount", "Due Day", "Active"],
    )

if "uber" not in st.session_state:
    # Using the annual summary sheet for clean editing
    st.session_state.uber = load_and_fix(
        "Terrance-Uber-Tracker-2.xlsx",
        "UBER EARNINGS - 2026 ANNUAL SUMMARY",  # exact sheet name
        3,
        ["Month", "Total Hours", "Total Earnings", "Monthly Goal", "Difference", "Status"],
    )

# Shortcuts
cards_df = st.session_state.cards
bills_df = st.session_state.bills
uber_df = st.session_state.uber

# =========================
# 4. TITLE & TABS
# =========================

st.title("🏛️ Massey Strategic Capital Terminal")

tabs = st.tabs(
    [
        "📊 DASHBOARD",
        "💳 CARDS & LIQUIDITY",
        "📅 BILL MASTER",
        "🚖 UBER PERFORMANCE",
    ]
)

# =========================
# 5. DASHBOARD TAB
# =========================
with tabs[0]:
    st.subheader("Executive Overview")

    # Credit metrics
    # Try flexible column names in case headers differ slightly
    bal_col = next(
        (c for c in cards_df.columns if "Total Current Balance" in c or "Balance" in c),
        None,
    )
    lim_col = next(
        (c for c in cards_df.columns if "Credit Limit" in c or "Limit" in c),
        None,
    )

    total_liabilities = 0
    total_limit = 0
    utilization = 0

    if bal_col and lim_col:
        total_liabilities = pd.to_numeric(cards_df[bal_col], errors="coerce").sum()
        total_limit = pd.to_numeric(cards_df[lim_col], errors="coerce").sum()
        utilization = (total_liabilities / total_limit * 100) if total_limit > 0 else 0

    # Monthly burn from active bills
    if "Active" in bills_df.columns:
        active_mask = bills_df["Active"].astype(str).str.strip().str.lower().isin(
            ["yes", "true", "1"]
        )
        monthly_burn = pd.to_numeric(
            bills_df.loc[active_mask, "Amount"], errors="coerce"
        ).sum()
    else:
        monthly_burn = pd.to_numeric(bills_df.get("Amount", 0), errors="coerce").sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOTAL LIABILITIES", f"${total_liabilities:,.2f}")
    m2.metric(
        "AVERAGE UTILIZATION",
        f"{utilization:.1f}%" if total_limit > 0 else "N/A",
    )
    m3.metric("MONTHLY BURN (ACTIVE BILLS)", f"${monthly_burn:,.2f}")
    m4.metric("TARGET APR", "35.9%", "High Interest Risk")

    st.divider()

    #
