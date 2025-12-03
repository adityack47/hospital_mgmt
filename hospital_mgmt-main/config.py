import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Core configuration for the Hospital Management System.
    Uses SQLite for local development as per project requirements.
    """

    # Secret key for session management
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hospital-dev-secret-key"

    # SQLite database path (created programmatically)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "hospital.db")

    # Disable unnecessary SQLAlchemy event tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False
