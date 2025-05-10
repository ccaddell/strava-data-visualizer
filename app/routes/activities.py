import requests
from flask import Blueprint, render_template, session, redirect, url_for

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/activities')
def activities():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('auth.login'))

    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code == 200:
        activities = response.json()
        return render_template('activities.html', activities=activities)
    else:
        return f"Error fetching activities: {response.text}", 400
