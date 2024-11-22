import os
import base64
import requests
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

# Zerion API Key, accessed securely from environment variables
API_TOKEN = os.getenv('API_TOKEN', 'default_zerion_api_token')
# Railway API Key, accessed securely from environment variables
MY_API_KEY = os.getenv('MY_API_KEY', 'default_railway_api_key')

app = FastAPI()

# Enable CORS to allow calls from browsers or client-side applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins if necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define API Key header for authentication
api_key_header = APIKeyHeader(name='X-API-Key')

# Dependency function to validate the API key
async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != MY_API_KEY:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

# Function to fetch raw data from Zerion API
def fetch_raw_data():
    # Encode the Zerion API key
    encoded_api_key = base64.b64encode(API_TOKEN.encode('utf-8')).decode('utf-8')

    headers = {
        'accept': 'application/json',
        'authorization': f'Basic {encoded_api_key}'
    }

    # Zerion API endpoint (replace wallet address if needed)
    url = 'https://api.zerion.io/v1/wallets/0x1bdb97985913d699b0fbd1aacf96d1f855d9e1d0/positions/?filter[positions]=no_filter&currency=usd&filter[trash]=only_non_trash&sort=value'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error fetching data from Zerion API: {response.text}"
        )

# Function to format raw API data
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

# Function to perform computations and return results
def compute_results(data):
    # Extract and compute token details
    # Implementing computations similar to those in your original script
    # This function would be similar to the `compute_results` you already defined.
    # Return results based on the provided data
    # Omitted here for brevity, implement based on your business logic

# Endpoint for raw API data
@app.get("/raw_api")
async def raw_api(api_key: str = Depends(get_api_key)):
    data = fetch_raw_data()
    formatted_data = format_raw_api_data(data)
    return formatted_data

# Endpoint for computed results
@app.get("/computed_api")
async def computed_api(api_key: str = Depends(get_api_key)):
    data = fetch_raw_data()
    results = compute_results(data)
    return results
