import os
import streamlit as st
from twilio.rest import Client

def send_budget_alert(user_phone, category, budget_amount, spent_amount, percentage):
    """
    Send SMS notification for budget alerts
    
    Parameters:
    - user_phone: User's phone number (with country code)
    - category: Budget category that triggered the alert
    - budget_amount: The budget amount for the category
    - spent_amount: The amount spent in this category
    - percentage: The percentage of budget used
    
    Returns:
    - Boolean indicating if the message was sent successfully
    - Status message
    """
    # Check if Twilio credentials are available
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
        return False, "Twilio credentials not configured. Contact support to enable SMS alerts."
    
    try:
        # Format the phone number (ensure it has country code)
        if not user_phone.startswith('+'):
            user_phone = '+91' + user_phone  # Default to India country code if not provided
        
        # Create Twilio client
        client = Client(twilio_account_sid, twilio_auth_token)
        
        # Construct the message
        status_word = "CRITICAL" if percentage >= 100 else "WARNING"
        message_body = f"""
FinSmart Budget {status_word}:
Your {category} budget is at {percentage:.1f}%.
Budget: ₹{budget_amount:.2f}
Spent: ₹{spent_amount:.2f}
Remaining: ₹{max(0, budget_amount - spent_amount):.2f}

Reply STOP to unsubscribe.
        """
        
        # Send the message
        message = client.messages.create(
            body=message_body, 
            from_=twilio_phone_number, 
            to=user_phone
        )
        
        return True, f"Alert sent. SID: {message.sid}"
    
    except Exception as e:
        return False, f"Failed to send alert: {str(e)}"


def show_notification_settings():
    """Display and manage notification settings"""
    st.markdown("<div class='gradient-header'>Budget Alert Notifications</div>", unsafe_allow_html=True)
    
    # Initialize notification settings in session state if not present
    if 'notifications_enabled' not in st.session_state:
        st.session_state.notifications_enabled = False
    
    if 'phone_number' not in st.session_state:
        st.session_state.phone_number = ""
    
    if 'alert_threshold' not in st.session_state:
        st.session_state.alert_threshold = 80  # Default to 80% of budget
        
    # Check if Twilio credentials are configured
    twilio_configured = all([
        os.environ.get('TWILIO_ACCOUNT_SID'),
        os.environ.get('TWILIO_AUTH_TOKEN'),
        os.environ.get('TWILIO_PHONE_NUMBER')
    ])
    
    if not twilio_configured:
        st.warning("⚠️ SMS notifications require Twilio configuration. Please contact support to enable this feature.")
        
    # Display notification settings in a styled container
    with st.container():
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); 
                    border-radius: 10px; padding: 18px; margin-bottom: 1rem;
                    border: 1px solid #dee2e6;">
            <h5 style="margin-top: 0; color: #2E4053;">SMS Budget Alerts</h5>
            <p style="margin-bottom: 1rem; color: #495057;">
                Receive SMS notifications when your spending approaches or exceeds your budget limits.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enable/disable notifications
        enable_notifications = st.toggle(
            "Enable SMS Notifications", 
            value=st.session_state.notifications_enabled,
            disabled=not twilio_configured
        )
        
        if enable_notifications != st.session_state.notifications_enabled:
            st.session_state.notifications_enabled = enable_notifications
            if enable_notifications:
                st.success("SMS notifications enabled!")
            else:
                st.info("SMS notifications disabled.")
        
        # Phone number input (only show if notifications are enabled)
        if st.session_state.notifications_enabled:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                phone_number = st.text_input(
                    "Phone Number (with country code)", 
                    value=st.session_state.phone_number,
                    placeholder="+91XXXXXXXXXX"
                )
                
                if phone_number != st.session_state.phone_number:
                    st.session_state.phone_number = phone_number
            
            with col2:
                # Alert threshold slider
                alert_threshold = st.slider(
                    "Alert Threshold (%)", 
                    min_value=50, 
                    max_value=100,
                    value=st.session_state.alert_threshold, 
                    step=5,
                    help="Receive alerts when your spending reaches this percentage of your budget."
                )
                
                if alert_threshold != st.session_state.alert_threshold:
                    st.session_state.alert_threshold = alert_threshold
            
            # Display example message
            with st.expander("What will the SMS alert look like?"):
                st.markdown(f"""
                ```
                FinSmart Budget WARNING:
                Your Food budget is at {alert_threshold}%.
                Budget: ₹5000.00
                Spent: ₹{5000 * alert_threshold / 100:.2f}
                Remaining: ₹{5000 * (1 - alert_threshold / 100):.2f}
                
                Reply STOP to unsubscribe.
                ```
                """)
            
            # Test notification button
            if st.button("Send Test Alert", disabled=not (phone_number and twilio_configured)):
                success, message = send_budget_alert(
                    phone_number, 
                    "Test", 
                    1000, 
                    800, 
                    80
                )
                
                if success:
                    st.success(f"Test alert sent successfully! Check your phone.")
                else:
                    st.error(f"Failed to send test alert: {message}")


def check_budget_alerts():
    """
    Check if any budget categories have crossed the alert threshold and
    send notifications if enabled
    """
    if not st.session_state.get('notifications_enabled', False):
        return  # Skip if notifications are disabled
    
    if not st.session_state.get('phone_number'):
        return  # Skip if no phone number provided
    
    if not st.session_state.budgets or st.session_state.expenses.empty:
        return  # Skip if no budgets or expenses yet
    
    # Get the alert threshold from session state
    alert_threshold = st.session_state.get('alert_threshold', 80)
    
    # Get the current month and year
    from datetime import datetime
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Filter expenses for the current month
    import pandas as pd
    monthly_expenses = st.session_state.expenses[
        (pd.to_datetime(st.session_state.expenses['date']).dt.month == current_month) &
        (pd.to_datetime(st.session_state.expenses['date']).dt.year == current_year)
    ]
    
    # Get category totals
    category_expenses = monthly_expenses.groupby('category')['amount'].sum().to_dict()
    
    # Track categories that need alerts
    alerts_sent = []
    
    # Check each category against its budget
    for category, budget in st.session_state.budgets.items():
        if budget <= 0:
            continue  # Skip categories with no budget
        
        spent = category_expenses.get(category, 0)
        percentage = (spent / budget) * 100
        
        # Only alert if percentage is above threshold and we haven't alerted for this before
        alert_key = f"alerted_{category}_{current_month}_{current_year}"
        already_alerted = st.session_state.get(alert_key, False)
        
        if percentage >= alert_threshold and not already_alerted:
            # Send alert
            success, message = send_budget_alert(
                st.session_state.phone_number,
                category,
                budget,
                spent,
                percentage
            )
            
            if success:
                # Mark this category as alerted for this month to avoid duplicate alerts
                st.session_state[alert_key] = True
                alerts_sent.append(category)
    
    return alerts_sent