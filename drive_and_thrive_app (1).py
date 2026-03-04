# --- REVENUE TAB ---
with tabs[3]:
    st.header("💰 Revenue Tracker")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("↩️ Undo"):
            if st.session_state.revenue_history:
                st.session_state.revenue_df = st.session_state.revenue_history.pop()
                st.rerun()
    
    with col2:
        if st.button("🔄 Update"):
            # Force update of all calculations
            df = st.session_state.revenue_df.copy()
            df['Difference'] = df['Earnings'] - df['Goal']
            df['Status'] = df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
            st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
            st.session_state.revenue_df = df
            st.rerun()
    
    def update_revenue():
        if 'revenue_editor' in st.session_state:
            df = st.session_state.revenue_editor
            df['Difference'] = df['Earnings'] - df['Goal']
            # Format Difference with + sign for positive values
            df['Status'] = df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
            st.session_state.revenue_history.append(st.session_state.revenue_df.copy())
            # Keep only last 10 undo states
            if len(st.session_state.revenue_history) > 10:
                st.session_state.revenue_history.pop(0)
            st.session_state.revenue_df = df
    
    # Display the data editor
    edited_revenue = st.data_editor(
        st.session_state.revenue_df,
        num_rows="dynamic",
        use_container_width=True,
        key="revenue_editor",
        on_change=update_revenue,
        column_config={
            "Day": st.column_config.TextColumn("Day", width="small"),
            "Date": st.column_config.TextColumn("Date", width="small"),
            "Hours": st.column_config.NumberColumn(
                "Hours", 
                min_value=0.0,
                max_value=24.0,
                step=0.01,
                format="%.2f"
            ),
            "Earnings": st.column_config.NumberColumn(
                "Earnings ($)", 
                min_value=0.0,
                step=0.01,
                format="$%.2f"
            ),
            "Goal": st.column_config.NumberColumn(
                "Goal ($)", 
                min_value=0.0,
                step=0.01,
                format="$%.2f"
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
        hide_index=True
    )
    
    # Summary section with enhanced metrics
    st.markdown("---")
    st.subheader("📊 Summary")
    
    # Calculate totals
    total_hours = edited_revenue['Hours'].sum()
    total_earnings = edited_revenue['Earnings'].sum()
    total_goal = edited_revenue['Goal'].sum()
    total_diff = total_earnings - total_goal
    
    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Hours", f"{total_hours:.2f}")
    col2.metric("Total Earnings", f"${total_earnings:,.2f}")
    col3.metric("Total Goal", f"${total_goal:,.2f}")
    
    # Show Difference with + or - sign
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
    
    # Add Week button at bottom
    if st.button("📅 Add Week", key="add_week_bottom"):
        # Save current state for undo
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
        week_df['Difference'] = week_df['Earnings'] - week_df['Goal']
        week_df['Status'] = week_df['Difference'].apply(lambda x: '✅ Goal Met' if x >= 0 else '⚠️ Below Goal')
        
        st.session_state.revenue_df = pd.concat([st.session_state.revenue_df, week_df], ignore_index=True)
        st.rerun()
