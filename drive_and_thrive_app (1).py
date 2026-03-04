import os
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# 0. DATA DIRECTORY
# =========================
# Adjust this path to wherever your Excel files actually live.
# Example: data folder next to this script.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# Optional: show where we are and what files exist
st.write("Working directory:", SCRIPT_DIR)
st.write("Data directory:", DATA_DIR)
st.write("Data files:", os.listdir(DATA_DIR) if os.path.isdir(DATA_DIR) else "NO DATA DIR FOUND")

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

def load_and_fix(filename, sheet, skip, cols):
    """Load Excel sheet from DATA_DIR, clean columns, fill NaNs; on error show Streamlit error."""
    try:
        full_path = os.path.join(DATA_DIR, filename)
        df = pd.read_excel(full_path, sheet_name=sheet, skiprows=skip)
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna(0)
    except Exception as e:
        st.error(f"Error loading {filename} / {sheet}: {e}")
        return pd.DataFrame(columns=cols)

# =========================
# 3. PERSISTENT MEMORY
# =========================

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
    st.session_state.uber = load_and_fix(
        "Terrance-Uber-Tracker-2.xlsx",
        "UBER EARNINGS - 2026 ANNUAL SUMMARY",
        3,
        ["Month", "Total Hours", "Total Earnings", "Monthly Goal", "Difference", "Status"],
    )

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

    if total_liabilities > 0:
        months = ["MAR", "APR", "MAY", "JUN", "JUL"]
        projection = [max(0, total_liabilities - i * 1344) for i in range(len(months))]

        fig = px.line(
            x=months,
            y=projection,
            markers=True,
            labels={"x": "Month", "y": "Projected Liabilities"},
            title="Liability Reduction Projection",
        )
        fig.update_traces(line=dict(color="#0EA5E9", width=4))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No card data found yet to project liabilities.")

# =========================
# 6. CARDS & LIQUIDITY TAB
# =========================
with tabs[1]:
    st.subheader("Manage Credit Portfolio")

    st.session_state.cards = st.data_editor(
        st.session_state.cards,
        num_rows="dynamic",
        use_container_width=True,
        key="cards_editor",
    )

    if st.button("Save Cards & Refresh"):
        st.rerun()

# =========================
# 7. BILL MASTER TAB
# =========================
with tabs[2]:
    st.subheader("Manage Bills")

    st.session_state.bills = st.data_editor(
        st.session_state.bills,
        num_rows="dynamic",
        use_container_width=True,
        key="bills_editor",
    )

    if st.button("Save Bills & Refresh"):
        st.rerun()

# =========================
# 8. UBER PERFORMANCE TAB
# =========================
with tabs[3]:
    st.subheader("Edit Uber Annual Performance")
    st.info(
        "Edit any cell directly, use (+) at the bottom for new rows, then click "
        "'Commit & Recalculate Difference'."
    )

    uber_columns = list(st.session_state.uber.columns)

    column_config = {}
    if "Total Hours" in uber_columns:
        column_config["Total Hours"] = st.column_config.NumberColumn(disabled=False)
    if "Total Earnings" in uber_columns:
        column_config["Total Earnings"] = st.column_config.NumberColumn(
            disabled=False, format="$%0.2f"
        )
    if "Monthly Goal" in uber_columns:
        column_config["Monthly Goal"] = st.column_config.NumberColumn(
            disabled=False, format="$%0.2f"
        )
    if "Difference" in uber_columns:
        column_config["Difference"] = st.column_config.NumberColumn(
            disabled=False, format="$%0.2f"
        )

    edited_uber = st.data_editor(
        st.session_state.uber,
        num_rows="dynamic",
        use_container_width=True,
        key="uber_editor",
        column_config=column_config,
    )

    if st.button("Commit & Recalculate Difference"):
        if {"Total Earnings", "Monthly Goal"}.issubset(edited_uber.columns):
            edited_uber["Difference"] = pd.to_numeric(
                edited_uber["Total Earnings"], errors="coerce"
            ) - pd.to_numeric(edited_uber["Monthly Goal"], errors="coerce")
        st.session_state.uber = edited_uber
        st.rerun()
