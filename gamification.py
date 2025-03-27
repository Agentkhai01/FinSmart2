import streamlit as st
import pandas as pd
import numpy as np
import random
import json
from datetime import datetime, timedelta

# Initialize gamification elements if not already in session state
def initialize_gamification():
    if 'points' not in st.session_state:
        st.session_state.points = 0
    
    if 'streak' not in st.session_state:
        st.session_state.streak = 0
    
    if 'last_active' not in st.session_state:
        st.session_state.last_active = None
    
    if 'badges' not in st.session_state:
        st.session_state.badges = []
    
    if 'challenges' not in st.session_state:
        st.session_state.challenges = generate_challenges()
    
    if 'completed_challenges' not in st.session_state:
        st.session_state.completed_challenges = []
    
    if 'level' not in st.session_state:
        st.session_state.level = 1

    # Check for streak continuation
    check_streak()

def check_streak():
    """Check and update the user's login streak"""
    today = datetime.now().date()
    
    if st.session_state.last_active is None:
        # First time login
        st.session_state.streak = 1
        st.session_state.last_active = today
        add_points(10, "First login! +10 points")
        return
    
    last_active = st.session_state.last_active
    
    if isinstance(last_active, str):
        try:
            last_active = datetime.strptime(last_active, "%Y-%m-%d").date()
        except:
            last_active = today
    
    # If last active was yesterday, increase streak
    if (today - last_active).days == 1:
        st.session_state.streak += 1
        streak_points = min(10 + (st.session_state.streak // 5) * 5, 50)
        add_points(streak_points, f"Daily streak: {st.session_state.streak} days! +{streak_points} points")
        check_streak_badges()
    # If last active was today, do nothing
    elif (today - last_active).days == 0:
        pass
    # If more than 1 day has passed, reset streak
    else:
        if st.session_state.streak > 0:
            st.session_state.streak = 1
            add_points(10, "Welcome back! +10 points")
    
    st.session_state.last_active = today

def add_points(points, message=None):
    """Add points to the user's total and show a notification"""
    st.session_state.points += points
    
    # Check if level up is needed
    check_level_up()
    
    if message:
        if 'point_messages' not in st.session_state:
            st.session_state.point_messages = []
        st.session_state.point_messages.append(message)

def check_level_up():
    """Check if the user has enough points to level up"""
    # Points needed for each level (exponential growth)
    points_needed = 100 * (2 ** (st.session_state.level - 1))
    
    if st.session_state.points >= points_needed:
        st.session_state.level += 1
        if 'point_messages' not in st.session_state:
            st.session_state.point_messages = []
        st.session_state.point_messages.append(f"🎉 Level Up! You are now level {st.session_state.level}!")
        
        # Award badge for leveling up
        if st.session_state.level == 5:
            award_badge("Finance Apprentice", "Reached level 5")
        elif st.session_state.level == 10:
            award_badge("Finance Expert", "Reached level 10")
        elif st.session_state.level == 20:
            award_badge("Finance Master", "Reached level 20")

def check_streak_badges():
    """Award badges based on login streaks"""
    if st.session_state.streak == 7:
        award_badge("Weekly Warrior", "Logged in for 7 consecutive days")
    elif st.session_state.streak == 30:
        award_badge("Monthly Maven", "Logged in for 30 consecutive days")
    elif st.session_state.streak == 100:
        award_badge("Centurion", "Logged in for 100 consecutive days")

def award_badge(badge_name, badge_description):
    """Award a badge to the user"""
    if 'badges' not in st.session_state:
        st.session_state.badges = []
    
    # Don't add duplicate badges
    for badge in st.session_state.badges:
        if badge["name"] == badge_name:
            return
    
    badge = {
        "name": badge_name,
        "description": badge_description,
        "date_earned": datetime.now().strftime("%Y-%m-%d")
    }
    
    st.session_state.badges.append(badge)
    
    if 'point_messages' not in st.session_state:
        st.session_state.point_messages = []
    
    st.session_state.point_messages.append(f"🏆 New Badge: {badge_name}!")
    add_points(50, f"Badge earned: {badge_name} +50 points")

def generate_challenges():
    """Generate a set of challenges for the user"""
    all_challenges = [
        {"id": 1, "name": "Budget Master", "description": "Create a budget for at least 5 categories", "category": "budgeting", "points": 30, "progress_max": 5},
        {"id": 2, "name": "Expense Tracker", "description": "Log 10 expenses", "category": "tracking", "points": 20, "progress_max": 10},
        {"id": 3, "name": "Saving Star", "description": "Stay under budget for 3 categories in a month", "category": "saving", "points": 50, "progress_max": 3},
        {"id": 4, "name": "Data Analyst", "description": "View 5 different data visualizations", "category": "analysis", "points": 25, "progress_max": 5},
        {"id": 5, "name": "Investment Guru", "description": "Use all investment calculators at least once", "category": "investing", "points": 40, "progress_max": 4},
        {"id": 6, "name": "Export Expert", "description": "Export your financial data in all available formats", "category": "reports", "points": 15, "progress_max": 3},
        {"id": 7, "name": "Category Creator", "description": "Add expenses in 8 different categories", "category": "tracking", "points": 35, "progress_max": 8},
        {"id": 8, "name": "Notification Ninja", "description": "Set up budget alerts for 3 categories", "category": "budgeting", "points": 30, "progress_max": 3},
        {"id": 9, "name": "Goal Setter", "description": "Calculate SIP for 3 different financial goals", "category": "investing", "points": 45, "progress_max": 3},
        {"id": 10, "name": "Streak Keeper", "description": "Maintain a 5-day login streak", "category": "engagement", "points": 40, "progress_max": 5}
    ]
    
    # Initialize progress for each challenge
    for challenge in all_challenges:
        challenge["progress"] = 0
    
    # Return the full list of challenges
    return all_challenges

def update_challenge_progress(challenge_id, progress_increment=1):
    """Update progress for a specific challenge"""
    for challenge in st.session_state.challenges:
        if challenge["id"] == challenge_id:
            # Only update if not already completed
            if challenge["id"] not in [c["id"] for c in st.session_state.completed_challenges]:
                # Convert float to int if needed
                if isinstance(progress_increment, float):
                    increment = int(progress_increment) if progress_increment == int(progress_increment) else 1
                else:
                    increment = progress_increment
                
                challenge["progress"] = min(challenge["progress"] + increment, challenge["progress_max"])
                
                # Check if challenge is now complete
                if challenge["progress"] >= challenge["progress_max"]:
                    complete_challenge(challenge)
                
                return True
    return False

def complete_challenge(challenge):
    """Mark a challenge as complete and award points and possibly a badge"""
    # Only complete if not already completed
    if challenge["id"] not in [c["id"] for c in st.session_state.completed_challenges]:
        # Add to completed challenges list
        st.session_state.completed_challenges.append(challenge)
        
        # Award points
        add_points(challenge["points"], f"Challenge completed: {challenge['name']} +{challenge['points']} points")
        
        # For some special challenges, award badges
        if challenge["id"] == 1:  # Budget Master
            award_badge("Budget Planner", "Created budgets for multiple categories")
        elif challenge["id"] == 3:  # Saving Star
            award_badge("Saving Champion", "Stayed under budget consistently")
        elif challenge["id"] == 5:  # Investment Guru
            award_badge("Investment Planner", "Mastered all investment calculators")
        elif challenge["id"] == 10:  # Streak Keeper
            award_badge("Consistency King", "Maintained a solid login streak")

def check_challenges_for_expense_tracking(expense_data):
    """Check and update challenges related to expense tracking"""
    if not expense_data.empty:
        # Challenge 2: Log expenses
        update_challenge_progress(2, 1)  # Increment by 1 for each new expense
        
        # Challenge 7: Add expenses in different categories
        categories = expense_data['category'].unique()
        # Reset progress and set it to the current unique categories count
        for challenge in st.session_state.challenges:
            if challenge["id"] == 7:
                challenge["progress"] = min(len(categories), challenge["progress_max"])
                if challenge["progress"] >= challenge["progress_max"]:
                    complete_challenge(challenge)

def check_challenges_for_budget(budget_data):
    """Check and update challenges related to budgeting"""
    if budget_data:
        # Challenge 1: Create budgets for categories
        for challenge in st.session_state.challenges:
            if challenge["id"] == 1:
                challenge["progress"] = min(len(budget_data), challenge["progress_max"])
                if challenge["progress"] >= challenge["progress_max"]:
                    complete_challenge(challenge)
        
        # Challenge 8: Set up budget alerts (checked separately when alerts are configured)
        pass

def check_challenges_for_investing(calculator_used):
    """Check and update challenges related to investment calculators"""
    if calculator_used:
        # Challenge 5: Use all investment calculators
        if calculator_used == "sip":
            update_challenge_progress(5, 0.25)  # 1/4 of the challenge
        elif calculator_used == "lumpsum":
            update_challenge_progress(5, 0.25)  # 1/4 of the challenge
        elif calculator_used == "goal":
            update_challenge_progress(5, 0.25)  # 1/4 of the challenge
        elif calculator_used == "stepup":
            update_challenge_progress(5, 0.25)  # 1/4 of the challenge
        
        # Challenge 9: Calculate SIP for different goals
        if calculator_used == "goal":
            update_challenge_progress(9, 1)

def check_challenges_for_visualization():
    """Check and update challenges related to data visualization"""
    # Challenge 4: View data visualizations
    update_challenge_progress(4, 1)

def check_challenges_for_export(export_format):
    """Check and update challenges related to exporting data"""
    # Challenge 6: Export in different formats
    if export_format == "excel":
        for challenge in st.session_state.challenges:
            if challenge["id"] == 6:
                if challenge["progress"] == 0:
                    challenge["progress"] = 1
                elif challenge["progress"] == 2:
                    challenge["progress"] = 3
                    complete_challenge(challenge)
    elif export_format == "pdf":
        for challenge in st.session_state.challenges:
            if challenge["id"] == 6:
                if challenge["progress"] == 0:
                    challenge["progress"] = 2
                elif challenge["progress"] == 1:
                    challenge["progress"] = 3
                    complete_challenge(challenge)
    elif export_format == "csv":
        for challenge in st.session_state.challenges:
            if challenge["id"] == 6:
                if challenge["progress"] < 2:
                    challenge["progress"] += 1
                else:
                    challenge["progress"] = 3
                    complete_challenge(challenge)

def check_challenges_for_budget_performance(under_budget_categories):
    """Check and update challenges related to budget performance"""
    # Challenge 3: Stay under budget for categories
    if under_budget_categories:
        for challenge in st.session_state.challenges:
            if challenge["id"] == 3:
                challenge["progress"] = min(len(under_budget_categories), challenge["progress_max"])
                if challenge["progress"] >= challenge["progress_max"]:
                    complete_challenge(challenge)

def display_gamification_elements():
    """Display the main gamification UI elements"""
    initialize_gamification()
    
    # Display any point messages
    if 'point_messages' in st.session_state and st.session_state.point_messages:
        for message in st.session_state.point_messages:
            st.success(message)
        st.session_state.point_messages = []  # Clear messages after displaying
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Level", st.session_state.level)
    
    with col2:
        st.metric("Points", st.session_state.points)
    
    with col3:
        st.metric("Streak", f"{st.session_state.streak} days")
    
    # Progress bar for next level
    points_needed = 100 * (2 ** (st.session_state.level - 1))
    next_level_points = 100 * (2 ** st.session_state.level)
    progress = (st.session_state.points - points_needed) / (next_level_points - points_needed)
    
    st.write(f"Progress to Level {st.session_state.level + 1}:")
    st.progress(min(max(progress, 0), 1))
    st.write(f"{st.session_state.points}/{next_level_points} points needed")

def show_achievements():
    """Show the user's badges and achievements"""
    st.markdown("<h2 style='text-align: center;'>🏆 Achievements 🏆</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Badges", "Challenges"])
    
    with tab1:
        if not st.session_state.badges:
            st.info("You haven't earned any badges yet. Complete challenges and use the app regularly to earn badges!")
        else:
            # Display badges in a grid
            badges_per_row = 3
            for i in range(0, len(st.session_state.badges), badges_per_row):
                cols = st.columns(badges_per_row)
                for j in range(badges_per_row):
                    if i + j < len(st.session_state.badges):
                        badge = st.session_state.badges[i + j]
                        with cols[j]:
                            st.markdown(f"""
                            <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 10px; text-align: center;">
                                <h3>{badge['name']}</h3>
                                <p>{badge['description']}</p>
                                <p><small>Earned on: {badge['date_earned']}</small></p>
                            </div>
                            """, unsafe_allow_html=True)
    
    with tab2:
        # Separate challenges into ongoing and completed
        ongoing_challenges = [c for c in st.session_state.challenges if c["id"] not in [cc["id"] for cc in st.session_state.completed_challenges]]
        
        # Display ongoing challenges
        st.subheader("Ongoing Challenges")
        if not ongoing_challenges:
            st.info("You've completed all challenges! Great job!")
        else:
            for challenge in ongoing_challenges:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{challenge['name']}**: {challenge['description']}")
                    progress_pct = int((challenge['progress'] / challenge['progress_max']) * 100)
                    st.progress(challenge['progress'] / challenge['progress_max'])
                    st.write(f"Progress: {challenge['progress']}/{challenge['progress_max']} ({progress_pct}%)")
                with col2:
                    st.write(f"**Reward:** {challenge['points']} points")
        
        # Display completed challenges
        st.subheader("Completed Challenges")
        if not st.session_state.completed_challenges:
            st.info("Complete challenges to see them here!")
        else:
            for challenge in st.session_state.completed_challenges:
                st.markdown(f"""
                <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                    <h4>{challenge['name']} ✓</h4>
                    <p>{challenge['description']}</p>
                    <p><b>Reward:</b> {challenge['points']} points</p>
                </div>
                """, unsafe_allow_html=True)

def show_gamification_dashboard():
    """Show the main gamification dashboard"""
    st.markdown("<h1 style='text-align: center;'>🎮 Finance Game Center 🎮</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="margin-top: 0;">How It Works</h3>
        <p>Make finance fun by turning good financial habits into a game!</p>
        <ul>
            <li><b>Earn points</b> by tracking expenses, setting budgets, and using financial tools</li>
            <li><b>Level up</b> as you accumulate points and improve your financial habits</li>
            <li><b>Complete challenges</b> to earn badges and bonus points</li>
            <li><b>Maintain streaks</b> by using the app regularly</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Display main gamification elements
    display_gamification_elements()
    
    # Display badges and challenges
    show_achievements()
    
    # Show tips based on user's progress
    st.subheader("Financial Tips")
    
    tips = [
        "Track all your expenses, even small ones - they add up!",
        "Set realistic budgets that you can stick to",
        "Review your spending weekly to stay on track",
        "Save first, spend later - automate your savings",
        "Invest early and regularly to benefit from compounding",
        "Keep an emergency fund of 3-6 months of expenses",
        "Use the 50/30/20 rule: 50% needs, 30% wants, 20% savings",
        "Don't compare your financial journey to others",
        "Focus on long-term financial goals, not short-term gains",
        "Regularly check in on your investment performance"
    ]
    
    # Display 3 random tips
    selected_tips = random.sample(tips, 3)
    for i, tip in enumerate(selected_tips):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(33,150,243,0.1), rgba(33,150,243,0.05)); 
                    border-radius: 10px; padding: 10px; margin: 10px 0;">
            <p style="margin: 0;"><b>Tip {i+1}:</b> {tip}</p>
        </div>
        """, unsafe_allow_html=True)