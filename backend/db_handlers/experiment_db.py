"""
Handles database operations related to experiments.
"""

from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db
from ..models.experiment import Experiment
from ..models.variant import Variant
from ..models.funnel_step import FunnelStep
from ..models.user_event import UserEvent

def create_experiment_record(experiment_name: str) -> int:
    """Create a new experiment record in the database."""
    experiment = Experiment(experiment_name=experiment_name)
    try:
        db.session.add(experiment)
        db.session.commit()
        return experiment.id
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error creating experiment: {e}")
        raise

def add_funnel_steps(experiment_id: int, step_names: List[str]) -> None:
    """Add funnel steps for an experiment."""
    try:
        # Add each funnel step
        for i, step_name in enumerate(step_names):
            funnel_step = FunnelStep(
                experiment_id=experiment_id,
                name=step_name,
                step_order=i + 1  # 1-based order
            )
            db.session.add(funnel_step)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error adding funnel steps: {e}")
        raise

def save_variant_data(
    experiment_id: int, 
    variant_name: str, 
    user_count: int, 
    variant_df: pd.DataFrame, 
    funnel_steps: List[str]
) -> None:
    """Save variant data including user events for funnel steps."""
    try:
        # Create variant record
        variant = Variant(
            experiment_id=experiment_id,
            variant_name=variant_name,
            user_count=user_count
        )
        db.session.add(variant)
        db.session.flush()  # Get the variant ID without committing
        
        # Get funnel step records for this experiment
        db_funnel_steps = FunnelStep.query.filter_by(experiment_id=experiment_id).all()
        step_id_map = {step.name: step.id for step in db_funnel_steps}
        
        # Process each user's funnel steps
        user_events = []
        for _, row in variant_df.iterrows():
            user_id = row['user_id']
            
            for step_name in funnel_steps:
                # Check if user completed this step (1 = completed, 0 = not completed)
                completed = int(row[step_name]) == 1
                
                if step_name in step_id_map:
                    user_event = UserEvent(
                        variant_id=variant.id,
                        user_id=str(user_id),
                        funnel_step_id=step_id_map[step_name],
                        completed=completed
                    )
                    user_events.append(user_event)
        
        # Bulk insert user events
        db.session.bulk_save_objects(user_events)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error saving variant data: {e}")
        raise

def get_experiment_with_variants(experiment_id: int) -> Optional[Tuple[Experiment, List[Variant], Dict[int, FunnelStep]]]:
    """Get experiment with its variants and funnel steps."""
    try:
        experiment = Experiment.query.get(experiment_id)
        if not experiment:
            return None
            
        variants = Variant.query.filter_by(experiment_id=experiment_id).all()
        funnel_steps = FunnelStep.query.filter_by(experiment_id=experiment_id).order_by(FunnelStep.step_order).all()
        
        # Create a map of funnel step ID to object for easy lookup
        funnel_steps_map = {step.id: step for step in funnel_steps}
        
        return experiment, variants, funnel_steps_map
    except SQLAlchemyError as e:
        print(f"Error retrieving experiment: {e}")
        raise

def get_experiment_name(experiment_id: int) -> str:
    """Get the name of an experiment."""
    experiment = Experiment.query.get(experiment_id)
    if experiment:
        return experiment.experiment_name
    return "Unknown Experiment"

def get_variant_results(experiment_id: int) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get conversion rates for each funnel step for all variants in an experiment.
    Returns a dictionary mapping variant names to lists of step results.
    """
    try:
        # Get all variants for the experiment
        variants = Variant.query.filter_by(experiment_id=experiment_id).all()
        if not variants:
            return {}
            
        # Get all funnel steps for the experiment, ordered by step_order
        funnel_steps = FunnelStep.query.filter_by(experiment_id=experiment_id).order_by(FunnelStep.step_order).all()
        if not funnel_steps:
            return {}
            
        results = {}
        
        for variant in variants:
            variant_results = []
            
            for step in funnel_steps:
                # Count users who completed this step for this variant
                completed_count = UserEvent.query.filter_by(
                    variant_id=variant.id,
                    funnel_step_id=step.id,
                    completed=True
                ).count()
                
                # Calculate conversion rate
                conversion_rate = completed_count / variant.user_count if variant.user_count > 0 else 0
                
                variant_results.append({
                    'step_name': step.name,
                    'completed_count': completed_count,
                    'conversion_rate': conversion_rate
                })
                
            results[variant.variant_name] = variant_results
            
        return results
    except SQLAlchemyError as e:
        print(f"Error getting variant results: {e}")
        raise

def save_experiment_results(data: Dict[str, Any]) -> int:
    """
    Save experiment results to the database.
    This is a placeholder for now.
    """
    # TODO: Implement proper saving logic once we have models defined
    # For now, just return a dummy experiment ID
    return 1

def create_variant_record(experiment_id: int, variant_name: str, user_count: int) -> int:
    """Create a new variant record in the database."""
    variant = Variant(
        experiment_id=experiment_id,
        variant_name=variant_name,
        user_count=user_count
    )
    try:
        db.session.add(variant)
        db.session.flush()  # Get the variant ID without committing
        return variant.id
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error creating variant record: {e}")
        raise

def get_or_create_funnel_step(experiment_id: int, step_name: str) -> int:
    """Get or create a funnel step for the given experiment."""
    try:
        # Check if step already exists
        step = FunnelStep.query.filter_by(
            experiment_id=experiment_id,
            name=step_name
        ).first()
        
        if step:
            return step.id
            
        # Get highest existing step order
        max_order = db.session.query(db.func.max(FunnelStep.step_order)).filter(
            FunnelStep.experiment_id == experiment_id
        ).scalar() or 0
        
        # Create new step with next order
        new_step = FunnelStep(
            experiment_id=experiment_id,
            name=step_name,
            step_order=max_order + 1
        )
        db.session.add(new_step)
        db.session.flush()
        return new_step.id
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error creating funnel step: {e}")
        raise

def save_conversion_data(variant_id: int, funnel_step_id: int, conversion_count: int, conversion_rate: float) -> None:
    """Save conversion data for a variant and funnel step."""
    try:
        # For this implementation, we'll create one UserEvent per conversion count
        # This is simplified - in a real app, you'd have events for each real user
        for i in range(conversion_count):
            user_event = UserEvent(
                variant_id=variant_id,
                user_id=f"synthetic_{variant_id}_{funnel_step_id}_{i}",
                funnel_step_id=funnel_step_id,
                completed=True
            )
            db.session.add(user_event)
        
        # Commit all changes
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error saving conversion data: {e}")
        raise 