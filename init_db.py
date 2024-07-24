from app import app, db

with app.app_context():
    db.create_all()  # Creates tables based on models
