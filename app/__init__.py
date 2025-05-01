from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    
    app  = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

    from .routes.home import home_bp
    from .routes.auth import auth_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)

    return app 