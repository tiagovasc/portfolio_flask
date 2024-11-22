from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import os
import base64
import requests
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables
API_TOKEN = os.getenv('ZERION_API', 'default_zerion_api_token')
MY_API_KEY = os.getenv('RAILWAY_API', 'default_railway_api_key')

app = Flask(__name__)
CORS(app)  # Enables CORS for all domains and routes

def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != MY_API_KEY:
        logging.error('Invalid API Key provided.')
        abort(401, 'Invalid API Key')

def fetch_raw_data():
    encoded_api_key = base64.b64encode(API_TOKEN.encode('utf-8')).decode('utf-8')
    headers = {
        'accept': 'application/json',
        'authorization': f'Basic {encoded_api_key}'
    }
    url = 'https://api.zerion.io/v1/wallets/0x1bdb97985913d699b0fbd1aacf96d1f855d9e1d0/positions/?filter[positions]=no_filter&currency=usd&filter[trash]=only_non_trash&sort=value'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch data from Zerion API: Status Code: {response.status_code}, Response: {response.text}")
        abort(response.status_code, f"Error fetching data from Zerion API: {response.text}")
    return response.json()

def format_raw_api_data(data):
    formatted_data = []
    for item in data.get('data', []):
        attributes = item.get('attributes', {})
        fungible_info = attributes.get('fungible_info', {})
        formatted_entry = {
            'ticker': fungible_info.get('symbol', 'Unknown'),
            'name': fungible_info.get('name', 'Unknown'),
            'price': attributes.get('price', 'N/A'),
            'usdValue': attributes.get('value', 'N/A'),
            'quantity': attributes.get('quantity', {}).get('float', 'N/A')
        }
        formatted_data.append(formatted_entry)
    return formatted_data

def perform_computations(data):
    token_details = [item for item in format_raw_api_data(data) if item['usdValue'] >= 1000]
    total_vault_worth = sum(item['usdValue'] for item in token_details)
    return token_details, total_vault_worth

@app.route('/raw_api')
def raw_api():
    validate_api_key()
    data = fetch_raw_data()
    logging.info('Raw API data fetched successfully.')
    return jsonify(data)

@app.route('/computed_api')
def computed_api():
    validate_api_key()
    data = fetch_raw_data()
    computed_data, total_vault_worth = perform_computations(data)
    result = {
        'total_vault_worth': total_vault_worth,
        'computed_data': computed_data
    }
    logging.info('Computed API data prepared successfully.')
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
