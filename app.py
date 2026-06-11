import streamlit as st
import pickle
import pandas as pd

# Set Page Config
st.set_page_config(
    page_title="IPL Win Probability Predictor",
    page_icon="🏏",
    layout="centered"
)

# Custom Premium Styling
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
    /* Main App Layout */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header Customization */
    h1 {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(to right, #38bdf8, #8b5cf6) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
    }
    .header-desc {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Input Container Styling */
    div[data-testid="stBlock"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    div.stButton > button {
        background: linear-gradient(to right, #38bdf8, #8b5cf6) !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        width: 100% !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.4) !important;
    }
    
    /* Input Labels */
    label p {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.05em !important;
    }
    
    /* Dropdowns and Number Inputs */
    div[data-baseweb="select"] > div {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    div[data-testid="stNumberInput"] input {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# IPL Logo at top
st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/1200px-Indian_Premier_League_Official_Logo.svg.png" 
             style="width: 130px; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.5));" alt="IPL Logo">
    </div>
""", unsafe_allow_html=True)

st.title("IPL Win Predictor")
st.markdown('<p class="header-desc">Predict the 2nd innings run chase in real-time</p>', unsafe_allow_html=True)

# Data Definition
teams = [
    'Chennai Super Kings', 'Delhi Capitals', 'Kings XI Punjab', 
    'Kolkata Knight Riders', 'Mumbai Indians', 'Rajasthan Royals', 
    'Royal Challengers Bangalore', 'Sunrisers Hyderabad'
]

cities = [
    'Abu Dhabi', 'Ahmedabad', 'Bangalore', 'Bengaluru', 'Bloemfontein', 
    'Cape Town', 'Centurion', 'Chandigarh', 'Chennai', 'Cuttack', 
    'Delhi', 'Dharamsala', 'Durban', 'East London', 'Hyderabad', 
    'Indore', 'Jaipur', 'Johannesburg', 'Kimberley', 'Kolkata', 
    'Mohali', 'Mumbai', 'Nagpur', 'Pune', 'Raipur', 'Ranchi', 
    'Sharjah', 'Visakhapatnam'
]

# Load ML Pipeline
pipe = pickle.load(open('pipe.pkl', 'rb'))

# Form inputs
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        batting_team = st.selectbox('Select Batting Team', sorted(teams), index=0)
    with col2:
        # Default select the second team to avoid same team warning on start
        bowling_team = st.selectbox('Select Bowling Team', sorted(teams), index=1)

    selected_city = st.selectbox('Select Host City', sorted(cities))

with st.container():
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        target = st.number_input('Target Score', min_value=1, value=180, step=1)
    with col4:
        score = st.number_input('Current Score', min_value=0, value=100, step=1)
    with col5:
        overs = st.number_input('Overs Completed', min_value=0.0, max_value=20.0, value=10.0, step=0.1)
    with col6:
        wickets = st.number_input('Wickets Out', min_value=0, max_value=10, value=3, step=1)

# Prediction Logic
if st.button('Calculate Probability'):
    # Validation 1: Batting and Bowling Team cannot be identical
    if batting_team == bowling_team:
        st.warning("⚠️ Batting Team and Bowling Team cannot be the same! Please select different teams.")
    
    # Validation 2: Score cannot exceed target by more than 5 runs
    elif score > target + 5:
        st.error("❌ Invalid Score: Current score cannot exceed the target by more than 5 runs.")
        
    else:
        # Business logic for boundary conditions
        if score >= target:
            win = 1.0
            loss = 0.0
        elif wickets == 10:
            win = 0.0
            loss = 1.0
        else:
            # Safe math inputs
            runs_left = target - score
            balls_left = int(120 - (overs * 6))
            
            # Bound balls remaining to positive to prevent negative Division errors
            if balls_left < 0:
                balls_left = 0
                
            wickets_left = 10 - wickets
            
            # Safe CRR Calculation
            if overs == 0:
                crr = 0.0
            else:
                crr = score / overs
                
            # Safe RRR Calculation
            if balls_left == 0:
                rrr = 0.0
            else:
                rrr = (runs_left * 6) / balls_left

            # Build Prediction Dataframe
            input_df = pd.DataFrame({
                'batting_team': [batting_team],
                'bowling_team': [bowling_team],
                'city': [selected_city],
                'runs_left': [runs_left],
                'balls_left': [balls_left],
                'wickets': [wickets_left],
                'total_runs_x': [target],
                'crr': [crr],
                'rrr': [rrr]
            })

            # Predict Probabilities
            result = pipe.predict_proba(input_df)
            loss = result[0][0]
            win = result[0][1]

        # Convert to percentage
        win_pct = round(win * 100)
        loss_pct = round(loss * 100)

        # Output Results using Styled Premium Progress Bars
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 20px; border: 1px solid rgba(255,255,255,0.08); margin-top: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <h3 style="text-align: center; margin-bottom: 1.5rem; font-weight: 600; color: #f8fafc; font-family: 'Outfit';">MATCH PREDICTION</h3>
                
                <!-- Batting Team Result -->
                <div style="margin-bottom: 1.5rem;">
                    <div style="display: flex; justify-content: space-between; font-weight: 600; font-size: 1.15rem; margin-bottom: 0.5rem; font-family: 'Outfit';">
                        <span>{batting_team} (Win)</span>
                        <span style="color: #10b981;">{win_pct}%</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); height: 14px; border-radius: 10px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #10b981, #059669); width: {win_pct}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
                
                <!-- Bowling Team Result -->
                <div>
                    <div style="display: flex; justify-content: space-between; font-weight: 600; font-size: 1.15rem; margin-bottom: 0.5rem; font-family: 'Outfit';">
                        <span>{bowling_team} (Win)</span>
                        <span style="color: #f43f5e;">{loss_pct}%</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); height: 14px; border-radius: 10px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #f43f5e, #e11d48); width: {loss_pct}%; height: 100%; border-radius: 10px;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)