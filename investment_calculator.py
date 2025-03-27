import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def calculate_sip_returns(monthly_investment, annual_return_rate, time_years):
    """
    Calculate returns for SIP investments
    
    Parameters:
    - monthly_investment: Amount invested each month
    - annual_return_rate: Expected annual return rate (in %)
    - time_years: Investment duration in years
    
    Returns:
    - DataFrame with monthly data on investment growth
    """
    # Convert annual return rate to monthly
    monthly_rate = (1 + annual_return_rate/100) ** (1/12) - 1
    
    # Total number of months
    total_months = time_years * 12
    
    # Initialize arrays
    total_investment = np.zeros(total_months)
    investment_value = np.zeros(total_months)
    
    # Calculate values for each month
    for month in range(total_months):
        if month == 0:
            total_investment[month] = monthly_investment
            investment_value[month] = monthly_investment
        else:
            # Add this month's investment
            total_investment[month] = total_investment[month-1] + monthly_investment
            
            # Calculate new value with returns
            investment_value[month] = (investment_value[month-1] * (1 + monthly_rate)) + monthly_investment
    
    # Create DataFrame
    result_df = pd.DataFrame({
        'Month': range(1, total_months + 1),
        'Total_Investment': total_investment,
        'Investment_Value': investment_value
    })
    
    return result_df

def calculate_lumpsum_returns(investment_amount, annual_return_rate, time_years):
    """
    Calculate returns for lumpsum investments
    
    Parameters:
    - investment_amount: Initial investment amount
    - annual_return_rate: Expected annual return rate (in %)
    - time_years: Investment duration in years
    
    Returns:
    - DataFrame with yearly data on investment growth
    """
    # Initialize arrays
    years = np.arange(0, time_years + 1)
    investment_value = np.zeros(len(years))
    
    # Calculate values for each year
    for i, year in enumerate(years):
        investment_value[i] = investment_amount * ((1 + annual_return_rate/100) ** year)
    
    # Create DataFrame
    result_df = pd.DataFrame({
        'Year': years,
        'Investment_Value': investment_value
    })
    
    return result_df

def calculate_goal_based_sip(target_amount, annual_return_rate, time_years):
    """
    Calculate SIP required to reach a specific financial goal
    
    Parameters:
    - target_amount: Target amount to reach
    - annual_return_rate: Expected annual return rate (in %)
    - time_years: Investment duration in years
    
    Returns:
    - monthly_sip: Required monthly SIP amount
    """
    # Convert annual return rate to monthly
    monthly_rate = (1 + annual_return_rate/100) ** (1/12) - 1
    
    # Total number of months
    total_months = time_years * 12
    
    # Calculate required monthly SIP using the formula:
    # M = P / ((1+r)^n - 1) / r * (1+r)
    # Where:
    # M = monthly SIP amount
    # P = target amount
    # r = monthly rate
    # n = number of months
    
    monthly_sip = target_amount / (((1 + monthly_rate) ** total_months - 1) / monthly_rate) / (1 + monthly_rate)
    
    return monthly_sip

def calculate_step_up_sip(initial_monthly_investment, annual_step_up_rate, annual_return_rate, time_years):
    """
    Calculate returns for SIP investments with annual step-up
    
    Parameters:
    - initial_monthly_investment: Initial amount invested each month
    - annual_step_up_rate: Annual percentage increase in SIP amount
    - annual_return_rate: Expected annual return rate (in %)
    - time_years: Investment duration in years
    
    Returns:
    - DataFrame with monthly data on investment growth
    """
    # Convert annual return rate to monthly
    monthly_rate = (1 + annual_return_rate/100) ** (1/12) - 1
    
    # Total number of months
    total_months = time_years * 12
    
    # Initialize arrays
    monthly_investment = np.zeros(total_months)
    total_investment = np.zeros(total_months)
    investment_value = np.zeros(total_months)
    
    # Calculate values for each month
    for month in range(total_months):
        year = month // 12
        
        # Calculate the SIP amount for this month with step-up
        if month % 12 == 0 and month > 0:  # Apply step-up at the beginning of each year (except first)
            current_monthly_sip = initial_monthly_investment * ((1 + annual_step_up_rate/100) ** year)
        elif month == 0:
            current_monthly_sip = initial_monthly_investment
        else:
            current_monthly_sip = monthly_investment[month-1]  # Same as previous month
        
        monthly_investment[month] = current_monthly_sip
        
        if month == 0:
            total_investment[month] = current_monthly_sip
            investment_value[month] = current_monthly_sip
        else:
            # Add this month's investment
            total_investment[month] = total_investment[month-1] + current_monthly_sip
            
            # Calculate new value with returns
            investment_value[month] = (investment_value[month-1] * (1 + monthly_rate)) + current_monthly_sip
    
    # Create DataFrame
    result_df = pd.DataFrame({
        'Month': range(1, total_months + 1),
        'Monthly_SIP': monthly_investment,
        'Total_Investment': total_investment,
        'Investment_Value': investment_value
    })
    
    return result_df

