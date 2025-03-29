"""
Defines the Variant model.
"""

from ..extensions import db


class Variant(db.Model):
  """Model for storing variant details and user counts."""
  __tablename__ = 'variants'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  user_count = db.Column(db.Integer, nullable=False)

  # Foreign Key to link back to the Experiment
  experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)

  # Relationships
  # One-to-Many: A Variant can have multiple StepResults
  step_results = db.relationship('StepResult', backref='variant', lazy=True, cascade="all, delete-orphan")

  def __repr__(self) -> str:
    return f'<Variant {self.id} - {self.name} ({self.user_count} users) for Exp {self.experiment_id}>' 