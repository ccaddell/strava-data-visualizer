from flask import Blueprint, redirect, render_template, request, session, url_for
from dotenv import load_dotenv
import requests
import os
from app.models import db, User

load_dotenv()

auth_bp = Blueprint('auth', __name__)

CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
AUTH_URL = 'https://www.strava.com/oauth/authorize'
TOKEN_URL = 'https://www.strava.com/oauth/token'

@auth_bp.route('/')
def index():
    return '<a href="/login">Login with Strava</a>'

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
    
    # Retrieve athlete profile
    access_token = token_data.get('access_token')
    headers = {"Authorization": f"Bearer {access_token}"}
    athlete_response = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)

    if athlete_response.status_code != 200:
        return "Failed to fetch athlete profile!", 500
    
    athlete = athlete_response.json()

    # Store or update user in database
    user = User.query.filter_by(strava_id=athlete["id"]).first()
    if not user:
        user = User(strava_id=athlete["id"])
        db.session.add(user)

    user.firstname = athlete.get("firstname")
    user.lastname = athlete.get("lastname")
    user.access_token = access_token
    user.refresh_token = token_data.get("refresh_token")
    user.expires_at = token_data.get("expires_at")

    db.session.commit()

    # Set session info
    session['strava_id'] = athlete['id']
    session['access_token'] = access_token
    session['expires_at'] = token_data.get('expires_at')

    return redirect(url_for('activities.activities')) 
