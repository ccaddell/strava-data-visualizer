from .db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strava_id = db.Column(db.Integer, unique=True, nullable=False)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    access_token = db.Column(db.String(255))
    refresh_token = db.Column(db.String(255))
    expires_at = db.Column(db.Integer)

    def __repr__(self):
        return f"<User {self.name}>"

class Activity(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)  # Strava activity ID
    name = db.Column(db.String(256))
    distance = db.Column(db.Float)
    moving_time = db.Column(db.Integer)
    start_date = db.Column(db.String(64))

    def __repr__(self):
        return f"<Activity {self.name}>"