import streamlit as st
import pickle
import pandas as pd

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IPL Win Probability Predictor",
    page_icon="🏏",
    layout="centered"
)

# ── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
/* ── BACKGROUND ── */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── MAIN TITLE ── */
h1 {
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    background: linear-gradient(to right, #38bdf8, #8b5cf6) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-align: center !important;
}
.header-desc {
    text-align: center;
    color: #94a3b8;
    font-size: 1.05rem;
    margin-bottom: 1.5rem;
}

/* ── BUTTON ── */
div.stButton > button {
    background: linear-gradient(to right, #38bdf8, #8b5cf6) !important;
    color: #ffffff !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.45) !important;
}
/* Force button label white (Streamlit wraps in <p>) */
div.stButton > button p,
div.stButton > button span,
div.stButton > button div {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* ── WIDGET LABELS ── */
label, label p, label span,
.stSelectbox label, .stSelectbox label p,
.stNumberInput label, .stNumberInput label p,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
.stWidgetLabel, .stWidgetLabel p {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.80rem !important;
    letter-spacing: 0.07em !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── SELECTBOX ── */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div {
    background-color: #1e293b !important;
    border: 1px solid rgba(148, 163, 184, 0.35) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] [class$="singleValue"],
div[data-baseweb="select"] [class$="placeholder"],
div[data-baseweb="select"] input {
    color: #f1f5f9 !important;
    background: transparent !important;
    font-family: 'Outfit', sans-serif !important;
}
div[data-baseweb="select"] svg { fill: #94a3b8 !important; }

/* Dropdown panel */
div[data-baseweb="menu"],
div[data-baseweb="popover"] div {
    background-color: #1e293b !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
}
li[role="option"] {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    font-family: 'Outfit', sans-serif !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background-color: #334155 !important;
    color: #38bdf8 !important;
}

/* ── NUMBER INPUTS ── */
div[data-testid="stNumberInput"] input,
input[type="number"] {
    background-color: #1e293b !important;
    border: 1px solid rgba(148, 163, 184, 0.35) !important;
    color: #f1f5f9 !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
    font-family: 'Outfit', sans-serif !important;
    padding: 0.5rem 0.75rem !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2) !important;
    outline: none !important;
}
/* +/- stepper buttons */
div[data-testid="stNumberInput"] button {
    background-color: #334155 !important;
    color: #f1f5f9 !important;
    border: none !important;
    border-radius: 6px !important;
}

/* ── GENERAL TEXT inside app ── */
.stMarkdown p, .stMarkdown span, p, span {
    color: #e2e8f0;
    font-family: 'Outfit', sans-serif;
}

/* ── WARNINGS / ERRORS ── */
div[data-testid="stAlert"] {
    background-color: rgba(30, 41, 59, 0.8) !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ── IPL Logo ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-bottom:1.2rem;">
    <img src="https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/1200px-Indian_Premier_League_Official_Logo.svg.png"
         style="width:110px; filter:drop-shadow(0 4px 8px rgba(0,0,0,0.6));" alt="IPL Logo">
</div>
""", unsafe_allow_html=True)

st.title("IPL Win Predictor")
st.markdown('<p class="header-desc">Predict the 2nd innings run chase in real-time</p>', unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
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

# ── Load Model ────────────────────────────────────────────────────────────────
pipe = pickle.load(open('pipe.pkl', 'rb'))

# ── Form ──────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    batting_team = st.selectbox('Batting Team', sorted(teams), index=0)
with col2:
    bowling_team = st.selectbox('Bowling Team', sorted(teams), index=1)

selected_city = st.selectbox('Host City', sorted(cities))

st.markdown("<br>", unsafe_allow_html=True)

col3, col4, col5, col6 = st.columns(4)
with col3:
    target = st.number_input('Target Score', min_value=1, value=180, step=1)
with col4:
    score = st.number_input('Current Score', min_value=0, value=100, step=1)
with col5:
    overs = st.number_input('Overs Done', min_value=0.0, max_value=20.0, value=10.0, step=0.1)
with col6:
    wickets = st.number_input('Wickets Out', min_value=0, max_value=10, value=3, step=1)

st.markdown("<br>", unsafe_allow_html=True)

# ── Predict ───────────────────────────────────────────────────────────────────
if st.button('🏏 Calculate Win Probability'):

    if batting_team == bowling_team:
        st.warning("⚠️ Batting and Bowling teams cannot be the same!")

    elif score > target + 5:
        st.error("❌ Invalid: Current score cannot exceed the target by more than 5 runs.")

    else:
        # Boundary edge cases
        if score >= target:
            win, loss = 1.0, 0.0
        elif wickets == 10:
            win, loss = 0.0, 1.0
        else:
            runs_left  = target - score
            balls_left = max(0, int(120 - (overs * 6)))
            wickets_left = 10 - wickets

            crr = 0.0 if overs == 0 else score / overs
            rrr = 0.0 if balls_left == 0 else (runs_left * 6) / balls_left

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

            result = pipe.predict_proba(input_df)
            loss = result[0][0]
            win  = result[0][1]

        win_pct  = round(win * 100)
        loss_pct = round(loss * 100)

        # Results card
        st.markdown(f"""
<div style="background:rgba(255,255,255,0.05); padding:2rem; border-radius:20px;
            border:1px solid rgba(255,255,255,0.1); margin-top:1.5rem;
            box-shadow:0 20px 40px rgba(0,0,0,0.5);">

    <h3 style="text-align:center; margin-bottom:1.5rem; font-weight:700;
               color:#f8fafc; font-family:'Outfit',sans-serif;
               letter-spacing:0.08em; font-size:1rem;">MATCH PREDICTION</h3>

    <div style="margin-bottom:1.5rem;">
        <div style="display:flex; justify-content:space-between;
                    font-weight:600; font-size:1.1rem; margin-bottom:0.5rem;
                    color:#f1f5f9; font-family:'Outfit',sans-serif;">
            <span>{batting_team}</span>
            <span style="color:#10b981; font-size:1.4rem; font-weight:800;">{win_pct}%</span>
        </div>
        <div style="background:rgba(255,255,255,0.1); height:14px; border-radius:10px; overflow:hidden;">
            <div style="background:linear-gradient(90deg,#10b981,#059669);
                        width:{win_pct}%; height:100%; border-radius:10px;"></div>
        </div>
    </div>

    <div>
        <div style="display:flex; justify-content:space-between;
                    font-weight:600; font-size:1.1rem; margin-bottom:0.5rem;
                    color:#f1f5f9; font-family:'Outfit',sans-serif;">
            <span>{bowling_team}</span>
            <span style="color:#f43f5e; font-size:1.4rem; font-weight:800;">{loss_pct}%</span>
        </div>
        <div style="background:rgba(255,255,255,0.1); height:14px; border-radius:10px; overflow:hidden;">
            <div style="background:linear-gradient(90deg,#f43f5e,#e11d48);
                        width:{loss_pct}%; height:100%; border-radius:10px;"></div>
        </div>
    </div>

</div>
""", unsafe_allow_html=True)