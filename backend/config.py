"""
Application configuration settings.
Loads sensitive data from environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
  """Base configuration settings."""
  SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'postgresql://mode_analyzer_user:bank123@localhost:5432/mode_analyzer_db' # Replace with your actual DB connection
  SQLALCHEMY_TRACK_MODIFICATIONS = False