def calculate_retirement_corpus(monthly_expenses, life_expectancy, retirement_age, inflation_rate):
    """
    Calculate the retirement corpus needed
    
    Parameters:
    - monthly_expenses: Current monthly expenses
    - life_expectancy: Expected age of living
    - retirement_age: Age at which you plan to retire
    - inflation_rate: Expected inflation rate (in %)
    
    Returns:
    - retirement_corpus: Corpus needed at retirement
    """
    current_age = retirement_age  # Simplifying assumption, we calculate from retirement age
    retirement_duration = life_expectancy - retirement_age
    
    # Calculate monthly expenses at retirement age (adjusted for inflation)
    monthly_expenses_at_retirement = monthly_expenses * ((1 + inflation_rate/100) ** (retirement_age - current_age))
    
    # Annual expenses at retirement
    annual_expenses_at_retirement = monthly_expenses_at_retirement * 12
    
    # Assuming withdrawal rate of 4% annually (25x annual expenses rule)
    # This is based on the 4% rule which suggests that you can safely withdraw 4% of your retirement corpus
    # each year with minimal risk of running out of money during your lifetime.
    retirement_corpus = annual_expenses_at_retirement * 25
    
    return retirement_corpus

def show_investment_calculator():
    # Modern header with icon
    st.markdown("<h1 style='font-size: 2.1rem; font-weight: 600; margin-bottom: 1.5rem;'>📚 Investment Calculator</h1>", unsafe_allow_html=True)
    
    # Create tabs for different calculators
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "SIP Calculator", 
        "Lumpsum Calculator", 
        "Goal-based SIP", 
        "Step-up SIP", 
        "Investment Education"
    ])
    
    with tab1:
        # Card-like container for SIP calculator
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3>SIP (Systematic Investment Plan) Calculator</h3>", unsafe_allow_html=True)
        
        # Input form for SIP calculator
        with st.form(key="sip_calculator_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                monthly_investment = st.number_input(
                    "Monthly Investment Amount (₹)",
                    min_value=100,
                    value=1000,
                    step=100
                )
                
                annual_return_rate = st.slider(
                    "Expected Annual Return (%)",
                    min_value=1.0,
                    max_value=30.0,
                    value=12.0,
                    step=0.5
                )
            
            with col2:
                time_years = st.slider(
                    "Investment Duration (Years)",
                    min_value=1,
                    max_value=40,
                    value=10
                )
                
                inflation_rate = st.slider(
                    "Expected Inflation Rate (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=6.0,
                    step=0.5
                )
            
            calculate_button = st.form_submit_button("Calculate SIP Returns")
            
            if calculate_button:
                # Calculate returns
                sip_results = calculate_sip_returns(
                    monthly_investment, 
                    annual_return_rate, 
                    time_years
                )
                
                # Display summary results
                st.subheader("SIP Investment Summary")
                
                # Calculate key metrics
                total_invested = monthly_investment * time_years * 12
                final_value = sip_results['Investment_Value'].iloc[-1]
                wealth_gained = final_value - total_invested
                
                # Inflation-adjusted final value
                real_return_rate = (1 + annual_return_rate/100) / (1 + inflation_rate/100) - 1
                inflation_adj_final = monthly_investment * (((1 + real_return_rate) ** (time_years * 12) - 1) / real_return_rate) * (1 + real_return_rate)
                
                # Display metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Amount Invested", f"₹{total_invested:,.2f}")
                
                with col2:
                    st.metric("Expected Final Value", f"₹{final_value:,.2f}")
                
                with col3:
                    st.metric("Wealth Gained", f"₹{wealth_gained:,.2f}", 
                             delta=f"{(wealth_gained/total_invested)*100:.1f}%")
                
                # Additional metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Inflation-Adjusted Value", f"₹{inflation_adj_final:,.2f}")
                
                with col2:
                    st.metric("Real Returns", f"{real_return_rate*100:.2f}%")
                
                # Visualize the growth
                st.subheader("Investment Growth Over Time")
                
                # Plot investment growth
                fig = go.Figure()
                
                # Add total investment line
                fig.add_trace(
                    go.Scatter(
                        x=sip_results['Month'],
                        y=sip_results['Total_Investment'],
                        name="Amount Invested",
                        line=dict(color="blue")
                    )
                )
                
                # Add investment value line
                fig.add_trace(
                    go.Scatter(
                        x=sip_results['Month'],
                        y=sip_results['Investment_Value'],
                        name="Investment Value",
                        line=dict(color="green")
                    )
                )
                
                # Add inflation-adjusted value line
                inflation_adj_values = []
                for month in range(1, time_years * 12 + 1):
                    inflation_factor = (1 + inflation_rate/100) ** (month/12)
                    inflation_adj_value = sip_results['Investment_Value'].iloc[month-1] / inflation_factor
                    inflation_adj_values.append(inflation_adj_value)
                
                fig.add_trace(
                    go.Scatter(
                        x=sip_results['Month'],
                        y=inflation_adj_values,
                        name="Inflation-Adjusted Value",
                        line=dict(color="red", dash="dash")
                    )
                )
                
                # Update layout
                fig.update_layout(
                    title="SIP Investment Growth Visualization",
                    xaxis_title="Months",
                    yaxis_title="Value (₹)",
                    legend=dict(x=0, y=1.1, orientation="h"),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data in tabular format
                with st.expander("View detailed growth data"):
                    yearly_data = sip_results[sip_results['Month'] % 12 == 0].copy()
                    yearly_data['Year'] = yearly_data['Month'] // 12
                    yearly_data = yearly_data[['Year', 'Total_Investment', 'Investment_Value']]
                    yearly_data['Wealth_Gained'] = yearly_data['Investment_Value'] - yearly_data['Total_Investment']
                    yearly_data['Returns_Percentage'] = (yearly_data['Wealth_Gained'] / yearly_data['Total_Investment'] * 100)
                    
                    # Format for display
                    display_df = yearly_data.copy()
                    display_df['Total_Investment'] = display_df['Total_Investment'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Investment_Value'] = display_df['Investment_Value'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Wealth_Gained'] = display_df['Wealth_Gained'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Returns_Percentage'] = display_df['Returns_Percentage'].apply(lambda x: f"{x:.2f}%")
                    
                    st.dataframe(display_df, use_container_width=True)
    
    with tab2:
        st.subheader("Lumpsum Investment Calculator")
        
        # Input form for lumpsum calculator
        with st.form(key="lumpsum_calculator_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                investment_amount = st.number_input(
                    "Investment Amount (₹)",
                    min_value=1000,
                    value=100000,
                    step=1000
                )
                
                annual_return_rate = st.slider(
                    "Expected Annual Return (%)",
                    min_value=1.0,
                    max_value=30.0,
                    value=12.0,
                    step=0.5,
                    key="lumpsum_return_rate"
                )
            
            with col2:
                time_years = st.slider(
                    "Investment Duration (Years)",
                    min_value=1,
                    max_value=40,
                    value=10,
                    key="lumpsum_time_years"
                )
                
                inflation_rate = st.slider(
                    "Expected Inflation Rate (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=6.0,
                    step=0.5,
                    key="lumpsum_inflation_rate"
                )
            
            calculate_button = st.form_submit_button("Calculate Lumpsum Returns")
            
            if calculate_button:
                # Calculate returns
                lumpsum_results = calculate_lumpsum_returns(
                    investment_amount, 
                    annual_return_rate, 
                    time_years
                )
                
                # Display summary results
                st.subheader("Lumpsum Investment Summary")
                
                # Calculate key metrics
                initial_investment = investment_amount
                final_value = lumpsum_results['Investment_Value'].iloc[-1]
                wealth_gained = final_value - initial_investment
                
                # Inflation-adjusted final value
                real_return_rate = (1 + annual_return_rate/100) / (1 + inflation_rate/100) - 1
                inflation_adj_final = initial_investment * ((1 + real_return_rate) ** time_years)
                
                # Display metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Initial Investment", f"₹{initial_investment:,.2f}")
                
                with col2:
                    st.metric("Expected Final Value", f"₹{final_value:,.2f}")
                
                with col3:
                    st.metric("Wealth Gained", f"₹{wealth_gained:,.2f}", 
                             delta=f"{(wealth_gained/initial_investment)*100:.1f}%")
                
                # Additional metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Inflation-Adjusted Value", f"₹{inflation_adj_final:,.2f}")
                
                with col2:
                    st.metric("Real Annual Returns", f"{real_return_rate*100:.2f}%")
                
                # Visualize the growth
                st.subheader("Investment Growth Over Time")
                
                # Plot investment growth
                fig = go.Figure()
                
                # Add investment value line
                fig.add_trace(
                    go.Scatter(
                        x=lumpsum_results['Year'],
                        y=lumpsum_results['Investment_Value'],
                        name="Investment Value",
                        line=dict(color="green")
                    )
                )
                
                # Add initial investment line
                fig.add_trace(
                    go.Scatter(
                        x=lumpsum_results['Year'],
                        y=[initial_investment] * len(lumpsum_results),
                        name="Initial Investment",
                        line=dict(color="blue", dash="dash")
                    )
                )
                
                # Add inflation-adjusted value line
                inflation_adj_values = []
                for year in range(time_years + 1):
                    inflation_factor = (1 + inflation_rate/100) ** year
                    inflation_adj_value = lumpsum_results['Investment_Value'].iloc[year] / inflation_factor
                    inflation_adj_values.append(inflation_adj_value)
                
                fig.add_trace(
                    go.Scatter(
                        x=lumpsum_results['Year'],
                        y=inflation_adj_values,
                        name="Inflation-Adjusted Value",
                        line=dict(color="red", dash="dash")
                    )
                )
                
                # Update layout
                fig.update_layout(
                    title="Lumpsum Investment Growth Visualization",
                    xaxis_title="Years",
                    yaxis_title="Value (₹)",
                    legend=dict(x=0, y=1.1, orientation="h"),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data in tabular format
                with st.expander("View detailed growth data"):
                    display_df = lumpsum_results.copy()
                    display_df['Initial_Investment'] = initial_investment
                    display_df['Wealth_Gained'] = display_df['Investment_Value'] - display_df['Initial_Investment']
                    display_df['Returns_Percentage'] = (display_df['Wealth_Gained'] / display_df['Initial_Investment'] * 100)
                    
                    # Format for display
                    display_df['Initial_Investment'] = display_df['Initial_Investment'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Investment_Value'] = display_df['Investment_Value'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Wealth_Gained'] = display_df['Wealth_Gained'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Returns_Percentage'] = display_df['Returns_Percentage'].apply(lambda x: f"{x:.2f}%")
                    
                    st.dataframe(display_df, use_container_width=True)
    
    with tab3:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Goal-based SIP Calculator</h3>", unsafe_allow_html=True)
        st.markdown("Calculate how much you need to invest monthly to reach a specific financial goal")
        
        # Input form for goal-based SIP calculator
        with st.form(key="goal_sip_calculator_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                target_amount = st.number_input(
                    "Target Amount (₹)",
                    min_value=10000,
                    value=1000000,
                    step=10000
                )
                
                annual_return_rate = st.slider(
                    "Expected Annual Return (%)",
                    min_value=1.0,
                    max_value=30.0,
                    value=12.0,
                    step=0.5,
                    key="goal_return_rate"
                )
            
            with col2:
                time_years = st.slider(
                    "Time to Achieve Goal (Years)",
                    min_value=1,
                    max_value=40,
                    value=10,
                    key="goal_time_years"
                )
                
                inflation_rate = st.slider(
                    "Expected Inflation Rate (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=6.0,
                    step=0.5,
                    key="goal_inflation_rate"
                )
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(33,150,243,0.1), rgba(33,150,243,0.05)); 
                        border-radius: 10px; padding: 10px; margin: 10px 0;">
                <p style="margin: 0; font-size: 0.9rem;">
                    <strong>💡 Common Financial Goals:</strong> Home purchase (₹50L-₹2Cr), 
                    Child's education (₹25L-₹50L), Retirement (₹1Cr-₹3Cr), Wedding (₹10L-₹30L)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            calculate_button = st.form_submit_button("Calculate Required SIP")
            
            if calculate_button:
                # Calculate inflation-adjusted target amount
                inflation_adjusted_target = target_amount * ((1 + inflation_rate/100) ** time_years)
                
                # Calculate required SIP
                monthly_sip = calculate_goal_based_sip(
                    inflation_adjusted_target, 
                    annual_return_rate, 
                    time_years
                )
                
                # Display summary results
                st.subheader("Goal-based SIP Result")
                
                # Display metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Monthly SIP Required", f"₹{monthly_sip:,.2f}")
                
                with col2:
                    st.metric("Total Investment", f"₹{monthly_sip * 12 * time_years:,.2f}")
                
                with col3:
                    st.metric("Target Amount", f"₹{target_amount:,.2f}")
                
                # Additional metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Inflation-Adjusted Target", f"₹{inflation_adjusted_target:,.2f}")
                
                with col2:
                    wealth_gained = inflation_adjusted_target - (monthly_sip * 12 * time_years)
                    st.metric("Potential Wealth Gained", f"₹{wealth_gained:,.2f}")
                
                # Calculate and visualize growth
                sip_results = calculate_sip_returns(monthly_sip, annual_return_rate, time_years)
                
                # Plot investment growth
                fig = go.Figure()
                
                # Add total investment line
                fig.add_trace(
                    go.Scatter(
                        x=sip_results['Month'],
                        y=sip_results['Total_Investment'],
                        name="Amount Invested",
                        line=dict(color="blue")
                    )
                )
                
                # Add investment value line
                fig.add_trace(
                    go.Scatter(
                        x=sip_results['Month'],
                        y=sip_results['Investment_Value'],
                        name="Investment Value",
                        line=dict(color="green")
                    )
                )
                
                # Add target line
                fig.add_trace(
                    go.Scatter(
                        x=sip_results['Month'],
                        y=[inflation_adjusted_target] * len(sip_results),
                        name="Target Amount",
                        line=dict(color="red", dash="dash")
                    )
                )
                
                # Update layout
                fig.update_layout(
                    title="Goal Achievement Projection",
                    xaxis_title="Months",
                    yaxis_title="Value (₹)",
                    legend=dict(x=0, y=1.1, orientation="h"),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Goal planning tips
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                            border-radius: 10px; padding: 15px; margin-top: 1rem;">
                    <h4 style="margin-top: 0;">Tips for Goal-based Investing</h4>
                    <ul style="margin-bottom: 0;">
                        <li>Consider increasing your SIP amount annually to keep pace with inflation</li>
                        <li>Revisit your goal and investment strategy annually</li>
                        <li>For long-term goals, allocate more to equity investments</li>
                        <li>For short-term goals (under 3 years), focus on safer investments</li>
                        <li>Set up an automatic SIP to ensure disciplined investing</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab4:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Step-up SIP Calculator</h3>", unsafe_allow_html=True)
        st.markdown("Calculate returns with an annual increase in your SIP investment amount")
        
        # Input form for step-up SIP calculator
        with st.form(key="stepup_sip_calculator_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                initial_monthly_investment = st.number_input(
                    "Initial Monthly Investment (₹)",
                    min_value=100,
                    value=1000,
                    step=100
                )
                
                annual_step_up_rate = st.slider(
                    "Annual Step-up Rate (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=10.0,
                    step=1.0
                )
            
            with col2:
                annual_return_rate = st.slider(
                    "Expected Annual Return (%)",
                    min_value=1.0,
                    max_value=30.0,
                    value=12.0,
                    step=0.5,
                    key="stepup_return_rate"
                )
                
                time_years = st.slider(
                    "Investment Duration (Years)",
                    min_value=1,
                    max_value=40,
                    value=15,
                    key="stepup_time_years"
                )
            
            calculate_button = st.form_submit_button("Calculate Step-up SIP Returns")
            
            if calculate_button:
                # Calculate step-up SIP returns
                stepup_results = calculate_step_up_sip(
                    initial_monthly_investment,
                    annual_step_up_rate,
                    annual_return_rate,
                    time_years
                )
                
                # For comparison, calculate regular SIP returns with the same initial amount
                regular_results = calculate_sip_returns(
                    initial_monthly_investment,
                    annual_return_rate,
                    time_years
                )
                
                # Display summary results
                st.subheader("Step-up SIP Investment Summary")
                
                # Calculate key metrics
                total_invested = stepup_results['Total_Investment'].iloc[-1]
                final_value = stepup_results['Investment_Value'].iloc[-1]
                wealth_gained = final_value - total_invested
                
                # Regular SIP metrics for comparison
                regular_total_invested = regular_results['Total_Investment'].iloc[-1]
                regular_final_value = regular_results['Investment_Value'].iloc[-1]
                
                # Display metrics in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Amount Invested", f"₹{total_invested:,.2f}")
                
                with col2:
                    st.metric("Expected Final Value", f"₹{final_value:,.2f}")
                
                with col3:
                    st.metric("Wealth Gained", f"₹{wealth_gained:,.2f}", 
                             delta=f"{(wealth_gained/total_invested)*100:.1f}%")
                
                # Comparison with regular SIP
                st.subheader("Comparison with Regular SIP")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Step-up SIP Final Value", 
                        f"₹{final_value:,.2f}", 
                        delta=f"₹{final_value-regular_final_value:,.2f} more than regular SIP"
                    )
                
                with col2:
                    st.metric(
                        "Regular SIP Final Value", 
                        f"₹{regular_final_value:,.2f}"
                    )
                
                # Visualize the growth
                st.subheader("Investment Growth Over Time")
                
                # Plot investment growth comparison
                fig = go.Figure()
                
                # Add step-up SIP investment value line
                fig.add_trace(
                    go.Scatter(
                        x=stepup_results['Month'],
                        y=stepup_results['Investment_Value'],
                        name="Step-up SIP Value",
                        line=dict(color="green")
                    )
                )
                
                # Add regular SIP investment value line
                fig.add_trace(
                    go.Scatter(
                        x=regular_results['Month'],
                        y=regular_results['Investment_Value'],
                        name="Regular SIP Value",
                        line=dict(color="blue", dash="dot")
                    )
                )
                
                # Add step-up total investment line
                fig.add_trace(
                    go.Scatter(
                        x=stepup_results['Month'],
                        y=stepup_results['Total_Investment'],
                        name="Step-up Investment",
                        line=dict(color="orange")
                    )
                )
                
                # Add regular total investment line
                fig.add_trace(
                    go.Scatter(
                        x=regular_results['Month'],
                        y=regular_results['Total_Investment'],
                        name="Regular Investment",
                        line=dict(color="purple", dash="dot")
                    )
                )
                
                # Update layout
                fig.update_layout(
                    title="Step-up vs. Regular SIP Growth Comparison",
                    xaxis_title="Months",
                    yaxis_title="Value (₹)",
                    legend=dict(x=0, y=1.1, orientation="h"),
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data in tabular format with yearly comparison
                with st.expander("View yearly comparison data"):
                    # Get yearly data points
                    yearly_step = stepup_results[stepup_results['Month'] % 12 == 0].copy()
                    yearly_step['Year'] = yearly_step['Month'] // 12
                    
                    yearly_regular = regular_results[regular_results['Month'] % 12 == 0].copy()
                    
                    # Create comparison DataFrame
                    comparison_df = pd.DataFrame({
                        'Year': yearly_step['Year'],
                        'Monthly_SIP_Amount': yearly_step['Monthly_SIP'],
                        'Step_Up_Invested': yearly_step['Total_Investment'],
                        'Step_Up_Value': yearly_step['Investment_Value'],
                        'Regular_Invested': yearly_regular['Total_Investment'],
                        'Regular_Value': yearly_regular['Investment_Value']
                    })
                    
                    # Add difference columns
                    comparison_df['Value_Difference'] = comparison_df['Step_Up_Value'] - comparison_df['Regular_Value']
                    
                    # Format for display
                    display_df = comparison_df.copy()
                    display_df['Monthly_SIP_Amount'] = display_df['Monthly_SIP_Amount'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Step_Up_Invested'] = display_df['Step_Up_Invested'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Step_Up_Value'] = display_df['Step_Up_Value'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Regular_Invested'] = display_df['Regular_Invested'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Regular_Value'] = display_df['Regular_Value'].apply(lambda x: f"₹{x:,.2f}")
                    display_df['Value_Difference'] = display_df['Value_Difference'].apply(lambda x: f"₹{x:,.2f}")
                    
                    st.dataframe(display_df, use_container_width=True)
                
                # Monthly SIP Progression chart
                st.subheader("Monthly SIP Amount Progression")
                
                fig = px.line(
                    stepup_results, 
                    x='Month', 
                    y='Monthly_SIP',
                    title=f"Monthly SIP Amount with {annual_step_up_rate}% Annual Step-up",
                    labels={'Month': 'Month', 'Monthly_SIP': 'SIP Amount (₹)'}
                )
                
                fig.update_layout(height=400)
                
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab5:
        # Investment basics accordion
        with st.expander("Investment Basics for Students"):
            st.write("""
            ### Why should students invest?
            
            Starting to invest early gives you a huge advantage due to the power of compounding. 
            Even small investments made during college years can grow significantly over time.
            
            ### Key investment terms:
            
            - **SIP (Systematic Investment Plan)**: A method to invest a fixed amount regularly in mutual funds
            - **Mutual Funds**: Professionally managed investment funds that pool money from many investors
            - **Equity**: Ownership in a company through stocks
            - **Debt**: Fixed income investments like bonds and fixed deposits
            - **Returns**: The profit or loss from your investments
            - **Risk**: The possibility of losing money in an investment
            - **Diversification**: Spreading investments across different assets to reduce risk
            """)
        
        # SIP vs. Lumpsum accordion
        with st.expander("SIP vs. Lumpsum Investment"):
            st.write("""
            ### Systematic Investment Plan (SIP)
            
            **Advantages for students:**
            - Start with small amounts (as low as ₹500 per month)
            - Builds discipline in saving regularly
            - Reduces the impact of market volatility through rupee cost averaging
            - Easier to manage with limited student income
            
            ### Lumpsum Investment
            
            **When it makes sense:**
            - When you receive a large amount at once (scholarship, gift, internship stipend)
            - When markets are significantly down (though timing the market is difficult)
            - For short-term financial goals (1-3 years)
            
            ### Which should you choose?
            
            As a student, SIP is generally more suitable as it:
            - Matches your income pattern (monthly allowances)
            - Allows starting with smaller amounts
            - Builds a healthy financial habit
            """)
        
        # Investment options for students
        with st.expander("Best Investment Options for Students"):
            st.write("""
            ### Investment options suitable for students:
            
            1. **Mutual Funds via SIP**
               - Equity funds for long-term goals (5+ years)
               - Debt funds for medium-term goals (2-4 years)
               - Hybrid funds for balanced approach
            
            2. **Public Provident Fund (PPF)**
               - Long-term tax-free investment
               - Current interest rate: ~7.1%
               - Lock-in period: 15 years
            
            3. **Fixed Deposits**
               - Safe and guaranteed returns
               - Good for short-term goals
               - Current interest rates: 5-7%
            
            4. **Index Funds**
               - Low-cost investment in market indices like Nifty 50
               - Good for beginners
               - Lower risk than active equity funds
            
            5. **Sukanya Samriddhi Yojana** (for girl students)
               - Government-backed scheme with tax benefits
               - Current interest rate: ~7.6%
            """)
        
        # Common mistakes accordion
        with st.expander("Common Investment Mistakes Students Make"):
            st.write("""
            ### Avoid these common mistakes:
            
            1. **Not starting early enough**
               - Even ₹500/month from age 20 can grow significantly by retirement
            
            2. **Investing without financial goals**
               - Define what you're saving for (higher education, travel, first job expenses)
            
            3. **Not building an emergency fund first**
               - Keep 3-6 months of expenses in a liquid account before investing
            
            4. **Trying to time the market**
               - Regular investments work better than waiting for the "perfect time"
            
            5. **Withdrawing investments for small expenses**
               - Let your investments grow; use them only for planned goals
            
            6. **Not understanding tax implications**
               - Learn about STCG, LTCG, and tax-saving investments
            
            7. **Investing in complex products without understanding**
               - Start with simple investment options until you learn more
            """)
        
        # Interactive comparison tool
        st.subheader("Compare Investment Growth")
        
        col1, col2 = st.columns(2)
        
        with col1:
            compare_amount = st.number_input(
                "Monthly SIP Amount (₹)",
                min_value=100,
                value=1000,
                step=100,
                key="compare_sip_amount"
            )
        
        with col2:
            compare_years = st.slider(
                "Investment Duration (Years)",
                min_value=5,
                max_value=40,
                value=20,
                key="compare_years"
            )
        
        # Calculate and compare different return rates
        return_rates = [8, 12, 15]
        results = []
        
        for rate in return_rates:
            sip_results = calculate_sip_returns(compare_amount, rate, compare_years)
            final_value = sip_results['Investment_Value'].iloc[-1]
            total_invested = compare_amount * compare_years * 12
            results.append({
                'Rate': rate,
                'Final_Value': final_value,
                'Total_Invested': total_invested,
                'Wealth_Gained': final_value - total_invested
            })
        
        # Display comparison
        st.write(f"### Comparing a monthly SIP of ₹{compare_amount} for {compare_years} years")
        
        # Create comparison chart
        comparison_df = pd.DataFrame(results)
        
        fig = go.Figure()
        
        # Add bars for total invested
        fig.add_trace(
            go.Bar(
                x=[f"{r}% Return" for r in comparison_df['Rate']],
                y=comparison_df['Total_Invested'],
                name="Amount Invested",
                marker_color="blue"
            )
        )
        
        # Add bars for wealth gained
        fig.add_trace(
            go.Bar(
                x=[f"{r}% Return" for r in comparison_df['Rate']],
                y=comparison_df['Wealth_Gained'],
                name="Wealth Gained",
                marker_color="green"
            )
        )
        
        # Update layout
        fig.update_layout(
            title="Investment Growth Comparison",
            xaxis_title="Expected Return Rate",
            yaxis_title="Value (₹)",
            barmode="stack",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison table
        for result in results:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(f"{result['Rate']}% Returns", f"₹{result['Final_Value']:,.2f}")
            
            with col2:
                st.metric("Amount Invested", f"₹{result['Total_Invested']:,.2f}")
            
            with col3:
                st.metric("Wealth Gained", f"₹{result['Wealth_Gained']:,.2f}", 
                         delta=f"{(result['Wealth_Gained']/result['Total_Invested'])*100:.1f}%")
