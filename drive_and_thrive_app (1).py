# --- TAB 4: REVENUE ---
with tabs[3]:
    st.header("💰 Revenue Tracker")
    
    # Month selector
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    selected_month = st.selectbox("Select Month", months, index=2)
    
    st.info(f"Editing {selected_month} 2026 - Changes calculate automatically!")
    
    # Ensure revenue_df exists and is properly formatted with all columns
    if not safe_df_check(st.session_state.get('revenue_df')):
        sample_data = {
            'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'Date': ['2026-03-02', '2026-03-03', '2026-03-04', '2026-03-05', '2026-03-06', '2026-03-07', '2026-03-08'],
            'Hours': [8.53, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'Earnings': [224.70, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'Goal': [150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0]
        }
        df = pd.DataFrame(sample_data)
        # Add calculated columns
        df['Difference'] = df['Earnings'] - df['Goal']
        df['Status'] = df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
        st.session_state.revenue_df = df
    
    if 'revenue_history' not in st.session_state:
        st.session_state.revenue_history = []
    
    # Make sure all required columns exist
    required_cols = ['Day', 'Date', 'Hours', 'Earnings', 'Goal', 'Difference', 'Status']
    for col in required_cols:
        if col not in st.session_state.revenue_df.columns:
            if col == 'Difference':
                st.session_state.revenue_df[col] = st.session_state.revenue_df['Earnings'] - st.session_state.revenue_df['Goal']
            elif col == 'Status':
                st.session_state.revenue_df[col] = st.session_state.revenue_df['Difference'].apply(
                    lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal'
                )
            else:
                st.session_state.revenue_df[col] = 0.0 if col in ['Hours', 'Earnings', 'Goal'] else ''
    
    # Make a clean copy for editing
    working_df = st.session_state.revenue_df.copy()
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        # Undo button
        if st.button("↩️ Undo", key="undo_revenue"):
            if st.session_state.revenue_history:
                st.session_state.revenue_df = st.session_state.revenue_history.pop()
                st.success("Undo successful!")
                st.rerun()
            else:
                st.warning("No more undos available")
    
    with col2:
        # Add week button
        if st.button("📅 Add Week", key="add_week"):
            # Save current state for undo
            st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            current_date = datetime.datetime.now()
            
            week_rows = []
            for i, day in enumerate(days):
                week_date = current_date + datetime.timedelta(days=i)
                earnings = 0.0
                goal = 175.0
                difference = earnings - goal
                status = '⚠️ Below Goal' if difference < 0 else '✅ Goal Met'
                
                week_rows.append({
                    'Day': day,
                    'Date': week_date.strftime("%Y-%m-%d"),
                    'Hours': 0.0,
                    'Earnings': earnings,
                    'Goal': goal,
                    'Difference': difference,
                    'Status': status
                })
            
            week_df = pd.DataFrame(week_rows)
            st.session_state.revenue_df = pd.concat([st.session_state.revenue_df, week_df], ignore_index=True)
            st.rerun()
    
    # Define the update function with auto-calculation
    def update_revenue_data():
        try:
            if 'revenue_editor' in st.session_state and st.session_state.revenue_editor is not None:
                edited_df = st.session_state.revenue_editor
                
                # Auto-calculate Difference and Status
                if 'Earnings' in edited_df.columns and 'Goal' in edited_df.columns:
                    edited_df['Difference'] = edited_df['Earnings'] - edited_df['Goal']
                    edited_df['Status'] = edited_df['Difference'].apply(
                        lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal'
                    )
                
                # Save current state for undo
                st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
                # Keep only last 10 undo states
                if len(st.session_state.revenue_history) > 10:
                    st.session_state.revenue_history.pop(0)
                
                # Update session state
                st.session_state.revenue_df = edited_df
        except Exception as e:
            st.error(f"Error saving changes: {e}")
    
    # Display the data editor with all columns
    if safe_df_check(working_df):
        edited_revenue = st.data_editor(
            working_df,
            num_rows="dynamic",
            use_container_width=True,
            key="revenue_editor",
            on_change=update_revenue_data,
            column_config={
                "Day": st.column_config.TextColumn(
                    "Day",
                    disabled=False,
                    width="small"
                ),
                "Date": st.column_config.TextColumn(
                    "Date",
                    disabled=False,
                    width="small"
                ),
                "Hours": st.column_config.NumberColumn(
                    "Hours",
                    min_value=0.0,
                    max_value=24.0,
                    step=0.01,
                    format="%.2f",
                    disabled=False
                ),
                "Earnings": st.column_config.NumberColumn(
                    "Earnings ($)",
                    min_value=0.0,
                    step=0.01,
                    format="$%.2f",
                    disabled=False
                ),
                "Goal": st.column_config.NumberColumn(
                    "Goal ($)",
                    min_value=0.0,
                    step=0.01,
                    format="$%.2f",
                    disabled=False
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
            hide_index=True,
        )
        
        # Summary section
        st.markdown("---")
        st.subheader("📊 Summary")
        
        # Calculate totals
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
        
        # Performance metrics
        days_above = len(edited_revenue[edited_revenue['Earnings'] >= edited_revenue['Goal']])
        days_below = len(edited_revenue[edited_revenue['Earnings'] < edited_revenue['Goal']])
        success_rate = (days_above / len(edited_revenue) * 100) if len(edited_revenue) > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Days Above Goal", f"{days_above}")
        col2.metric("Days Below Goal", f"{days_below}")
        col3.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Weekly breakdown
        if len(edited_revenue) >= 7:
            with st.expander("📋 Weekly Breakdown"):
                num_weeks = (len(edited_revenue) + 6) // 7
                for week_num in range(num_weeks):
                    start_idx = week_num * 7
                    end_idx = min((week_num + 1) * 7, len(edited_revenue))
                    week_data = edited_revenue.iloc[start_idx:end_idx]
                    
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
    else:
        st.error("No revenue data available. Please create a template.")
        if st.button("Create Revenue Template"):
            sample_data = {
                'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                'Date': ['2026-03-02', '2026-03-03', '2026-03-04', '2026-03-05', '2026-03-06', '2026-03-07', '2026-03-08'],
                'Hours': [8.53, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                'Earnings': [224.70, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                'Goal': [150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0]
            }
            df = pd.DataFrame(sample_data)
            df['Difference'] = df['Earnings'] - df['Goal']
            df['Status'] = df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
            st.session_state.revenue_df = df
            st.rerun()
