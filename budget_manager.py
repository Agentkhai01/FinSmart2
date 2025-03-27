import streamlit as st
import pandas as pd
from datetime import datetime
import data_visualization

def show_budget_manager():
    # Modern header with icon
    st.markdown("<h1 style='font-size: 2.1rem; font-weight: 600; margin-bottom: 1.5rem;'>📈 Budget Manager</h1>", unsafe_allow_html=True)
    
    # Initialize budget categories if not already in session state
    if 'budget_categories' not in st.session_state:
        st.session_state.budget_categories = [
            "Food & Drinks", "Groceries", "Transportation", 
            "Entertainment", "Shopping", "Bills & Utilities",
            "Education", "Housing & Rent", "Health", "Other"
        ]
    
    # Create tabs for setting budgets and viewing analysis with better styling
    tab1, tab2 = st.tabs(["Set Budgets", "Budget Analysis"])
    
    with tab1:
        # Card-like container for budget settings
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Set Your Budget Limits</h3>", unsafe_allow_html=True)
        
        # Budget period selection with improved UI
        col1, col2 = st.columns([2, 3])
        with col1:
            budget_period = st.selectbox(
                "Budget period",
                ["Monthly", "Weekly"],
                index=0,
                help="Set your budget period. Monthly is recommended for most expenses."
            )
        
        # Determine the current period for reference
        current_period = ""
        if budget_period == "Monthly":
            current_period = datetime.now().strftime("%B %Y")
        else:  # Weekly
            today = datetime.now().date()
            start_of_week = today - pd.Timedelta(days=today.weekday())
            end_of_week = start_of_week + pd.Timedelta(days=6)
            current_period = f"{start_of_week.strftime('%d %b')} - {end_of_week.strftime('%d %b %Y')}"
        
        st.write(f"Setting budget for: **{current_period}**")
        
        # Budget form
        with st.form(key="budget_form"):
            # Get a list of categories that need budgets
            categories_to_budget = st.session_state.budget_categories
            
            # For each category, allow the user to set a budget
            for category in categories_to_budget:
                # Get existing budget if any
                current_budget = st.session_state.budgets.get(category, 0.0)
                
                # Input for this category's budget
                new_budget = st.number_input(
                    f"Budget for {category} (₹)",
                    min_value=0.0,
                    value=current_budget,
                    step=100.0,
                    key=f"budget_{category}"
                )
                
                # Store in temporary dict
                st.session_state.budgets[category] = new_budget
            
            # Custom category option
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                new_category = st.text_input("Add a custom category (optional)")
            with col2:
                new_category_budget = st.number_input(
                    "Budget for custom category (₹)",
                    min_value=0.0,
                    value=0.0,
                    step=100.0
                )
            
            # Submit button
            submit_button = st.form_submit_button("Save Budget Settings")
            
            if submit_button:
                # Add the new custom category if provided
                if new_category and new_category not in st.session_state.budget_categories:
                    st.session_state.budget_categories.append(new_category)
                    st.session_state.budgets[new_category] = new_category_budget
                    st.success(f"Added new category: {new_category}")
                
                st.success("Budget settings saved successfully!")
        
        # Quick view of current budget allocation with better styling
        if st.session_state.budgets:
            st.markdown("<h3 style='margin-top: 1.5rem;'>Your Budget Allocation</h3>", unsafe_allow_html=True)
            
            # Filter out zero-budget categories
            active_budgets = {k: v for k, v in st.session_state.budgets.items() if v > 0}
            
            if active_budgets:
                # Display pie chart of budget allocation
                data_visualization.plot_budget_allocation(active_budgets)
                
                # Calculate total allocated budget
                total_allocated = sum(active_budgets.values())
                st.markdown(f"<p style='text-align: center; color: #666;'>Total allocated: <strong>₹{total_allocated:.2f}</strong></p>", unsafe_allow_html=True)
            else:
                st.info("Set your budget amounts above to see your allocation.")
        
        # Close the container div
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        # Card-like container for budget analysis
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Budget vs. Actual Spending</h3>", unsafe_allow_html=True)
        
        if not st.session_state.budgets or all(v == 0 for v in st.session_state.budgets.values()):
            st.info("Please set your budgets in the 'Set Budgets' tab to see analysis.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Date range for budget analysis
            if budget_period == "Monthly":
                current_month = datetime.now().month
                current_year = datetime.now().year
                
                # Get all expenses for the current month
                monthly_expenses = st.session_state.expenses[
                    (pd.to_datetime(st.session_state.expenses['date']).dt.month == current_month) &
                    (pd.to_datetime(st.session_state.expenses['date']).dt.year == current_year)
                ]
                
                period_text = datetime.now().strftime("%B %Y")
            else:  # Weekly
                today = datetime.now().date()
                start_of_week = today - pd.Timedelta(days=today.weekday())
                
                # Get all expenses for the current week
                weekly_expenses = st.session_state.expenses[
                    pd.to_datetime(st.session_state.expenses['date']).dt.date >= start_of_week
                ]
                
                monthly_expenses = weekly_expenses  # Reuse the variable name for code simplicity
                period_text = f"{start_of_week.strftime('%d %b')} - {(start_of_week + pd.Timedelta(days=6)).strftime('%d %b %Y')}"
            
            st.write(f"Showing budget analysis for: **{period_text}**")
            
            # Calculate spending by category
            category_spending = {}
            for category in st.session_state.budget_categories:
                category_expenses = monthly_expenses[monthly_expenses['category'] == category]
                total_spent = category_expenses['amount'].sum() if not category_expenses.empty else 0
                category_spending[category] = total_spent
            
            # Create progress bars for each category with budget
            for category, budget in st.session_state.budgets.items():
                if budget > 0:  # Only show categories with budget set
                    spent = category_spending.get(category, 0)
                    percentage = min(100, (spent / budget) * 100) if budget > 0 else 0
                    
                    # Determine color based on percentage
                    color = "green"
                    if percentage >= 80:
                        color = "red"
                    elif percentage >= 60:
                        color = "orange"
                    
                    # Display progress bar
                    st.write(f"**{category}**: ₹{spent:.2f} of ₹{budget:.2f}")
                    st.progress(percentage / 100)
                    
                    # Display warning if close to budget
                    remaining = budget - spent
                    if remaining < 0:
                        st.error(f"⚠️ Over budget by ₹{abs(remaining):.2f}")
                    elif remaining < (budget * 0.2):
                        st.warning(f"⚠️ Only ₹{remaining:.2f} left in budget")
                    
                    st.write("")  # Add space between categories
            
            # Overall budget summary
            total_budget = sum(st.session_state.budgets.values())
            total_spent = sum(category_spending.values())
            
            st.subheader("Overall Budget Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Budget", f"₹{total_budget:.2f}")
            
            with col2:
                st.metric("Total Spent", f"₹{total_spent:.2f}")
            
            with col3:
                remaining = total_budget - total_spent
                st.metric("Remaining", f"₹{remaining:.2f}", 
                         delta=f"{(remaining/total_budget)*100:.1f}%" if total_budget > 0 else "0%")
            
            # Visualization of budget vs. actual
            st.subheader("Budget vs. Actual Spending")
            data_visualization.plot_budget_vs_actual()
            
            # Budget saving tips with better styling
            with st.expander("Tips to stay within your budget"):
                st.markdown("""
                <div style="padding: 0.5rem 0;">
                    <div style="display: flex; margin-bottom: 0.5rem; align-items: center;">
                        <div style="margin-right: 0.5rem; color: #4CAF50;">✓</div>
                        <div><strong>Cook meals at home</strong> instead of eating out - save up to 70% on food costs</div>
                    </div>
                    <div style="display: flex; margin-bottom: 0.5rem; align-items: center;">
                        <div style="margin-right: 0.5rem; color: #4CAF50;">✓</div>
                        <div><strong>Use student discounts</strong> for entertainment, software, and services</div>
                    </div>
                    <div style="display: flex; margin-bottom: 0.5rem; align-items: center;">
                        <div style="margin-right: 0.5rem; color: #4CAF50;">✓</div>
                        <div><strong>Plan grocery shopping</strong> with a list to avoid impulse purchases</div>
                    </div>
                    <div style="display: flex; margin-bottom: 0.5rem; align-items: center;">
                        <div style="margin-right: 0.5rem; color: #4CAF50;">✓</div>
                        <div><strong>Use public transportation</strong> or carpool to save on travel expenses</div>
                    </div>
                    <div style="display: flex; margin-bottom: 0.5rem; align-items: center;">
                        <div style="margin-right: 0.5rem; color: #4CAF50;">✓</div>
                        <div><strong>Get second-hand textbooks</strong> or e-books instead of new editions</div>
                    </div>
                    <div style="display: flex; margin-bottom: 0.5rem; align-items: center;">
                        <div style="margin-right: 0.5rem; color: #4CAF50;">✓</div>
                        <div><strong>Use college resources</strong> like libraries, labs, and free software</div>
                    </div>
                    <div style="display: flex; margin-bottom: 0.5rem; align-items: center;">
                        <div style="margin-right: 0.5rem; color: #4CAF50;">✓</div>
                        <div><strong>Share subscription services</strong> like Netflix, Amazon Prime with roommates</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Close the container
            st.markdown("</div>", unsafe_allow_html=True)
