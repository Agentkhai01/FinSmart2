# Fin Smart: Student Finance Manager

A comprehensive personal finance management platform designed specifically for Indian students and young professionals.

## Features

- **Expense Tracking**: Record and categorize daily expenses
- **Budget Management**: Set and monitor category-wise budgets
- **Investment Calculators**: SIP, Lumpsum, Goal-based, and Step-up SIP calculators
- **Visual Analytics**: Interactive charts and graphs for expense analysis
- **Weekly Spending Planner**: Plan your daily spending with customizable allocation
- **SMS Notifications**: Budget alerts via SMS using Twilio integration
- **Gamification System**: Earn points, complete challenges, and collect badges
- **Data Export**: Export financial data in multiple formats (Excel, PDF, CSV)

## Tech Stack

- Streamlit for the web interface
- Pandas for data manipulation
- Plotly for interactive visualizations
- Twilio for SMS notifications
- FPDF for PDF report generation
- XlsxWriter for Excel export

## Installation & Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fin-smart.git
   cd fin-smart
   ```

2. Install dependencies:
   ```
   pip install fpdf numpy openpyxl pandas plotly streamlit twilio xlsxwriter
   ```

3. Set up environment variables for Twilio integration:
   ```
   export TWILIO_ACCOUNT_SID="your_twilio_sid"
   export TWILIO_AUTH_TOKEN="your_twilio_auth_token"
   export TWILIO_PHONE_NUMBER="your_twilio_phone_number"
   ```

4. Run the application:
   ```
   streamlit run app.py
   ```

## Deployment

This application can be easily deployed on platforms like Render or Streamlit Cloud. The included Procfile makes deployment straightforward.

## License

MIT

## Acknowledgements

- Icons from Icons8
- Special thanks to the Streamlit team for the amazing framework