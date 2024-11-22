from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import os
import base64
import requests

# Environment variables
API_TOKEN = os.getenv('ZERION_API', 'default_zerion_api_token')
MY_API_KEY = os.getenv('RAILWAY_API', 'default_railway_api_key')

app = Flask(__name__)
CORS(app)  # Enables CORS for all domains and routes

# Function to validate the API key
def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != MY_API_KEY:
        abort(401, 'Invalid API Key')

# Function to fetch raw data from Zerion API
def fetch_raw_data():
    encoded_api_key = base64.b64encode(API_TOKEN.encode('utf-8')).decode('utf-8')
    headers = {
        'accept': 'application/json',
        'authorization': f'Basic {encoded_api_key}'
    }
    url = 'https://api.zerion.io/v1/wallets/0x1bdb97985913d699b0fbd1aacf96d1f855d9e1d0/positions/?filter[positions]=no_filter&currency=usd&filter[trash]=only_non_trash&sort=value'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        abort(response.status_code, f"Error fetching data from Zerion API: {response.text}")
    return response.json()

@app.route('/raw_api')
def raw_api():
    validate_api_key()
    data = fetch_raw_data()
    return jsonify(data)

@app.route('/computed_api')
def computed_api():
    validate_api_key()
    data = fetch_raw_data()
    # Implement computation logic and return formatted results
    return jsonify(data)  # Placeholder, implement actual computation and formatting

if __name__ == '__main__':
    app.run(debug=True)
