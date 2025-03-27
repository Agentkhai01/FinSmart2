import streamlit as st
import pandas as pd
from datetime import datetime
import data_visualization

def show_expense_tracker():
    # More modern header with icon
    st.markdown("<h1 style='font-size: 2.1rem; font-weight: 600; margin-bottom: 1.5rem;'>💰 Expense Tracker</h1>", unsafe_allow_html=True)
    
    # Create tabs with custom styling
    tab1, tab2 = st.tabs(["Add Expense", "Expense History"])
    
    with tab1:
        # Create a card-like container for the form
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Record a New Expense</h3>", unsafe_allow_html=True)
        
        # Expense input form with better spacing
        with st.form(key="expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date", datetime.now().date())
                amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
            
            with col2:
                categories = [
                    "Food & Drinks", "Groceries", "Transportation", 
                    "Entertainment", "Shopping", "Bills & Utilities",
                    "Education", "Housing & Rent", "Health", "Other"
                ]
                category = st.selectbox("Category", categories)
                description = st.text_input("Description (Optional)")
            
            # More prominent submit button
            submit_button = st.form_submit_button(label="Add Expense", 
                                                use_container_width=True)
            
            if submit_button:
                if amount > 0:
                    # Add the expense to the session state
                    new_expense = pd.DataFrame({
                        'date': [date],
                        'amount': [amount],
                        'category': [category],
                        'description': [description]
                    })
                    
                    # Append to existing expenses
                    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], 
                                                         ignore_index=True)
                    
                    st.success("Expense added successfully!")
                else:
                    st.error("Please enter an amount greater than zero.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Quick expense summary in a stylish card
        if not st.session_state.expenses.empty:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("<h3>Recent Expenses</h3>", unsafe_allow_html=True)
            
            recent_expenses = st.session_state.expenses.sort_values(
                by='date', ascending=False).head(3)
            
            for _, expense in recent_expenses.iterrows():
                exp_date = pd.to_datetime(expense['date']).strftime('%d %b')
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; margin-bottom: 0.8rem; padding-bottom: 0.8rem; border-bottom: 1px solid #f0f0f0;'>
                    <div>
                        <div style='font-weight: 500;'>{expense['category']}</div>
                        <div style='color: #666; font-size: 0.8rem;'>{exp_date} • {expense['description'] if expense['description'] else 'No description'}</div>
                    </div>
                    <div style='font-weight: 500; color: #FF5252;'>₹{expense['amount']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        # Modern header and container design for expense history
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<h3>Expense History</h3>", unsafe_allow_html=True)
        
        if st.session_state.expenses.empty:
            st.info("No expenses recorded yet. Start by adding your first expense!")
        else:
            # Filter options in a cleaner layout
            st.markdown("<div style='background-color: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>", unsafe_allow_html=True)
            st.markdown("<h4>Filter Options</h4>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Date range filter with horizontal layout
                date_filter = st.radio(
                    "Filter by date",
                    ["All time", "This month", "Last 7 days", "Custom"],
                    horizontal=True
                )
                
                # Initialize start_date and end_date to avoid "possibly unbound" errors
                start_date = datetime.now().date() - pd.Timedelta(days=30)
                end_date = datetime.now().date()
                
                if date_filter == "Custom":
                    date_col1, date_col2 = st.columns(2)
                    with date_col1:
                        start_date = st.date_input("Start date", start_date)
                    with date_col2:
                        end_date = st.date_input("End date", end_date)
            
            with col2:
                # Category filter with better styling
                if not st.session_state.expenses.empty:
                    all_categories = st.session_state.expenses['category'].unique().tolist()
                    selected_categories = st.multiselect(
                        "Filter by category",
                        options=all_categories,
                        default=all_categories
                    )
                else:
                    selected_categories = []
                    
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Apply filters
            filtered_expenses = st.session_state.expenses.copy()
            
            # Apply date filter
            if date_filter == "This month":
                current_month = datetime.now().month
                current_year = datetime.now().year
                filtered_expenses = filtered_expenses[
                    (pd.to_datetime(filtered_expenses['date']).dt.month == current_month) &
                    (pd.to_datetime(filtered_expenses['date']).dt.year == current_year)
                ]
            elif date_filter == "Last 7 days":
                last_week = datetime.now().date() - pd.Timedelta(days=7)
                filtered_expenses = filtered_expenses[
                    pd.to_datetime(filtered_expenses['date']).dt.date >= last_week
                ]
            elif date_filter == "Custom":
                filtered_expenses = filtered_expenses[
                    (pd.to_datetime(filtered_expenses['date']).dt.date >= start_date) &
                    (pd.to_datetime(filtered_expenses['date']).dt.date <= end_date)
                ]
            
            # Apply category filter
            if selected_categories:
                filtered_expenses = filtered_expenses[
                    filtered_expenses['category'].isin(selected_categories)
                ]
            
            # Display filtered data with visual enhancements
            if filtered_expenses.empty:
                st.info("No expenses match your filters.")
            else:
                # Display summary statistics with card-like styling
                total_filtered = filtered_expenses['amount'].sum()
                
                # Summary metrics in a row
                metric_cols = st.columns(3)
                metric_cols[0].metric("Total Expenses", f"₹{total_filtered:.2f}")
                
                # Add count of transactions
                transaction_count = len(filtered_expenses)
                metric_cols[1].metric("Transactions", f"{transaction_count}")
                
                # Calculate average expense
                avg_expense = total_filtered / transaction_count if transaction_count > 0 else 0
                metric_cols[2].metric("Average Expense", f"₹{avg_expense:.2f}")
                
                # Visual expense breakdown in a card
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.markdown("<h3>Expense Breakdown</h3>", unsafe_allow_html=True)
                data_visualization.plot_expense_by_category(filtered_expenses)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Display expense table in a card with nicer formatting
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.markdown("<h3>Expense Details</h3>", unsafe_allow_html=True)
                
                # Sort by date (most recent first)
                display_df = filtered_expenses.sort_values(by='date', ascending=False)
                
                # Format for display
                display_df = display_df.copy()
                display_df['amount'] = display_df['amount'].apply(lambda x: f"₹{x:.2f}")
                display_df = display_df.rename(columns={
                    'date': 'Date',
                    'amount': 'Amount',
                    'category': 'Category',
                    'description': 'Description'
                })
                
                st.dataframe(
                    display_df, 
                    use_container_width=True,
                    column_config={
                        "Amount": st.column_config.TextColumn(
                            "Amount",
                            help="Expense amount",
                            width="medium"
                        ),
                        "Category": st.column_config.TextColumn(
                            "Category",
                            width="medium"
                        )
                    }
                )
                
                # Export option with better styling
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("Export as CSV", use_container_width=True):
                        csv = filtered_expenses.to_csv(index=False)
                        st.download_button(
                            label="Download CSV File",
                            data=csv,
                            file_name="my_expenses.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                st.markdown("</div>", unsafe_allow_html=True)
                
        # Close the main container
        st.markdown("</div>", unsafe_allow_html=True)
