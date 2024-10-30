from flask import Flask, render_template, request, jsonify
import pickle
import requests
import pandas as pd
from flask_cors import CORS
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load the crop prediction model
with open('models/RandomForest.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

@app.route('/')
def index():
    return render_template('index.html')  # Main page

@app.route('/get_weather')
def weather_page():
    return render_template('get_weather.html')  # Weather page

@app.route('/get_crop_recommendation', methods=['GET', 'POST'])
def get_crop_recommendation():
    prediction = None
    if request.method == 'POST':
        npk_values = [float(request.form['N']), float(request.form['P']), float(request.form['K'])]
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        temperature = float(request.form['temperature'])  # Get user input for temperature
        humidity = float(request.form['humidity'])        # Get user input for humidity

        # Prepare input data for crop prediction
        data_df = pd.DataFrame({
            'N': [npk_values[0]],
            'P': [npk_values[1]],
            'K': [npk_values[2]],
            'temperature': [temperature],  # Use user input
            'humidity': [humidity],         # Use user input
            'ph': [ph],
            'rainfall': [rainfall]
        })

        # Use RandomForest model for prediction
        prediction = model.predict(data_df)[0]

    return render_template('get_crop_recommendation.html', prediction=prediction)

@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.get_json()  # Get JSON data from the request
    city = data.get('city')
    
    api_key = '6daa8091ea0a64e28c136f2a3a55a3b9'  # Your OpenWeather API key
    base_url = 'http://api.openweathermap.org/data/2.5/weather'

    # Construct URL to get current weather
    url = f'{base_url}?q={city}&appid={api_key}&units=metric'
    
    # Fetch weather data from the API
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        max_temp = data['main']['temp_max']
        min_temp = data['main']['temp_min']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        if 'sys' in data and 'sunrise' in data['sys'] and 'sunset' in data['sys']:
            sunrise_time = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')
            sunset_time = datetime.fromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')
        else:
            sunrise_time = "Unknown"
            sunset_time = "Unknown"

        # Create formatted weather report
        report = {
            'city': city,
            'maxTemp': max_temp,
            'minTemp': min_temp,
            'humidity': humidity,
            'windSpeed': wind_speed,
            'sunriseTime': sunrise_time,
            'sunsetTime': sunset_time
        }

        return jsonify(report)
    else:
        return jsonify({'error': 'Weather data not available for the given city.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
