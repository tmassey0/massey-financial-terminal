# 2. DATA LOAD ENGINE
def load_and_fix(file, sheet, skip, cols):
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        df.columns = [str(c).strip() for c in df.columns]
        return df.fillna(0)
    except Exception as e:
        st.error(f"Error loading {file} / {sheet}: {e}")
        return pd.DataFrame(columns=cols)

# 3. PERSISTENT MEMORY
if 'cards' not in st.session_state:
    st.session_state.cards = load_and_fix(
        "Terrance-Credit-Card-1.xlsx", "Credit Cards", 1,
        ["Bank Name", "Balance", "Limit"]
    )

if 'bills' not in st.session_state:
    st.session_state.bills = load_and_fix(
        "Terrance-Credit-Card-1.xlsx", "Bill Master List", 1,
        ["Bill Name", "Amount"]
    )

if 'uber' not in st.session_state:
    # Option A: use the annual summary (clean, tabular)
    st.session_state.uber = load_and_fix(
        "Terrance-Uber-Tracker-2.xlsx",
        "UBER EARNINGS - 2026 ANNUAL SUMMARY",  # exact sheet name
        3,
        ["Month", "Total Hours", "Total Earnings", "Monthly Goal", "Difference"]
    )
    # or Option B: a daily sheet once you decide the exact sheet_name
