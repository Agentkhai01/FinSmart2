import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def plot_expense_by_category(expenses_df=None):
    """
    Plot a pie chart showing expenses by category
    
    Parameters:
    - expenses_df: DataFrame containing expense data (optional)
                   If not provided, uses the data from session state
    """
    # If no DataFrame is provided, use the one from session state
    if expenses_df is None:
        if st.session_state.expenses.empty:
            st.info("No expense data available for visualization.")
            return
        expenses_df = st.session_state.expenses.copy()
    
    if expenses_df.empty:
        st.info("No expenses match your current filters.")
        return
    
    # Group expenses by category
    category_totals = expenses_df.groupby('category')['amount'].sum().reset_index()
    
    # Calculate percentages for annotations
    total_expense = category_totals['amount'].sum()
    category_totals['percentage'] = (category_totals['amount'] / total_expense * 100).round(1)
    
    # Create a more visually appealing pie chart with custom styling
    fig = px.pie(
        category_totals,
        values='amount',
        names='category',
        title='<b>Expense Distribution</b>',
        hole=0.5,  # Larger hole for a more modern donut chart
        color_discrete_sequence=px.colors.qualitative.Bold,  # More vibrant color scheme
        custom_data=['percentage']  # Add percentage for hover
    )
    
    # Enhanced layout with drop shadow and better typography
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.5, xanchor="center"),
        height=450,
        title_font=dict(size=22, family="Arial", color="#2E4053"),
        font=dict(family="Arial", size=14),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=80, b=80, l=20, r=20)
    )
    
    # Add rupee symbol, percentage and improved hover text
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>₹%{value:.2f}<br>%{customdata[0]}% of total',
        textfont_size=14,
        marker=dict(line=dict(color='#FFFFFF', width=2)),  # Add white borders between segments
        pull=[0.03 if x == category_totals['amount'].max() else 0 for x in category_totals['amount']]  # Pull out largest segment
    )
    
    # Add a total amount annotation in the center
    fig.add_annotation(
        text=f"<b>₹{total_expense:.2f}</b><br>Total",
        x=0.5, y=0.5,
        font=dict(size=16, color="#1E88E5", family="Arial"),
        showarrow=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create an enhanced horizontal bar chart with gradient and annotations
    sorted_categories = category_totals.sort_values('amount', ascending=True)  # Ascending for better visual layout
    
    # Create customized bar chart with better visual appeal
    fig2 = go.Figure()
    
    # Add bars with gradient fill
    fig2.add_trace(go.Bar(
        y=sorted_categories['category'],
        x=sorted_categories['amount'],
        orientation='h',
        marker=dict(
            color=sorted_categories['amount'],
            colorscale='Viridis',  # Gradient colorscale
            line=dict(width=1, color='#FFFFFF')
        ),
        text=[f'₹{x:.0f} ({y}%)' for x, y in zip(sorted_categories['amount'], sorted_categories['percentage'])],
        textposition='auto',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{y}</b><br>Amount: ₹%{x:.2f}<br>Percentage: %{text}<extra></extra>'
    ))
    
    # Add visual improvements
    fig2.update_layout(
        title={
            'text': '<b>Category-wise Expenditure</b>',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'font': dict(size=22, family="Arial", color="#2E4053")
        },
        xaxis=dict(
            title='Amount (₹)',
            titlefont=dict(size=14),
            tickprefix="₹",
            showgrid=True,
            gridcolor='rgba(230, 230, 230, 0.5)'
        ),
        yaxis=dict(
            title='Category',
            titlefont=dict(size=14),
            categoryorder='total ascending'  # Order by value
        ),
        height=max(400, len(sorted_categories) * 50),  # Dynamic height based on categories
        margin=dict(l=20, r=20, t=80, b=50),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Add a note about the visualization
    st.markdown("<div style='text-align: right; font-size: 0.8rem; color: #666;'>Hover over bars for details</div>", unsafe_allow_html=True)
    
    # Display the chart
    st.plotly_chart(fig2, use_container_width=True)
    
    # Add breakdown cards for top categories
    st.markdown("<h4 style='margin-top: 1rem;'>Top Spending Categories</h4>", unsafe_allow_html=True)
    
    # Display top categories as cards
    top_categories = category_totals.sort_values('amount', ascending=False).head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top_categories.iterrows()):
        with cols[i]:
            color = ["#4CAF50", "#2196F3", "#FF9800"][i]  # Green, Blue, Orange
            percentage = row['percentage']
            st.markdown(f"""
            <div style="border-radius: 10px; padding: 15px; background: linear-gradient(135deg, {color}33, {color}11); border-left: 4px solid {color};">
                <h5 style="margin: 0; color: {color};">{row['category']}</h5>
                <div style="font-size: 1.5rem; font-weight: 600; margin: 8px 0;">₹{row['amount']:.2f}</div>
                <div style="font-size: 0.9rem; color: #666;">{percentage}% of total expenses</div>
            </div>
            """, unsafe_allow_html=True)

def plot_expense_over_time(expenses_df=None, period='daily'):
    """
    Plot expenses over time as a line chart
    
    Parameters:
    - expenses_df: DataFrame containing expense data (optional)
    - period: 'daily', 'weekly', or 'monthly'
    """
    # If no DataFrame is provided, use the one from session state
    if expenses_df is None:
        if st.session_state.expenses.empty:
            st.info("No expense data available for visualization.")
            return
        expenses_df = st.session_state.expenses.copy()
    
    if expenses_df.empty:
        st.info("No expenses match your current filters.")
        return
    
    # Convert date to datetime if it's not already
    expenses_df['date'] = pd.to_datetime(expenses_df['date'])
    
    # Group by the selected period
    if period == 'daily':
        expenses_df['period'] = expenses_df['date'].dt.date
        title = 'Daily Expenses Over Time'
        x_title = 'Date'
    elif period == 'weekly':
        expenses_df['period'] = expenses_df['date'].dt.isocalendar().week
        expenses_df['year'] = expenses_df['date'].dt.isocalendar().year
        expenses_df['period'] = expenses_df['year'].astype(str) + '-W' + expenses_df['period'].astype(str)
        title = 'Weekly Expenses Over Time'
        x_title = 'Week'
    elif period == 'monthly':
        expenses_df['period'] = expenses_df['date'].dt.strftime('%Y-%m')
        title = 'Monthly Expenses Over Time'
        x_title = 'Month'
    
    # Group by period and calculate total
    period_totals = expenses_df.groupby('period')['amount'].sum().reset_index()
    
    # Create line chart
    fig = px.line(
        period_totals,
        x='period',
        y='amount',
        title=title,
        labels={'amount': 'Total Amount (₹)', 'period': x_title},
        markers=True
    )
    
    # Add dots for each data point
    fig.update_traces(mode='lines+markers')
    
    # Format y-axis to show rupee symbol
    fig.update_layout(
        yaxis=dict(tickprefix="₹"),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_budget_vs_actual():
    """Plot a comparison of budgeted amounts vs actual spending by category"""
    # Return early if no data is available
    if st.session_state.expenses.empty or not st.session_state.budgets:
        st.info("Both expense data and budget settings are needed for this visualization.")
        return
    
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_month_name = datetime.now().strftime('%B')
    
    # Filter expenses for the current month
    monthly_expenses = st.session_state.expenses[
        (pd.to_datetime(st.session_state.expenses['date']).dt.month == current_month) &
        (pd.to_datetime(st.session_state.expenses['date']).dt.year == current_year)
    ]
    
    # Get category totals
    category_expenses = monthly_expenses.groupby('category')['amount'].sum().to_dict()
    
    # Prepare data for the chart
    categories = []
    budget_amounts = []
    actual_amounts = []
    percentages = []
    status = []
    
    for category, budget in st.session_state.budgets.items():
        if budget > 0:  # Only include categories with a budget
            actual = category_expenses.get(category, 0)
            percentage = (actual / budget) * 100 if budget > 0 else 0
            
            # Determine status based on percentage of budget used
            if percentage < 70:
                cat_status = "Good"
            elif percentage < 90:
                cat_status = "Warning"
            else:
                cat_status = "Alert"
                
            categories.append(category)
            budget_amounts.append(budget)
            actual_amounts.append(actual)
            percentages.append(percentage)
            status.append(cat_status)
    
    # Create DataFrame for plotting
    comparison_df = pd.DataFrame({
        'Category': categories,
        'Budget': budget_amounts,
        'Actual': actual_amounts,
        'Percentage': percentages,
        'Status': status
    })
    
    # Sort by budget utilization percentage (descending)
    comparison_df = comparison_df.sort_values('Percentage', ascending=False)
    
    # Create a more visually informative comparison chart
    fig = go.Figure()
    
    # Color mapping for status
    color_map = {
        "Good": "#4CAF50",      # Green
        "Warning": "#FF9800",   # Orange
        "Alert": "#F44336"      # Red
    }
    
    # Add budget bars (semi-transparent)
    fig.add_trace(go.Bar(
        x=comparison_df['Category'],
        y=comparison_df['Budget'],
        name='Budget Allocation',
        marker=dict(
            color='rgba(0, 105, 222, 0.3)',
            line=dict(color='rgba(0, 105, 222, 0.7)', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Budget: ₹%{y:.2f}<extra></extra>'
    ))
    
    # Add actual expense bars with color coding by status
    fig.add_trace(go.Bar(
        x=comparison_df['Category'],
        y=comparison_df['Actual'],
        name='Actual Spending',
        marker=dict(
            color=[color_map[s] for s in comparison_df['Status']],
            opacity=0.8,
            line=dict(color='white', width=1)
        ),
        text=[f'{p:.1f}%' for p in comparison_df['Percentage']],
        textposition='auto',
        insidetextfont=dict(color='white'),
        hovertemplate='<b>%{x}</b><br>Spent: ₹%{y:.2f}<br>Budget utilization: %{text}<extra></extra>'
    ))
    
    # Enhanced layout with better styling and typography
    fig.update_layout(
        title={
            'text': f"<b>Budget vs. Actual Spending</b><br><span style='font-size:16px; color:#666;'>{current_month_name} {current_year}</span>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20, family="Arial", color="#2E4053")
        },
        xaxis=dict(
            title="Category",
            titlefont=dict(size=14, family="Arial"),
            tickangle=-30
        ),
        yaxis=dict(
            title="Amount (₹)",
            titlefont=dict(size=14, family="Arial"),
            tickprefix="₹",
            gridcolor='rgba(230, 230, 230, 0.5)'
        ),
        barmode='overlay',  # Overlay mode for better visualization of budget vs actual
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=100, b=80, l=60, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        )
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Add infographic indicators for budget performance
    st.markdown("<h4 style='margin-top: 1rem;'>Budget Performance</h4>", unsafe_allow_html=True)
    
    # Calculate overall metrics
    total_budget = sum(budget_amounts)
    total_spent = sum(actual_amounts)
    overall_percentage = (total_spent / total_budget) * 100 if total_budget > 0 else 0
    remaining_budget = total_budget - total_spent
    
    # Create a progress bar for total budget
    progress_color = "#4CAF50" if overall_percentage < 70 else "#FF9800" if overall_percentage < 90 else "#F44336"
    
    # Using Bootstrap-style progress bar with gradient
    st.markdown(f"""
    <div style="margin: 1.5rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <div style="font-weight: 500;">Overall Budget: ₹{total_budget:.2f}</div>
            <div style="font-weight: 500; color: {progress_color};">{overall_percentage:.1f}% Used</div>
        </div>
        <div style="height: 12px; background-color: #e9ecef; border-radius: 10px; overflow: hidden;">
            <div style="width: {min(overall_percentage, 100)}%; height: 100%; background: linear-gradient(90deg, {progress_color}88, {progress_color}); border-radius: 10px;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
            <div style="font-size: 0.9rem; color: #666;">Spent: ₹{total_spent:.2f}</div>
            <div style="font-size: 0.9rem; color: #4CAF50;">Remaining: ₹{remaining_budget:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add category-specific insights
    cols = st.columns(3)
    
    # Over budget categories
    with cols[0]:
        over_budget = comparison_df[comparison_df['Percentage'] > 100]
        over_count = len(over_budget)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(244,67,54,0.1), rgba(244,67,54,0.05)); 
                    border-radius: 10px; padding: 15px; height: 100%;
                    border: 1px solid rgba(244,67,54,0.2);">
            <h5 style="color: #F44336; margin-top: 0;">Over Budget</h5>
            <div style="font-size: 2rem; font-weight: 600;">{over_count}</div>
            <div style="font-size: 0.9rem; color: #666;">categories exceeded budget</div>
            {f'<div style="margin-top: 0.5rem; font-size: 0.85rem;">Top overspent: <b>{over_budget.iloc[0]["Category"]}</b> ({over_budget.iloc[0]["Percentage"]:.1f}%)</div>' if over_count > 0 else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # Warning categories (close to budget)
    with cols[1]:
        warning = comparison_df[(comparison_df['Percentage'] >= 80) & (comparison_df['Percentage'] <= 100)]
        warning_count = len(warning)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255,152,0,0.1), rgba(255,152,0,0.05)); 
                    border-radius: 10px; padding: 15px; height: 100%;
                    border: 1px solid rgba(255,152,0,0.2);">
            <h5 style="color: #FF9800; margin-top: 0;">Approaching Limit</h5>
            <div style="font-size: 2rem; font-weight: 600;">{warning_count}</div>
            <div style="font-size: 0.9rem; color: #666;">categories > 80% of budget</div>
            {f'<div style="margin-top: 0.5rem; font-size: 0.85rem;">Closest to limit: <b>{warning.iloc[0]["Category"]}</b> ({warning.iloc[0]["Percentage"]:.1f}%)</div>' if warning_count > 0 else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # Healthy categories (well under budget)
    with cols[2]:
        healthy = comparison_df[comparison_df['Percentage'] < 80]
        healthy_count = len(healthy)
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(76,175,80,0.1), rgba(76,175,80,0.05)); 
                    border-radius: 10px; padding: 15px; height: 100%;
                    border: 1px solid rgba(76,175,80,0.2);">
            <h5 style="color: #4CAF50; margin-top: 0;">Healthy Budget</h5>
            <div style="font-size: 2rem; font-weight: 600;">{healthy_count}</div>
            <div style="font-size: 0.9rem; color: #666;">categories within budget</div>
            {f'<div style="margin-top: 0.5rem; font-size: 0.85rem;">Most efficient: <b>{healthy.iloc[-1]["Category"] if not healthy.empty else ""}</b> ({healthy.iloc[-1]["Percentage"]:.1f}%)</div>' if healthy_count > 0 else ''}
        </div>
        """, unsafe_allow_html=True)

def plot_budget_allocation(budgets):
    """Plot a pie chart showing budget allocation across categories"""
    # Convert budget dictionary to DataFrame
    budget_df = pd.DataFrame({
        'Category': list(budgets.keys()),
        'Amount': list(budgets.values())
    })
    
    # Create pie chart
    fig = px.pie(
        budget_df,
        values='Amount',
        names='Category',
        title='Budget Allocation by Category',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Update layout
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        height=400
    )
    
    # Add rupee symbol and formatting to hover text
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>₹%{value:.2f}<br>%{percent}'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_spending_plan(days, amounts):
    """Plot a bar chart showing the daily spending plan"""
    # Create DataFrame for plotting
    plan_df = pd.DataFrame({
        'Day': days,
        'Amount': amounts
    })
    
    # Calculate some metrics for annotations
    total_amount = sum(amounts)
    avg_daily = total_amount / len(days) if days else 0
    max_day = plan_df.loc[plan_df['Amount'].idxmax()]['Day'] if not plan_df.empty else ""
    min_day = plan_df.loc[plan_df['Amount'].idxmin()]['Day'] if not plan_df.empty else ""
    
    # Create a more visually appealing chart with gradient bars
    fig = go.Figure()
    
    # Add a single trace with customized marker for each bar
    fig.add_trace(go.Bar(
        x=plan_df['Day'],
        y=plan_df['Amount'],
        text=[f'₹{amt:.2f}' for amt in plan_df['Amount']],
        textposition='outside',
        textfont=dict(size=12),
        marker=dict(
            color=list(range(len(days))),
            colorscale='Viridis',
            line=dict(width=1, color='white')
        ),
        hovertemplate='<b>%{x}</b><br>Allowance: ₹%{y:.2f}<extra></extra>'
    ))
    
    # Add a line for the average daily amount
    fig.add_trace(go.Scatter(
        x=plan_df['Day'],
        y=[avg_daily] * len(days),
        mode='lines',
        name='Daily Average',
        line=dict(color='rgba(255, 99, 71, 0.7)', width=2, dash='dash'),
        hovertemplate='Average: ₹%{y:.2f}<extra></extra>'
    ))
    
    # Enhanced layout with better styling and typography
    fig.update_layout(
        title={
            'text': '<b>Weekly Spending Plan</b>',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=22, family="Arial", color="#2E4053")
        },
        xaxis=dict(
            title="Day of Week",
            titlefont=dict(size=14, family="Arial")
        ),
        yaxis=dict(
            title="Daily Allowance (₹)",
            titlefont=dict(size=14, family="Arial"),
            tickprefix="₹",
            gridcolor='rgba(230, 230, 230, 0.5)'
        ),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=80, b=60, l=60, r=40),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Add summary metrics in card format
    st.markdown("<h4 style='margin-top: 1rem;'>Weekly Budget Insights</h4>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    # Total weekly budget
    with cols[0]:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(33,150,243,0.1), rgba(33,150,243,0.05)); 
                    border-radius: 10px; padding: 15px; height: 100%;
                    border: 1px solid rgba(33,150,243,0.2);">
            <h5 style="color: #2196F3; margin-top: 0;">Weekly Total</h5>
            <div style="font-size: 1.5rem; font-weight: 600;">₹{total_amount:.2f}</div>
            <div style="font-size: 0.9rem; color: #666;">total budget</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Average daily allowance
    with cols[1]:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(156,39,176,0.1), rgba(156,39,176,0.05)); 
                    border-radius: 10px; padding: 15px; height: 100%;
                    border: 1px solid rgba(156,39,176,0.2);">
            <h5 style="color: #9C27B0; margin-top: 0;">Daily Average</h5>
            <div style="font-size: 1.5rem; font-weight: 600;">₹{avg_daily:.2f}</div>
            <div style="font-size: 0.9rem; color: #666;">per day</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Maximum allocation day
    with cols[2]:
        max_amount = plan_df['Amount'].max() if not plan_df.empty else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(76,175,80,0.1), rgba(76,175,80,0.05)); 
                    border-radius: 10px; padding: 15px; height: 100%;
                    border: 1px solid rgba(76,175,80,0.2);">
            <h5 style="color: #4CAF50; margin-top: 0;">Highest Budget</h5>
            <div style="font-size: 1.5rem; font-weight: 600;">₹{max_amount:.2f}</div>
            <div style="font-size: 0.9rem; color: #666;">on {max_day}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Minimum allocation day
    with cols[3]:
        min_amount = plan_df['Amount'].min() if not plan_df.empty else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255,152,0,0.1), rgba(255,152,0,0.05)); 
                    border-radius: 10px; padding: 15px; height: 100%;
                    border: 1px solid rgba(255,152,0,0.2);">
            <h5 style="color: #FF9800; margin-top: 0;">Lowest Budget</h5>
            <div style="font-size: 1.5rem; font-weight: 600;">₹{min_amount:.2f}</div>
            <div style="font-size: 0.9rem; color: #666;">on {min_day}</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Add spending tips based on the daily distribution
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f7fa, #f8f9fa); 
                border-radius: 10px; padding: 18px; margin-top: 1rem;
                border: 1px solid #e9ecef;">
        <h5 style="margin-top: 0; color: #2E4053;">💡 Smart Spending Tips</h5>
        <ul style="margin-bottom: 0; padding-left: 20px; color: #495057;">
            <li>Plan larger purchases on days with higher budget allocation</li>
            <li>Save 10-15% of each day's allowance for unexpected expenses</li>
            <li>Carry over unspent money from low-expense days to higher-expense days</li>
            <li>Track your daily spending to identify patterns and adjust your plan accordingly</li>
            <li>Use cash for daily expenses to make your spending more tangible</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
