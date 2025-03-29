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

  id = db.Column(db.Integer, primary_key=True) # Unique identifier for the step result record
  variant_id = db.Column(db.Integer, db.ForeignKey('variants.id'), nullable=False) # Foreign key linking to the variant this result belongs to
  funnel_step_id = db.Column(db.Integer, db.ForeignKey('funnel_steps.id'), nullable=False) # Foreign key linking to the funnel step this result corresponds to
  
  # Metrics
  converted_count = db.Column(db.Integer, nullable=False, default=0) # Number of users in the variant who completed this step
  posterior_mean = db.Column(db.Float, nullable=True)  # The mean conversion rate estimated by the Bayesian analysis
  ci_lower_95 = db.Column(db.Float, nullable=True)     # The lower bound of the 95% credible interval for the conversion rate
  ci_upper_95 = db.Column(db.Float, nullable=True)     # The upper bound of the 95% credible interval for the conversion rate
  prob_vs_control = db.Column(db.Float, nullable=True) # The calculated probability that this variant's true conversion rate is higher than the control variant's rate
  
  # Relationships
  variant = db.relationship('Variant', back_populates='step_results')
  funnel_step = db.relationship('FunnelStep', back_populates='step_results')
  
  def __repr__(self):
    return f"<StepResult variant_id={self.variant_id} step_id={self.funnel_step_id} count={self.converted_count}>" 