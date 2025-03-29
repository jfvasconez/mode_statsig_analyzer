"""
Defines the Experiment model, representing a single analysis session.
"""

from datetime import datetime
from sqlalchemy.sql import func # For server-side default timestamp
from ..extensions import db # Import db from extensions.py


class Experiment(db.Model):
  """Model for storing experiment sessions."""
  __tablename__ = 'experiments' # Explicit table name

  id = db.Column(db.Integer, primary_key=True)
  # Store the name of the uploaded file, if available
  original_filename = db.Column(db.String(255), nullable=True)
  # Timestamp when the experiment record was created
  created_at = db.Column(
    db.DateTime(timezone=True),
    server_default=func.now(),
    nullable=False
  )

  # Relationships (will be defined more fully later)
  # One-to-Many: An Experiment can have multiple Variants
  variants = db.relationship('Variant', backref='experiment', lazy=True, cascade="all, delete-orphan")
  # One-to-Many: An Experiment can have multiple Funnel Steps
  funnel_steps = db.relationship('FunnelStep', backref='experiment', lazy=True, cascade="all, delete-orphan")

  def __repr__(self) -> str:
    return f'<Experiment {self.id} - {self.original_filename or "N/A"} @ {self.created_at}>' 