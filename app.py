import streamlit as st
import pandas as pd
import numpy as np
import base64
from datetime import datetime, timedelta
import expense_tracker
import budget_manager
import investment_calculator
import data_visualization
import utils
import notification_service
import gamification
import export_service

# Page configuration
st.set_page_config(
    page_title="Fin Smart: Student Finance Manager",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for an enhanced design with gradient nav bar and infographic styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        font-weight: 600;
    }
    .stMetric {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    .metric-row {
        background: linear-gradient(to right, #ffffff, #f9f9f9);
        border-radius: 12px;
        padding: 1.8rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
        border-left: 4px solid #4CAF50;
    }
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border: 1px solid #f0f0f0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .chart-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    /* Gradient Navigation Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
    }
    [data-testid="stSidebar"] .st-emotion-cache-1q1n0ol {
        color: white;
    }
    [data-testid="stSidebar"] .st-emotion-cache-ue6h4q {
        color: rgba(255, 255, 255, 0.8);
    }
    /* Style for radio buttons in sidebar */
    [data-testid="stSidebar"] [role="radiogroup"] {
        margin-top: 1rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: white;
    }
    /* Improved progress bars */
    [data-testid="stProgressBar"] > div {
        background: linear-gradient(to right, #4CAF50, #8BC34A);
        border-radius: 10px;
    }
    /* Infographic section styling */
    .infographic-box {
        background: linear-gradient(120deg, #f8f9fa, #ffffff);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        border-left: 4px solid #3B82F6;
        position: relative;
        overflow: hidden;
    }
    .infographic-box::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #3B82F6 50%, transparent 50%);
        border-radius: 0 0 0 12px;
    }
    /* Improved spacing and typography */
    .sidebar .block-container {
        padding-top: 2rem;
    }
    .st-emotion-cache-1gulkbx p, .st-emotion-cache-1gulkbx div {
        line-height: 1.5;
    }
    /* Custom header styling */
    .gradient-header {
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-weight: 600;
        text-align: center;
    }
    /* Custom pill indicators */
    .pill-indicator {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .pill-success {
        background-color: rgba(76, 175, 80, 0.15);
        color: #2E7D32;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }
    .pill-warning {
        background-color: rgba(255, 152, 0, 0.15);
        color: #EF6C00;
        border: 1px solid rgba(255, 152, 0, 0.3);
    }
    .pill-danger {
        background-color: rgba(244, 67, 54, 0.15);
        color: #D32F2F;
        border: 1px solid rgba(244, 67, 54, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data persistence
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=[
        'date', 'amount', 'category', 'description'
    ])

if 'budgets' not in st.session_state:
    st.session_state.budgets = {}

# Sidebar Navigation with gradient & icons
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <img src="https://img.icons8.com/color/96/000000/wallet--v1.png" width="80"/>
    <h1 style="color: white; font-size: 2rem; margin: 0.5rem 0;">Fin Smart</h1>
    <p style="color: rgba(255,255,255,0.8); margin-bottom: 2rem;">Your personal finance companion</p>
</div>
""", unsafe_allow_html=True)

# Create custom navigation buttons with gradient effect
nav_options = ["📊 Dashboard", "💰 Expense Tracker", "📈 Budget Manager", "📚 Investment Calculator", "📆 Spending Planner", "🔔 Notifications", "🎮 Finance Game", "📤 Export"]
selected_nav = st.session_state.get("nav_selected", nav_options[0])

for nav in nav_options:
    is_active = nav == selected_nav
    button_style = f"""
    <div style="
        margin-bottom: 0.5rem;
        background: {'rgba(255,255,255,0.15)' if is_active else 'transparent'};
        border-radius: 8px;
        padding: 0.7rem 1rem;
        cursor: pointer;
        transition: all 0.3s;
        border-left: {f'4px solid white' if is_active else '4px solid transparent'};
    ">
        <span style="color: white; font-weight: {'600' if is_active else '400'};">{nav}</span>
    </div>
    """
    if st.sidebar.markdown(button_style, unsafe_allow_html=True):
        st.session_state.nav_selected = nav
        st.rerun()

page = selected_nav

# Main content
if "Dashboard" in page:
    # Cleaner dashboard header
    st.markdown("<h1 style='font-size: 2.1rem; font-weight: 600; margin-bottom: 0.8rem;'>Financial Dashboard</h1>", unsafe_allow_html=True)
    
    # Display summary statistics
    if not st.session_state.expenses.empty:
        # Create a cleaner metrics row
        st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        # Calculate total expenses
        total_expenses = st.session_state.expenses['amount'].sum()
        col1.metric("Total Expenses", f"₹{total_expenses:.2f}")
        
        # Calculate expenses this month
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_expenses = st.session_state.expenses[
            (pd.to_datetime(st.session_state.expenses['date']).dt.month == current_month) &
            (pd.to_datetime(st.session_state.expenses['date']).dt.year == current_year)
        ]['amount'].sum()
        col2.metric("This Month", f"₹{monthly_expenses:.2f}")
        
        # Calculate today's expenses
        today = datetime.now().date()
        today_expenses = st.session_state.expenses[
            pd.to_datetime(st.session_state.expenses['date']).dt.date == today
        ]['amount'].sum()
        col3.metric("Today", f"₹{today_expenses:.2f}")
        
        # Add a budget utilization percentage
        if st.session_state.budgets:
            total_budget = sum(st.session_state.budgets.values())
            budget_used = (monthly_expenses / total_budget) * 100 if total_budget > 0 else 0
            col4.metric("Budget Used", f"{budget_used:.1f}%", 
                      f"{(100-budget_used):.1f}% left" if budget_used < 100 else "Over budget!")
        else:
            col4.metric("Budget Used", "N/A", "Set budget first")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Create visual dashboard in two columns
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            # Display expense breakdown by category in a clean container
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Expense Breakdown</h3>", unsafe_allow_html=True)
            data_visualization.plot_expense_by_category()
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_right:
            # Display recent expense history in a clean container
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Recent Transactions</h3>", unsafe_allow_html=True)
            
            if not st.session_state.expenses.empty:
                recent = st.session_state.expenses.sort_values(by='date', ascending=False).head(5)
                for _, expense in recent.iterrows():
                    exp_date = pd.to_datetime(expense['date']).strftime('%d %b')
                    st.markdown(f"""
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.8rem; padding-bottom: 0.8rem; border-bottom: 1px solid #f0f0f0;'>
                        <div>
                            <div style='font-weight: 500;'>{expense['category']}</div>
                            <div style='color: #666; font-size: 0.8rem;'>{exp_date} • {expense['description']}</div>
                        </div>
                        <div style='font-weight: 500; color: #FF5252;'>₹{expense['amount']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent transactions")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Budget vs actual in a clean container
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Budget vs. Actual Spending</h3>", unsafe_allow_html=True)
        if st.session_state.budgets:
            data_visualization.plot_budget_vs_actual()
        else:
            st.info("Set up your budgets in the Budget Manager to see comparisons here.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Trending over time
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Spending Trends</h3>", unsafe_allow_html=True)
        period = st.radio("View trend by:", ["Daily", "Weekly", "Monthly"], horizontal=True)
        data_visualization.plot_expense_over_time(period=period.lower())
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # For new users with no data
        st.markdown("""
        <div style='text-align: center; padding: 3rem 1rem;'>
            <img src="https://img.icons8.com/fluency/96/000000/plus-math.png" width="60"/>
            <h2 style='margin-top: 1rem;'>Get Started with Fin Smart</h2>
            <p style='color: #666; max-width: 500px; margin: 1rem auto;'>
                Start tracking your expenses to see your financial dashboard.
                Use the sidebar to navigate to the Expense Tracker and add your first expense.
            </p>
        </div>
        """, unsafe_allow_html=True)

elif page == "Expense Tracker":
    expense_tracker.show_expense_tracker()

elif page == "Budget Manager":
    budget_manager.show_budget_manager()

elif page == "Investment Calculator":
    investment_calculator.show_investment_calculator()

elif page == "Spending Planner":
    st.header("Weekly Spending Planner")
    
    pocket_money = st.number_input("Enter your weekly pocket money (₹)", 
                                   min_value=0.0, 
                                   value=1000.0, 
                                   step=100.0)
    
    st.subheader("Recommended Daily Spending Limits")
    
    # Calculate daily spending allowance
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Default distribution: equal allocation
    default_distribution = [1/7] * 7
    
    # Custom distribution option
    custom_dist = st.checkbox("Set custom distribution?")
    
    if custom_dist:
        st.write("Adjust the percentage allocation for each day (must sum to 100%)")
        
        # Initialize percentages in session state if not already present
        if 'day_percentages' not in st.session_state:
            st.session_state.day_percentages = [14.3, 14.3, 14.3, 14.3, 14.3, 14.3, 14.2]
        
        # Collect user inputs for percentages
        percentages = []
        cols = st.columns(7)
        total_percentage = 0
        
        for i, day in enumerate(days_of_week):
            with cols[i]:
                pct = st.number_input(day, min_value=0.0, max_value=100.0, 
                                      value=st.session_state.day_percentages[i],
                                      step=0.1, key=f"pct_{day}")
                percentages.append(pct)
                total_percentage += pct
        
        # Store the new percentages
        st.session_state.day_percentages = percentages
        
        # Validate that percentages sum to 100
        if abs(total_percentage - 100.0) > 0.1:  # Allow small floating point error
            st.error(f"Total percentage must be 100%. Current total: {total_percentage:.1f}%")
            distribution = default_distribution
        else:
            distribution = [p/100 for p in percentages]
    else:
        distribution = default_distribution
    
    # Calculate and display the daily allowances
    daily_amounts = [pocket_money * dist for dist in distribution]
    
    # Create a DataFrame for the spending plan
    spending_plan = pd.DataFrame({
        'Day': days_of_week,
        'Percentage': [f"{dist*100:.1f}%" for dist in distribution],
        'Amount (₹)': [f"₹{amt:.2f}" for amt in daily_amounts]
    })
    
    st.dataframe(spending_plan, use_container_width=True)
    
    # Visualization of the spending plan
    st.subheader("Visual Spending Plan")
    data_visualization.plot_spending_plan(days_of_week, daily_amounts)
    
    # Tips for daily spending management
    with st.expander("Tips for managing your daily spending"):
        st.write("""
        - Save a small percentage of your daily allowance for unexpected expenses
        - Avoid borrowing from tomorrow's budget unless absolutely necessary
        - Consider saving unused money at the end of each day for special purchases
        - Use cash instead of digital payments to make spending more tangible
        - Keep track of your daily expenses to see where your money is going
        """)

elif page == "Notifications":
    st.header("Budget Notifications")
    
    # Render the notification service page
    notification_service.show_notification_settings()
    
    # Run budget checks if notifications are enabled
    if st.session_state.get('notifications_enabled', False) and st.session_state.get('phone_number'):
        # Add an unobtrusive message about budget monitoring
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(33,150,243,0.1), rgba(33,150,243,0.05)); 
                    border-radius: 10px; padding: 15px; margin-top: 2rem;
                    border: 1px solid rgba(33,150,243,0.2);">
            <h5 style="color: #2196F3; margin-top: 0;">👋 SMS Alert Status</h5>
            <p style="margin-bottom: 0;">
                Budget alerts are active. We'll monitor your spending and send SMS notifications 
                when categories reach your set threshold of 
                <b>{st.session_state.get('alert_threshold', 80)}%</b>.
            </p>
        </div>
        """.format(threshold=st.session_state.get('alert_threshold', 80)), unsafe_allow_html=True)
        
        # Automatically check for budget alerts whenever this page is viewed
        alerts_sent = notification_service.check_budget_alerts()
        
        if alerts_sent:
            st.success(f"Alerts were sent for these categories: {', '.join(alerts_sent)}")
    
    # Add information about how notifications work
    with st.expander("How do budget notifications work?"):
        st.markdown("""
        ### SMS Budget Alerts

        Budget notifications help you stay on top of your spending by sending SMS alerts when you approach or exceed your preset budget limits. Here's how they work:

        1. **Enable notifications** - Toggle the switch to enable SMS alerts
        2. **Enter your phone number** - Make sure to include the country code (+91 for India)
        3. **Set your alert threshold** - Choose when you want to be notified (e.g., at 80% of budget)
        4. **Receive timely alerts** - Get SMS messages when any budget category crosses your threshold

        These alerts will help you avoid overspending and stay within your financial goals. The system checks your spending against your budget whenever you add new expenses.
        
        **Note:** SMS notifications require Twilio service configuration. If you're seeing an error about missing configuration, please contact support.
        """)
    
    # Add a section about responsible spending
    st.markdown("""
    <div style="margin-top: 2rem;">
        <h3>Benefits of Budget Notifications</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div style="background: linear-gradient(135deg, #f8f9fa, #ffffff); border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h5 style="color: #4CAF50;">🎯 Stay on Track</h5>
                <p style="font-size: 0.9rem; color: #495057;">
                    Get timely reminders when you're approaching your budget limits, helping you make adjustments before it's too late.
                </p>
            </div>
            <div style="background: linear-gradient(135deg, #f8f9fa, #ffffff); border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h5 style="color: #FF9800;">⏰ Real-time Alerts</h5>
                <p style="font-size: 0.9rem; color: #495057;">
                    Receive SMS notifications in real-time as soon as your spending crosses the threshold you've set.
                </p>
            </div>
            <div style="background: linear-gradient(135deg, #f8f9fa, #ffffff); border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h5 style="color: #2196F3;">📱 Mobile Convenience</h5>
                <p style="font-size: 0.9rem; color: #495057;">
                    Get alerts directly on your phone, even when you're not using the app, ensuring you never miss important budget updates.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "Finance Game":
    # Initialize gamification system
    gamification.initialize_gamification()
    
    # Show the gamification dashboard
    gamification.show_gamification_dashboard()
    
    # Update challenges based on current app state
    if not st.session_state.expenses.empty:
        gamification.check_challenges_for_expense_tracking(st.session_state.expenses)
    
    if st.session_state.budgets:
        gamification.check_challenges_for_budget(st.session_state.budgets)
    
    # Check for under-budget categories (for challenge 3)
    if not st.session_state.expenses.empty and st.session_state.budgets:
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_expenses = st.session_state.expenses[
            (pd.to_datetime(st.session_state.expenses['date']).dt.month == current_month) &
            (pd.to_datetime(st.session_state.expenses['date']).dt.year == current_year)
        ]
        
        under_budget_categories = []
        for category, budget in st.session_state.budgets.items():
            category_expenses = monthly_expenses[monthly_expenses['category'] == category]['amount'].sum()
            if category_expenses < budget:
                under_budget_categories.append(category)
        
        gamification.check_challenges_for_budget_performance(under_budget_categories)

elif page == "Export":
    st.markdown("<h1 style='font-size: 2.1rem; font-weight: 600; margin-bottom: 1.5rem;'>Export Financial Reports</h1>", unsafe_allow_html=True)
    
    # Add section about export options
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(33,150,243,0.1), rgba(33,150,243,0.05)); 
                border-radius: 10px; padding: 15px; margin-bottom: 20px;">
        <h4 style="margin-top: 0;">Export Your Financial Data</h4>
        <p style="margin-bottom: 0;">
            Export your financial data for record-keeping, tax purposes, or further analysis in external tools.
            Choose from multiple formats and customize what data to include in your exports.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show export options
    export_service.show_export_options()
    
    # Add CSV export option
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("<h3>CSV Export (Simple Format)</h3>", unsafe_allow_html=True)
    st.markdown("Export your data in CSV format for easy import into spreadsheet applications.")
    
    if st.session_state.expenses.empty:
        st.warning("You don't have any expense data yet. Add some expenses to enable export functionality.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("CSV Start date", 
                                    value=pd.to_datetime(st.session_state.expenses['date']).min().date() if not st.session_state.expenses.empty else datetime.now().date(),
                                    key="csv_start_date")
        with col2:
            end_date = st.date_input("CSV End date", 
                                value=datetime.now().date(),
                                key="csv_end_date")
        
        # Filter data by date range
        filtered_expenses = st.session_state.expenses[
            (pd.to_datetime(st.session_state.expenses['date']).dt.date >= start_date) &
            (pd.to_datetime(st.session_state.expenses['date']).dt.date <= end_date)
        ]
        
        if st.button("Generate CSV Export"):
            if filtered_expenses.empty:
                st.warning("No expenses found in the selected date range.")
            else:
                # Format date for better readability in CSV
                expenses_df = filtered_expenses.sort_values('date', ascending=False).copy()
                expenses_df['date'] = pd.to_datetime(expenses_df['date']).dt.strftime('%Y-%m-%d')
                
                # Generate CSV
                csv = expenses_df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="fin_smart_expenses.csv">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("CSV export generated successfully!")
                
                # Update gamification challenge for export
                gamification.check_challenges_for_export("csv")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "Fin Smart: Helping Indian students manage their finances smartly. "
    "© 2023-2025 Fin Smart"
)
