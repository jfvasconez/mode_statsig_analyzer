"""
Main Flask application entry point.
Initializes extensions and registers blueprints.
"""

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from .config import Config
from .extensions import db
from . import models
from .routes.experiment_routes import experiment_bp

# Initialize Migrate
migrate = Migrate()

def create_app(config_class=Config) -> Flask:
  """Factory function to create and configure the Flask app."""
  app = Flask(__name__)
  app.config.from_object(config_class)

  # Enable CORS for all domains on all routes (adjust in production)
  CORS(app)

  # Initialize Flask extensions here
  db.init_app(app)
  migrate.init_app(app, db)

  # Register blueprints here
  app.register_blueprint(experiment_bp, url_prefix='/api/experiments')

  # A simple default route for testing
  @app.route('/')
  def hello():
    return "Hello from Backend!"

  return app

# Optional: Allow running the app directly using `python app.py`
# In production, use a proper WSGI server like Gunicorn or Waitress
if __name__ == '__main__':
  flask_app = create_app()
  flask_app.run(debug=True) # Enable debug mode for development
