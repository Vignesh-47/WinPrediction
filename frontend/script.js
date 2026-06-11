const cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
'Sharjah', 'Mohali', 'Bengaluru'];

const citySelect = document.getElementById('city');
cities.sort().forEach(city => {
    const option = document.createElement('option');
    option.value = city;
    option.textContent = city;
    citySelect.appendChild(option);
});

// Smart Rule 1: Prevent selecting the same team
const battingTeamSelect = document.getElementById('batting-team');
const bowlingTeamSelect = document.getElementById('bowling-team');

function updateTeamDropdowns() {
    const batTeam = battingTeamSelect.value;
    const bowlTeam = bowlingTeamSelect.value;
    
    Array.from(bowlingTeamSelect.options).forEach(opt => {
        if(opt.value && opt.value === batTeam) {
            opt.disabled = true;
        } else {
            opt.disabled = false;
        }
    });

    Array.from(battingTeamSelect.options).forEach(opt => {
        if(opt.value && opt.value === bowlTeam) {
            opt.disabled = true;
        } else {
            opt.disabled = false;
        }
    });
}

battingTeamSelect.addEventListener('change', updateTeamDropdowns);
bowlingTeamSelect.addEventListener('change', updateTeamDropdowns);

document.getElementById('prediction-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('predict-btn');
    btn.innerHTML = '<span>Calculating...</span>';
    btn.style.opacity = '0.8';

    const payload = {
        batting_team: document.getElementById('batting-team').value,
        bowling_team: document.getElementById('bowling-team').value,
        city: document.getElementById('city').value,
        target: parseInt(document.getElementById('target').value),
        score: parseInt(document.getElementById('score').value),
        overs: document.getElementById('overs').value,
        wickets: parseInt(document.getElementById('wickets').value)
    };

    // Smart Rule 2: Cannot exceed target by more than 5 runs
    if (payload.score > payload.target + 5) {
        alert("Invalid input: The current score cannot exceed the target by more than 5 runs.");
        btn.innerHTML = '<span>Calculate Probability</span>';
        btn.style.opacity = '1';
        return;
    }

    // Smart Rule 3: If target is reached, 100% win
    if (payload.score >= payload.target) {
        showResults(payload.batting_team, payload.bowling_team, 100, 0);
        btn.innerHTML = '<span>Calculate Probability</span>';
        btn.style.opacity = '1';
        return;
    }

    // Smart Rule 4: If 10 wickets are down and target is not reached, 0% win
    if (payload.wickets === 10) {
        showResults(payload.batting_team, payload.bowling_team, 0, 100);
        btn.innerHTML = '<span>Calculate Probability</span>';
        btn.style.opacity = '1';
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if(data.error) {
            alert('Error: ' + data.error);
        } else {
            showResults(payload.batting_team, payload.bowling_team, data.win, data.loss);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to connect to the backend server. Make sure server.py is running.');
    } finally {
        btn.innerHTML = '<span>Calculate Probability</span>';
        btn.style.opacity = '1';
    }
});

function showResults(battingTeam, bowlingTeam, winProb, lossProb) {
    const resultContainer = document.getElementById('result-container');
    resultContainer.classList.remove('hidden');

    document.getElementById('bat-name').textContent = battingTeam + ' (Win)';
    document.getElementById('bowl-name').textContent = bowlingTeam + ' (Win)';

    // Reset animations
    document.getElementById('bat-bar').style.width = '0%';
    document.getElementById('bowl-bar').style.width = '0%';

    // Start animations
    setTimeout(() => {
        document.getElementById('bat-prob').textContent = winProb + '%';
        document.getElementById('bat-bar').style.width = winProb + '%';
        
        document.getElementById('bowl-prob').textContent = lossProb + '%';
        document.getElementById('bowl-bar').style.width = lossProb + '%';
    }, 100);
    
    // Scroll down to results smoothly
    resultContainer.scrollIntoView({ behavior: 'smooth' });
}
