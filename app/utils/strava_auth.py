import requests
import os
from datetime import datetime
from app.db import db

def refresh_strava_token(user):
    if not user.refresh_token:
        return None  

    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')

    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': user.refresh_token
        }
    )

    if response.status_code == 200:
        tokens = response.json()
        user.access_token = tokens.get('access_token')
        user.refresh_token = tokens.get('refresh_token')  # may be new
        user.expires_at = tokens.get('expires_at')
        db.session.commit()
        return user.access_token
    else:
        print("Failed to refresh token:", response.text)
        return None
