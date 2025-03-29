"""
Defines the FunnelStep model.
"""

from ..extensions import db


class FunnelStep(db.Model):
  """Model for storing funnel step names."""
  __tablename__ = 'funnel_steps'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), nullable=False) # e.g., 'Goals', 'Protections'

  # Foreign Key to link back to the Experiment
  experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)

  # Relationships
  # One-to-Many: A FunnelStep can have multiple StepResults
  step_results = db.relationship('StepResult', backref='funnel_step', lazy=True, cascade="all, delete-orphan")

  def __repr__(self) -> str:
    return f'<FunnelStep {self.id} - {self.name} for Exp {self.experiment_id}>' 