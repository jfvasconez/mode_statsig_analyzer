"""
Model for experiments.
"""

from datetime import datetime
from ..extensions import db

class Experiment(db.Model):
  """
  Represents an experiment with variants and funnel steps.
  Each experiment has a name and creation timestamp.
  """
  __tablename__ = 'experiments' # Explicit table name
  
  id = db.Column(db.Integer, primary_key=True)
  experiment_name = db.Column(db.String(255), nullable=False)  # Changed from 'name' to 'experiment_name'
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  
  # Relationships
  variants = db.relationship('Variant', back_populates='experiment', cascade='all, delete-orphan')
  funnel_steps = db.relationship('FunnelStep', back_populates='experiment', cascade='all, delete-orphan')
  
  # Property for backward compatibility
  @property
  def name(self):
    return self.experiment_name
    
  # Setter for backward compatibility
  @name.setter
  def name(self, value):
    self.experiment_name = value
  
  def __repr__(self):
    return f"<Experiment id={self.id} name={self.experiment_name}>" 