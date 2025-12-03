from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login session management."""
    from app.models import User
    return User.query.get(int(user_id))


def create_app():
    """Application factory for Hospital Management System."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
