"""
Shared Flask extensions instantiated here to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy

# Create a single SQLAlchemy instance to be used throughout the app
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app."""
    db.init_app(app)
    
    # Create tables if they don't exist
    with app.app_context():
        # Import models here to ensure they're registered
        from .models import experiment, variant, funnel_step, user_event, step_result
        db.create_all() 