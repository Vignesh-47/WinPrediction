import streamlit as st
import pickle
import pandas as pd

st.set_page_config(
    page_title="IPL Win Probability Predictor",
    page_icon="🏏",
    layout="centered"
)

# Only inject CSS that the config.toml cannot handle: button gradient + results card
st.markdown(
"""<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
<style>
* { font-family: 'Outfit', sans-serif !important; }
h1 {
    background: linear-gradient(to right, #38bdf8, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    font-weight: 800 !important;
    font-size: 2.8rem !important;
}
div.stButton > button {
    background: linear-gradient(to right, #38bdf8, #8b5cf6) !important;
    color: #ffffff !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: none !important;
    width: 100% !important;
    padding: 0.75rem !important;
    margin-top: 0.5rem !important;
}
div.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-2px) !important;
}
div.stButton > button * { color: #ffffff !important; }
</style>""",
unsafe_allow_html=True
)

# Teams & Cities
teams = sorted([
    'Chennai Super Kings', 'Delhi Capitals', 'Kings XI Punjab',
    'Kolkata Knight Riders', 'Mumbai Indians', 'Rajasthan Royals',
    'Royal Challengers Bangalore', 'Sunrisers Hyderabad'
])

cities = sorted([
    'Abu Dhabi', 'Ahmedabad', 'Bangalore', 'Bengaluru', 'Bloemfontein',
    'Cape Town', 'Centurion', 'Chandigarh', 'Chennai', 'Cuttack',
    'Delhi', 'Dharamsala', 'Durban', 'East London', 'Hyderabad',
    'Indore', 'Jaipur', 'Johannesburg', 'Kimberley', 'Kolkata',
    'Mohali', 'Mumbai', 'Nagpur', 'Pune', 'Raipur', 'Ranchi',
    'Sharjah', 'Visakhapatnam'
])

pipe = pickle.load(open('pipe.pkl', 'rb'))

# ── Header ────────────────────────────────────────────────────────────────────
st.title("IPL Win Predictor")
st.markdown("<p style='text-align:center; color:#94a3b8; font-size:1.05rem;'>Predict the 2nd innings run chase in real-time</p>", unsafe_allow_html=True)
st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    batting_team = st.selectbox("Batting Team", teams, index=0)
with col2:
    bowling_team = st.selectbox("Bowling Team", teams, index=1)

selected_city = st.selectbox("Host City", cities)

st.markdown(" ")

col3, col4, col5, col6 = st.columns(4)
with col3:
    target = st.number_input("Target", min_value=1, value=180, step=1)
with col4:
    score = st.number_input("Score", min_value=0, value=100, step=1)
with col5:
    overs = st.number_input("Overs", min_value=0.0, max_value=20.0, value=10.0, step=0.1)
with col6:
    wickets = st.number_input("Wickets Out", min_value=0, max_value=10, value=3, step=1)

st.markdown(" ")

# ── Predict Button ────────────────────────────────────────────────────────────
if st.button("🏏  Calculate Win Probability"):

    if batting_team == bowling_team:
        st.warning("⚠️ Batting and Bowling teams cannot be the same!")

    elif score > target + 5:
        st.error("❌ Current score cannot exceed the target by more than 5 runs.")

    else:
        # Edge case handling
        if score >= target:
            win, loss = 1.0, 0.0
        elif wickets == 10:
            win, loss = 0.0, 1.0
        else:
            runs_left    = target - score
            balls_left   = max(0, int(120 - (overs * 6)))
            wickets_left = 10 - wickets
            crr = 0.0 if overs == 0 else score / overs
            rrr = 0.0 if balls_left == 0 else (runs_left * 6) / balls_left

            input_df = pd.DataFrame({
                'batting_team': [batting_team],
                'bowling_team': [bowling_team],
                'city':         [selected_city],
                'runs_left':    [runs_left],
                'balls_left':   [balls_left],
                'wickets':      [wickets_left],
                'total_runs_x': [target],
                'crr':          [crr],
                'rrr':          [rrr]
            })

            result = pipe.predict_proba(input_df)
            loss = result[0][0]
            win  = result[0][1]

        win_pct  = round(win * 100)
        loss_pct = round(loss * 100)

        st.divider()
        st.markdown("<h3 style='text-align:center; color:#f8fafc; letter-spacing:0.1em; font-size:0.95rem;'>MATCH PREDICTION</h3>", unsafe_allow_html=True)

        # Batting team bar
        st.markdown(f"<p style='margin-bottom:4px; color:#f1f5f9; font-weight:600;'>{batting_team} <span style='float:right; color:#10b981; font-size:1.3rem; font-weight:800;'>{win_pct}%</span></p>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:rgba(255,255,255,0.1); border-radius:10px; overflow:hidden; height:14px; margin-bottom:1.2rem;'><div style='width:{win_pct}%; height:100%; background:linear-gradient(90deg,#10b981,#059669); border-radius:10px;'></div></div>", unsafe_allow_html=True)

        # Bowling team bar
        st.markdown(f"<p style='margin-bottom:4px; color:#f1f5f9; font-weight:600;'>{bowling_team} <span style='float:right; color:#f43f5e; font-size:1.3rem; font-weight:800;'>{loss_pct}%</span></p>", unsafe_allow_html=True)
        st.markdown(f"<div style='background:rgba(255,255,255,0.1); border-radius:10px; overflow:hidden; height:14px;'><div style='width:{loss_pct}%; height:100%; background:linear-gradient(90deg,#f43f5e,#e11d48); border-radius:10px;'></div></div>", unsafe_allow_html=True)