from flask import Blueprint, redirect, request, session, url_for
from dotenv import load_dotenv
import requests
import os

load_dotenv()

auth_bp = Blueprint('auth', __name__)

CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
AUTH_URL = 'https://www.strava.com/oauth/authorize'
TOKEN_URL = 'https://www.strava.com/oauth/token'

@auth_bp.route('/login')
def login():
    params = {
        
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'read,activity:read,activity:read_all',
        'approval_prompt': 'force'
    }
    return redirect(f"{AUTH_URL}?{requests.compat.urlencode(params)}")

@auth_bp.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Authorization failed!", 400
    
    token_response = requests.post(TOKEN_URL, data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    })

    if token_response.status_code != 200:
        return f"Failed to fetch access token! Status code: {token_response.status_code}", 500
    
    token_data = token_response.json()
    session['access_token'] = token_data.get('access_token')
    
    if not session['access_token']:
        return "Failed to retrieve access token from response!", 500
    
    return redirect(url_for('auth.success'))

@auth_bp.route('/success')
def success():
    return "Authorization successful!"