import requests
import time
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for
from app.models import Activity, User
from app.db import db
from app.utils.strava_auth import refresh_strava_token

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/activities')
def activities():

    strava_id = session.get('strava_id')
    if not strava_id:
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(strava_id=session.get('strava_id')).first()
    if not user:
        return redirect(url_for('auth.login')) 
    
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('auth.login')
                        )

    after_timestamp = 0
    if user.last_synced:
        after_timestamp = int(user.last_synced.timestamp())

    if user.expires_at and user.expires_at < int(datetime.now(datetime.timezone.utc).timestamp()):
        new_token = refresh_strava_token(user)
        if not new_token:
            return redirect(url_for('auth.login'))  # fallback
        access_token = new_token
    else:
        access_token = session.get('access_token')

    all_activities = []
    page = 1
    while True:
        response = requests.get(
            'https://www.strava.com/api/v3/athlete/activities',
            headers={'Authorization': f'Bearer {access_token}'},
            params={'page': page, 'per_page': 200, 'after': after_timestamp}
        )

        if response.status_code != 200:
            return f"Error fetching activities: {response.text}", 400
        
        if response.status_code == 429:
             return "Rate limit exceeded. Try again in a few minutes.", 429

        data = response.json()
        if not data:
            break

        for item in data:
            existing = Activity.query.filter_by(id=item['id'], user_id=user.id).first()
            if not existing:
                new_activity = Activity(
                    id=item['id'],
                    user_id=user.id,
                    name=item.get('name'),
                    distance=item.get('distance'),
                    moving_time=item.get('moving_time'),
                    start_date=item.get('start_date')
                )
                db.session.add(new_activity)
                db.session.commit()

            all_activities.append({
                'id': item['id'],
                'name': item['name'],
                'distance': item['distance'],
                'moving_time': item['moving_time'],
                'start_date': item['start_date'],
            })

    page += 1

    user.last_synced = datetime.now(datetime.timezone.utc)
    db.session.commit()

    return render_template('activities.html', activities=activities)