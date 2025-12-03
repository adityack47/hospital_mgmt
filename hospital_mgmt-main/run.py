from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()


def ensure_admin_user():
    """
    Create a default admin user if it does not already exist.
    Admin account is created programmatically as per project rules.
    """
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        admin = User(
            name="Hospital Admin",
            email="admin@hospital.com",
            role="admin",
            password_hash=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created: admin@hospital.com / admin123")
    else:
        print("ℹ️ Admin user already exists")


if __name__ == "__main__":
    # Run one-time setup tasks
    with app.app_context():
        ensure_admin_user()

    # Start Flask development server
    app.run(debug=True)
