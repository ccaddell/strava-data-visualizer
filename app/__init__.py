from flask import Flask
import os
from dotenv import load_dotenv
from .db import db


load_dotenv()

def create_app():
    
    app  = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///strava.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from .models import User, Activity
        db.create_all()

    from .routes.home import home_bp
    from .routes.auth import auth_bp
    from .routes.activities import activities_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(activities_bp)

    return app 