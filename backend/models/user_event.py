"""
User Event model to track which users completed which funnel steps.
"""

from ..extensions import db

class UserEvent(db.Model):
    """
    Represents a user's interaction with a funnel step in an experiment.
    Each record indicates whether a user completed a particular step in the funnel.
    """
    __tablename__ = 'user_events'
    
    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('variants.id'), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)  # External user ID
    funnel_step_id = db.Column(db.Integer, db.ForeignKey('funnel_steps.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)  # Whether the user completed this step
    
    # Relationships
    variant = db.relationship('Variant', back_populates='user_events')
    funnel_step = db.relationship('FunnelStep', back_populates='user_events')
    
    def __repr__(self):
        return f"<UserEvent id={self.id}, user_id={self.user_id}, step_id={self.funnel_step_id}, completed={self.completed}>" 