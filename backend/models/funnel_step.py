"""
Model for funnel steps in an experiment.
"""

from ..extensions import db

class FunnelStep(db.Model):
  """
  Represents a step in the experiment funnel.
  Each step has a name and an order in the funnel.
  """
  __tablename__ = 'funnel_steps'

  id = db.Column(db.Integer, primary_key=True)
  experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
  name = db.Column(db.String(100), nullable=False)
  step_order = db.Column(db.Integer, nullable=False)
  
  # Relationships
  experiment = db.relationship('Experiment', back_populates='funnel_steps')
  step_results = db.relationship('StepResult', back_populates='funnel_step', cascade='all, delete-orphan')
  user_events = db.relationship('UserEvent', back_populates='funnel_step', cascade='all, delete-orphan')

  def __repr__(self):
    return f"<FunnelStep id={self.id} name={self.name} order={self.step_order}>" 