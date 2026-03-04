import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="MASSEY STRATEGIC CAPITAL", layout="wide")
st.markdown("""
<style>
    html, body, [class*="st-at"] { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA LOAD ENGINE ---
def load_excel_data(file, sheet, skip=0):
    try:
        df = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# --- 3. PERSISTENT MEMORY SETUP ---
# This part ENSURES the data stays editable and doesn't reset
if 'cards_df' not in st.session_state:
    st.session_state.cards_df = load_excel_data("Terrance Credit Card 1.xlsx", "Credit Cards", 1)
if 'bills_df' not in st.session_state:
    st.session_state.bills_df = load_excel_data("Terrance Credit Card 1.xlsx", "Bill Master List", 1)
if 'uber_df' not in st.session_state:
    st.session_state.uber_df = load_excel_data("Terrance Uber Tracker.xlsx", "March", 3)

# --- 4. THE COMMAND CENTER ---
st.title("🏛️ Massey Strategic Capital Terminal")
st.info("Status: Active Legal Case against Anamika Mishra/A3S LLC. Motion to Dismiss DENIED Feb 4, 2026.")

tabs = st.tabs(["📊 DASHBOARD", "💳 CARDS", "📅 BILLS", "🚖 UBER PERFORMANCE"])

# --- UBER PERFORMANCE TAB (EDITABLE) ---
with tabs[3]:
    st.subheader("Edit Uber Earnings & Hours")
    st.write("Double-click any cell to type. Click the **(+)** at the bottom to add a new day.")
    
    # The 'key' here is what makes it editable without resetting
    edited_uber = st.data_editor(
        st.session_state.uber_df,
        num_rows="dynamic",
        use_container_width=True,
        key="uber_editor_v1" 
    )
    
    if st.button("Save Uber Updates"):
        st.session_state.uber_df = edited_uber
        st.success("Uber data saved to app memory!")

# --- CARDS TAB (EDITABLE) ---
with tabs[1]:
    st.subheader("Edit Credit Cards & Available Credit")
    edited_cards = st.data_editor(
        st.session_state.cards_df,
        num_rows="dynamic",
        use_container_width=True,
        key="cards_editor_v1"
    )
    if st.button("Save Card Updates"):
        st.session_state.cards_df = edited_cards
        st.success("Card data saved!")

# --- BILLS TAB (EDITABLE) ---
with tabs[2]:
    st.subheader("Edit Bill Master List")
    edited_bills = st.data_editor(
        st.session_state.bills_df,
        num_rows="dynamic",
        use_container_width=True,
        key="bills_editor_v1"
    )
    if st.button("Save Bill Updates"):
        st.session_state.bills_df = edited_bills
        st.success("Bill data saved!")

# --- DASHBOARD TAB (AUTO-CALCULATIONS) ---
with tabs[0]:
    # Pull current data from memory
    c = st.session_state.cards_df
    u = st.session_state.uber_df
    
    # Calculate Totals (Scrubbing text to numbers)
    # Adjust column indices [1] and [2] based on your specific Excel layout
    bal = pd.to_numeric(c.iloc[:, 1], errors='coerce').sum() if not c.empty else 0
    lim = pd.to_numeric(c.iloc[:, 2], errors='coerce').sum() if not c.empty else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("TOTAL LIABILITIES", f"${bal:,.2f}")
    col2.metric("AVAILABLE CREDIT", f"${(lim - bal):,.2f}")
    col3.metric("PORTFOLIO UTILIZATION", f"{(bal/lim)*100:.1f}%" if lim > 0 else "0%")

    st.divider()
    st.write("### Legal & Strategic Context")
    st.write("- **Case Status**: Active ")
    st.write("- **Motion to Dismiss**: Denied on February 4, 2026 ")
    st.write("- **Next Major Event**: Motion for Summary Judgment hearing (Feb 19, 2026 - Past) [cite: 2]")
