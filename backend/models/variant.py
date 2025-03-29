"""
Model for experiment variants.
"""

from ..extensions import db


class Variant(db.Model):
  """
  Represents a variant in an experiment.
  A variant can be the control group or a test group.
  """
  __tablename__ = 'variants'

  id = db.Column(db.Integer, primary_key=True)
  experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), nullable=False)
  variant_name = db.Column(db.String(100), nullable=False)
  user_count = db.Column(db.Integer, nullable=False, default=0)
  
  # Relationships
  experiment = db.relationship('Experiment', back_populates='variants')
  step_results = db.relationship('StepResult', back_populates='variant', cascade='all, delete-orphan')
  user_events = db.relationship('UserEvent', back_populates='variant', cascade='all, delete-orphan')

  def __repr__(self):
    return f"<Variant id={self.id} name={self.variant_name} users={self.user_count}>" 