import requests
from flask import Blueprint, render_template, session, redirect, url_for
from app.models import Activity, User
from app.db import db

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/activities')
def activities():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('auth.login')
                        )
    user = User.query.filter_by(strava_id=session.get('strava_id')).first()
    if not user:
        return redirect(url_for('auth.login')) 

    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code != 200:
        return f"Error fetching activities: {response.text}", 400

    data = response.json()
    activities = []
    for item in data:
        existing = Activity.query.get(item['id'])
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

        activities.append({
            'id': item['id'],
            'name': item['name'],
            'distance': item['distance'],
            'moving_time': item['moving_time'],
            'start_date': item['start_date_local'],
        })

    return render_template('activities.html', activities=activities)