"""
Model for step results in an experiment.
"""

from ..extensions import db

class StepResult(db.Model):
  """
  Represents the aggregated results for a funnel step for a variant.
  Includes metrics such as posterior mean, credible intervals, and 
  probability vs control.
  """
  __tablename__ = 'step_results'

  id = db.Column(db.Integer, primary_key=True)
  variant_id = db.Column(db.Integer, db.ForeignKey('variants.id'), nullable=False)
  funnel_step_id = db.Column(db.Integer, db.ForeignKey('funnel_steps.id'), nullable=False)
  
  # Metrics
  converted_count = db.Column(db.Integer, nullable=False, default=0)
  posterior_mean = db.Column(db.Float, nullable=True)  # Rate as calculated by Bayesian analysis
  ci_lower_95 = db.Column(db.Float, nullable=True)     # Lower bound of 95% credible interval
  ci_upper_95 = db.Column(db.Float, nullable=True)     # Upper bound of 95% credible interval
  prob_vs_control = db.Column(db.Float, nullable=True) # Probability of being better than control
  
  # Relationships
  variant = db.relationship('Variant', back_populates='step_results')
  funnel_step = db.relationship('FunnelStep', back_populates='step_results')
  
  def __repr__(self):
    return f"<StepResult variant_id={self.variant_id} step_id={self.funnel_step_id} count={self.converted_count}>" 