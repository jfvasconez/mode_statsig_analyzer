"""
Defines the StepResult model, storing analysis results for each step/variant.
"""

from ..extensions import db


class StepResult(db.Model):
  """Model for storing raw counts and calculated Bayesian results per step/variant."""
  __tablename__ = 'step_results'

  id = db.Column(db.Integer, primary_key=True)

  # Foreign Keys
  variant_id = db.Column(db.Integer, db.ForeignKey('variants.id'), nullable=False)
  funnel_step_id = db.Column(db.Integer, db.ForeignKey('funnel_steps.id'), nullable=False)

  # Raw data from CSV
  converted_count = db.Column(db.Integer, nullable=False)

  # Calculated Bayesian Metrics
  # Using Float which is typically double precision in PostgreSQL
  posterior_mean = db.Column(db.Float, nullable=True)
  ci_lower_95 = db.Column(db.Float, nullable=True) # Lower bound of 95% Credible Interval
  ci_upper_95 = db.Column(db.Float, nullable=True) # Upper bound of 95% Credible Interval
  prob_vs_control = db.Column(db.Float, nullable=True) # Probability of being better than control

  # Add unique constraint to prevent duplicate entries for the same variant/step combination within an experiment
  # Note: This requires accessing the experiment_id through the relationships.
  # A simpler way is often to handle this constraint at the application logic level before insertion.
  # For now, we'll rely on application logic to prevent duplicates.
  # __table_args__ = (db.UniqueConstraint('variant_id', 'funnel_step_id', name='_variant_step_uc'),)

  def __repr__(self) -> str:
    return f'<StepResult {self.id} - Var:{self.variant_id} Step:{self.funnel_step_id} - Conv:{self.converted_count}>' 