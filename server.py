from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd

app = Flask(__name__)
CORS(app)

pipe = pickle.load(open('pipe.pkl', 'rb'))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        batting_team = data['batting_team']
        bowling_team = data['bowling_team']
        city = data['city']
        target = float(data['target'])
        score = float(data['score'])
        overs = float(data['overs'])
        wickets_out = float(data['wickets'])
        
        runs_left = target - score
        balls_left = 120 - (overs * 6)
        wickets = 10 - wickets_out
        
        if overs == 0:
            crr = 0
        else:
            crr = score / overs
            
        if balls_left == 0:
            rrr = 0
        else:
            rrr = (runs_left * 6) / balls_left
            
        input_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'city': [city],
            'runs_left': [runs_left],
            'balls_left': [balls_left],
            'wickets': [wickets],
            'total_runs_x': [target],
            'crr': [crr],
            'rrr': [rrr]
        })
        
        result = pipe.predict_proba(input_df)
        loss = result[0][0]
        win = result[0][1]
        
        return jsonify({
            'win': round(win * 100),
            'loss': round(loss * 100)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
