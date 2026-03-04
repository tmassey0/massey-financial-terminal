# --- UBER PERFORMANCE (WITH AUTO-CALCULATION) ---
with tabs[3]:
    st.subheader("🚖 Edit Uber Performance")
    
    # Month selector
    selected_month = st.selectbox("Select Month", uber_sheets, index=2, key="uber_month_selector")
    
    # Load selected month if changed
    if selected_month != st.session_state.uber_month:
        try:
            df = pd.read_excel("Terrance Uber Tracker.xlsx", sheet_name=selected_month, skiprows=3)
            # Filter to actual data rows
            df = df[df.iloc[:, 1].notna() & (df.iloc[:, 1] != '')]
            if len(df.columns) >= 7:
                df = df.iloc[:, :7]
                df.columns = ['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status']
                # Convert numeric columns
                for col in ['Hours', 'Daily Earnings', 'Daily Goal', 'Difference']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                # Calculate initial differences
                df['Difference'] = df['Daily Earnings'] - df['Daily Goal']
                df['Status'] = df['Difference'].apply(lambda x: "✅ Goal Met" if x >= 0 else "⚠️ Below Goal")
            st.session_state.uber_current = df
            st.session_state.uber_month = selected_month
        except Exception as e:
            st.error(f"Error loading {selected_month}: {e}")
    
    st.info(f"📝 Editing {st.session_state.uber_month} 2026. Changes calculate automatically!")
    st.caption("Hours format: 7.04 = 7 hours 4 minutes")
    
    # Week selector
    weeks = ["Week 1 (Days 1-7)", "Week 2 (Days 8-14)", "Week 3 (Days 15-21)", "Week 4 (Days 22-28)", "Week 5 (Days 29+)", "All Weeks"]
    selected_week = st.selectbox("Filter by Week", weeks, key="week_selector")
    
    # Filter based on selection
    uber_df = st.session_state.uber_current.copy()
    if selected_week != "All Weeks" and len(uber_df) > 0:
        if selected_week == "Week 1 (Days 1-7)":
            uber_df = uber_df.iloc[0:min(7, len(uber_df))]
        elif selected_week == "Week 2 (Days 8-14)":
            uber_df = uber_df.iloc[7:min(14, len(uber_df))]
        elif selected_week == "Week 3 (Days 15-21)":
            uber_df = uber_df.iloc[14:min(21, len(uber_df))]
        elif selected_week == "Week 4 (Days 22-28)":
            uber_df = uber_df.iloc[21:min(28, len(uber_df))]
        elif selected_week == "Week 5 (Days 29+)":
            uber_df = uber_df.iloc[28:]
    
    # Create a key that changes with the week to force refresh
    editor_key = f"uber_editor_{selected_week}_{st.session_state.uber_month}"
    
    # Create editable dataframe with on_change callback
    def on_uber_edit():
        # This gets the current state of the editor
        if st.session_state[editor_key] is not None:
            edited_data = st.session_state[editor_key]
            
            # Calculate difference and status for each row
            for i, row in edited_data.iterrows():
                earnings = row.get('Daily Earnings', 0)
                goal = row.get('Daily Goal', 175)
                edited_data.at[i, 'Difference'] = earnings - goal
                edited_data.at[i, 'Status'] = "✅ Goal Met" if earnings - goal >= 0 else "⚠️ Below Goal"
            
            # Update the main dataframe
            if selected_week != "All Weeks" and len(uber_df) > 0:
                start_idx = 0
                if selected_week == "Week 1 (Days 1-7)":
                    start_idx = 0
                elif selected_week == "Week 2 (Days 8-14)":
                    start_idx = 7
                elif selected_week == "Week 3 (Days 15-21)":
                    start_idx = 14
                elif selected_week == "Week 4 (Days 22-28)":
                    start_idx = 21
                elif selected_week == "Week 5 (Days 29+)":
                    start_idx = 28
                
                for i, row in edited_data.iterrows():
                    if start_idx + i < len(st.session_state.uber_current):
                        st.session_state.uber_current.iloc[start_idx + i] = row
            else:
                st.session_state.uber_current = edited_data
    
    # Use the editor with on_change
    edited_uber = st.data_editor(
        uber_df,
        num_rows="dynamic",
        use_container_width=True,
        key=editor_key,
        on_change=on_uber_edit,
        column_config={
            "Day": st.column_config.TextColumn("Day", disabled=True, width="small"),
            "Date": st.column_config.DatetimeColumn("Date", disabled=True, format="MM/DD/YYYY", width="small"),
            "Hours": st.column_config.NumberColumn(
                "Hours Worked",
                disabled=False,
                min_value=0.0,
                max_value=24.0,
                step=0.01,
                format="%.2f",
                help="Hours worked (e.g., 7.04 = 7 hours 4 minutes)"
            ),
            "Daily Earnings": st.column_config.NumberColumn(
                "Daily Earnings ($)",
                disabled=False,
                min_value=0.0,
                step=0.01,
                format="$%.2f",
                help="Enter daily earnings"
            ),
            "Daily Goal": st.column_config.NumberColumn(
                "Daily Goal ($)",
                disabled=False,
                min_value=0.0,
                step=0.01,
                format="$%.2f",
                help="Daily earnings goal"
            ),
            "Difference": st.column_config.NumberColumn(
                "Difference ($)",
                disabled=True,  # Auto-calculated
                format="$%.2f"
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                disabled=True  # Auto-calculated
            )
        },
        hide_index=True,
    )
    
    # Manual recalc button as backup
    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("🔄 Force Recalculate", key="force_recalc"):
            # Force recalculate all
            for i, row in st.session_state.uber_current.iterrows():
                earnings = row.get('Daily Earnings', 0)
                goal = row.get('Daily Goal', 175)
                st.session_state.uber_current.at[i, 'Difference'] = earnings - goal
                st.session_state.uber_current.at[i, 'Status'] = "✅ Goal Met" if earnings - goal >= 0 else "⚠️ Below Goal"
            st.success("✅ Recalculated all rows!")
            st.rerun()
    
    with col2:
        if st.button("💾 Save All Changes", key="save_uber"):
            st.success(f"💾 Changes saved to {st.session_state.uber_month}!")
            # No need to do anything else since data is already in session_state
    
    # Show week summary with auto-updating totals
    st.markdown("---")
    st.subheader("📊 Real-Time Summary")
    
    # Calculate totals from the CURRENT edited data
    if len(edited_uber) > 0:
        total_hours = edited_uber["Hours"].sum()
        total_earnings = edited_uber["Daily Earnings"].sum()
        total_goal = edited_uber["Daily Goal"].sum()
        total_diff = total_earnings - total_goal
        
        # Create metrics that update automatically
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Hours", f"{total_hours:.2f}")
        m2.metric("Total Earnings", f"${total_earnings:,.2f}")
        m3.metric("Total Goal", f"${total_goal:,.2f}")
        
        # Color code the difference metric
        if total_diff >= 0:
            m4.metric("Net vs Goal", f"+${total_diff:,.2f}", delta=f"+${total_diff:,.2f}")
        else:
            m4.metric("Net vs Goal", f"-${abs(total_diff):,.2f}", delta=f"-${abs(total_diff):,.2f}", delta_color="inverse")
        
        # Show daily breakdown
        with st.expander("📋 Daily Breakdown"):
            # Create a clean display dataframe
            display_df = edited_uber[['Day', 'Date', 'Hours', 'Daily Earnings', 'Daily Goal', 'Difference', 'Status']].copy()
            display_df['Daily Earnings'] = display_df['Daily Earnings'].apply(lambda x: f"${x:,.2f}")
            display_df['Daily Goal'] = display_df['Daily Goal'].apply(lambda x: f"${x:,.2f}")
            display_df['Difference'] = display_df['Difference'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Add new row button
    st.markdown("---")
    if st.button("➕ Add New Row", key="add_row"):
        import datetime
        # Determine next day
        if len(st.session_state.uber_current) > 0:
            last_date = st.session_state.uber_current['Date'].iloc[-1]
            if isinstance(last_date, pd.Timestamp):
                next_date = last_date + pd.Timedelta(days=1)
            else:
                next_date = datetime.datetime.now()
        else:
            next_date = datetime.datetime.now()
        
        # Determine day name
        day_name = next_date.strftime("%A") if isinstance(next_date, (pd.Timestamp, datetime.datetime)) else "New Day"
        
        new_row = pd.DataFrame({
            'Day': [day_name],
            'Date': [next_date],
            'Hours': [0.0],
            'Daily Earnings': [0.0],
            'Daily Goal': [175.0],
            'Difference': [-175.0],  # Will be recalculated
            'Status': ['⚠️ Below Goal']
        })
        st.session_state.uber_current = pd.concat([st.session_state.uber_current, new_row], ignore_index=True)
        st.rerun()
