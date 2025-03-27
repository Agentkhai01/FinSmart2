import streamlit as st
import pandas as pd
import io
import base64
import csv
from datetime import datetime
from fpdf import FPDF
import plotly.graph_objects as go
import zipfile

def export_to_excel(data_frames, sheet_names, filename="fin_smart_export.xlsx"):
    """
    Export multiple DataFrames to a single Excel file with multiple sheets
    
    Parameters:
    - data_frames: List of DataFrames to export
    - sheet_names: List of sheet names for each DataFrame
    - filename: Name of the Excel file
    
    Returns:
    - download_link: HTML link to download the Excel file
    """
    output = io.BytesIO()
    
    # Create Excel writer
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write each DataFrame to a different worksheet
        for df, sheet_name in zip(data_frames, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Add a format for the header
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D8E4BC',
                'border': 1
            })
            
            # Write the column headers with the defined format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Set the column width
            worksheet.set_column(0, len(df.columns) - 1, 15)
    
    # Get the Excel data
    data = output.getvalue()
    
    # Create a download link
    b64 = base64.b64encode(data).decode('utf-8')
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download Excel file</a>'
    
    return href

def export_to_pdf(data_frames, titles, filename="fin_smart_export.pdf"):
    """
    Export multiple DataFrames to a single PDF file
    
    Parameters:
    - data_frames: List of DataFrames to export
    - titles: List of titles for each DataFrame section
    - filename: Name of the PDF file
    
    Returns:
    - download_link: HTML link to download the PDF file
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add a title page
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 20, "Fin Smart: Financial Report", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.line(10, pdf.get_y() + 5, 200, pdf.get_y() + 5)
    pdf.ln(10)
    
    # Function to add table header
    def add_header(pdf, cols, col_widths):
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(200, 220, 255)
        for i, col in enumerate(cols):
            pdf.cell(col_widths[i], 10, col, 1, 0, "C", True)
        pdf.ln()
    
    # Function to add table row
    def add_row(pdf, row_data, col_widths):
        pdf.set_font("Arial", "", 10)
        for i, data in enumerate(row_data):
            pdf.cell(col_widths[i], 10, str(data)[:25], 1, 0, "L")
        pdf.ln()
    
    # For each DataFrame
    for df, title in zip(data_frames, titles):
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, ln=True, align='C')
        pdf.ln(5)
        
        if df.empty:
            pdf.set_font("Arial", "I", 12)
            pdf.cell(0, 10, "No data available", ln=True, align='C')
            continue
        
        # Calculate column widths based on the number of columns
        num_cols = len(df.columns)
        col_widths = [190 / num_cols] * num_cols  # 190mm is approximate width of A4
        
        # Add table header
        add_header(pdf, df.columns, col_widths)
        
        # Add table rows (limit to 100 rows to avoid excessive size)
        for _, row in df.head(100).iterrows():
            add_row(pdf, row.values, col_widths)
        
        if len(df) > 100:
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, f"Note: Showing only first 100 of {len(df)} records", ln=True, align='C')
    
    # Add summary page
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Financial Summary", ln=True, align='C')
    pdf.ln(5)
    
    # Add summary content if available in session state
    pdf.set_font("Arial", "", 12)
    if 'budgets' in st.session_state and st.session_state.budgets:
        pdf.cell(0, 10, "Budget Summary:", ln=True)
        pdf.ln(5)
        
        # Table header for budget
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(95, 10, "Category", 1, 0, "C", True)
        pdf.cell(95, 10, "Budget Amount (₹)", 1, 1, "C", True)
        
        # Budget data
        pdf.set_font("Arial", "", 10)
        for category, amount in st.session_state.budgets.items():
            pdf.cell(95, 10, category, 1, 0, "L")
            pdf.cell(95, 10, f"₹{amount:.2f}", 1, 1, "R")
    else:
        pdf.cell(0, 10, "No budget data available", ln=True)
    
    # Get PDF data
    pdf_data = pdf.output(dest="S").encode("latin1")
    
    # Create a download link
    b64 = base64.b64encode(pdf_data).decode('utf-8')
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download PDF Report</a>'
    
    return href

def show_export_options():
    """Display export options UI"""
    st.markdown("<div class='gradient-header'>Export Options</div>", unsafe_allow_html=True)
    
    if st.session_state.expenses.empty:
        st.warning("You don't have any expense data yet. Add some expenses to enable export functionality.")
        return
    
    with st.expander("Export Data"):
        # Select export format
        export_format = st.radio(
            "Choose export format:",
            ["Excel", "PDF"],
            horizontal=True
        )
        
        # Define date range for export
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date", 
                                     value=pd.to_datetime(st.session_state.expenses['date']).min().date() if not st.session_state.expenses.empty else datetime.now().date())
        with col2:
            end_date = st.date_input("End date", 
                                   value=datetime.now().date())
        
        # Filter data by date range
        filtered_expenses = st.session_state.expenses[
            (pd.to_datetime(st.session_state.expenses['date']).dt.date >= start_date) &
            (pd.to_datetime(st.session_state.expenses['date']).dt.date <= end_date)
        ]
        
        # What to include in export
        include_expenses = st.checkbox("Include expenses", value=True)
        include_budget = st.checkbox("Include budget information", value=True)
        include_summary = st.checkbox("Include summary statistics", value=True)
        
        if st.button("Generate Export"):
            # Prepare data for export
            data_frames = []
            titles = []
            
            # Include expenses if selected
            if include_expenses and not filtered_expenses.empty:
                # Sort expenses by date (newest first)
                expenses_df = filtered_expenses.sort_values('date', ascending=False).copy()
                # Format date for better readability
                expenses_df['date'] = pd.to_datetime(expenses_df['date']).dt.strftime('%Y-%m-%d')
                data_frames.append(expenses_df)
                titles.append("Expenses")
            
            # Include budget information if selected
            if include_budget and st.session_state.budgets:
                budget_df = pd.DataFrame({
                    'Category': list(st.session_state.budgets.keys()),
                    'Budget Amount (₹)': list(st.session_state.budgets.values())
                })
                data_frames.append(budget_df)
                titles.append("Budget Allocation")
            
            # Include summary statistics if selected
            if include_summary and not filtered_expenses.empty:
                # Group by category
                category_summary = filtered_expenses.groupby('category')['amount'].agg(['sum', 'count', 'mean']).reset_index()
                category_summary.columns = ['Category', 'Total Amount (₹)', 'Transaction Count', 'Average Transaction (₹)']
                
                # Total by month
                filtered_expenses['month'] = pd.to_datetime(filtered_expenses['date']).dt.strftime('%Y-%m')
                monthly_summary = filtered_expenses.groupby('month')['amount'].sum().reset_index()
                monthly_summary.columns = ['Month', 'Total Amount (₹)']
                
                data_frames.extend([category_summary, monthly_summary])
                titles.extend(["Category Summary", "Monthly Summary"])
            
            # Generate the export based on selected format
            if export_format == "Excel":
                sheet_names = titles  # Use titles as sheet names
                download_link = export_to_excel(data_frames, sheet_names)
                st.markdown(download_link, unsafe_allow_html=True)
            else:  # PDF
                download_link = export_to_pdf(data_frames, titles)
                st.markdown(download_link, unsafe_allow_html=True)
            
            st.success("Export generated successfully!")
    
    st.markdown("""
    <div style="margin-top: 20px; padding: 15px; border-radius: 10px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border: 1px solid #dee2e6;">
        <h4 style="margin-top: 0;">Export Features</h4>
        <ul style="margin-bottom: 0;">
            <li><strong>Excel Export:</strong> Generates a multi-sheet workbook with formatted tables for easy analysis</li>
            <li><strong>PDF Report:</strong> Creates a professional financial report with tables and summary information</li>
            <li><strong>Date Filtering:</strong> Export data for specific time periods</li>
            <li><strong>Customizable Content:</strong> Choose what to include in your exports</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)