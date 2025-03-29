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
from ..models.step_result import StepResult
from ..models.user_event import UserEvent
import logging

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
    Get conversion rates and analysis metrics for each funnel step for all variants.
    Queries the StepResult table for the data.
    Returns a dictionary mapping variant names to lists of step results.
    """
    logging.info(f"get_variant_results called for experiment_id: {experiment_id}")
    try:
        # Get all variants for the experiment
        variants = Variant.query.filter_by(experiment_id=experiment_id).all()
        if not variants:
            logging.warning(f"No variants found for experiment_id: {experiment_id}")
            return {}
            
        # Get all funnel steps for the experiment, ordered by step_order
        funnel_steps = FunnelStep.query.filter_by(experiment_id=experiment_id).order_by(FunnelStep.step_order).all()
        if not funnel_steps:
            logging.warning(f"No funnel steps found for experiment_id: {experiment_id}")
            return {}
            
        # Fetch all StepResult records for this experiment for efficiency
        all_step_results = StepResult.query.join(Variant).filter(Variant.experiment_id == experiment_id).all()
        
        # Organize StepResult records by variant_id and then funnel_step_id for quick lookup
        results_map: Dict[int, Dict[int, StepResult]] = {}
        for sr in all_step_results:
            if sr.variant_id not in results_map:
                results_map[sr.variant_id] = {}
            results_map[sr.variant_id][sr.funnel_step_id] = sr
            
        logging.info(f"Fetched and mapped {len(all_step_results)} StepResult records.")

        final_results = {}
        for variant in variants:
            logging.info(f"Processing variant: {variant.variant_name} (ID: {variant.id})")
            variant_step_data = []
            variant_results_map = results_map.get(variant.id, {}) # Get results for this specific variant
            
            for step in funnel_steps:
                step_result = variant_results_map.get(step.id) # Find the StepResult for this variant/step
                
                if step_result:
                    # Data found in StepResult table
                    completed_count = step_result.converted_count
                    conversion_rate = completed_count / variant.user_count if variant.user_count > 0 else 0
                    logging.debug(f"  Step: {step.name} (ID: {step.id}), Found StepResult: {step_result}")
                    variant_step_data.append({
                        'step_name': step.name,
                        'completed_count': completed_count,
                        'conversion_rate': conversion_rate,
                        # Include other metrics from StepResult
                        'posterior_mean': step_result.posterior_mean,
                        'ci_lower_95': step_result.ci_lower_95,
                        'ci_upper_95': step_result.ci_upper_95,
                        'prob_vs_control': step_result.prob_vs_control
                    })
                else:
                    # No StepResult found for this variant/step (shouldn't normally happen if saving worked)
                    logging.warning(f"  Step: {step.name} (ID: {step.id}), No StepResult found for variant {variant.id}. Defaulting to 0.")
                    variant_step_data.append({
                        'step_name': step.name,
                        'completed_count': 0,
                        'conversion_rate': 0,
                        'posterior_mean': None,
                        'ci_lower_95': None,
                        'ci_upper_95': None,
                        'prob_vs_control': None
                    })
                    
            final_results[variant.variant_name] = variant_step_data
            
        logging.info(f"Finished processing results for experiment {experiment_id}: {final_results}")
        return final_results
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_variant_results for experiment {experiment_id}: {e}", exc_info=True)
        print(f"Error getting variant results: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in get_variant_results for experiment {experiment_id}: {e}", exc_info=True)
        raise # Re-raise other exceptions

def save_experiment_results(data: Dict[str, Any]) -> int:
    """
    Save experiment results derived from the analysis to the database.
    Processes the structured data and saves Experiment, Variant, FunnelStep,
    and StepResult records (including Bayesian metrics).
    """
    logging.info(f"save_experiment_results called with data: {data}")
    session = db.session
    try:
        # 1. Create Experiment record
        original_filename = data.get('original_filename', 'Unknown Experiment')
        experiment = Experiment(experiment_name=original_filename)
        session.add(experiment)
        session.flush() # Assigns ID to experiment object
        experiment_id = experiment.id
        logging.info(f"Created experiment record with ID: {experiment_id}")

        if not experiment_id:
            raise ValueError("Failed to create experiment record, ID is missing.")

        # 2. Process Variants and Funnel Steps
        variants_data = data.get('variants', [])
        if not variants_data:
            logging.warning("No variant data found in the processed data.")
            session.commit()
            return experiment_id

        # Collect unique step names and create FunnelStep records
        funnel_step_names_set = set()
        for variant_info in variants_data:
            results_list = variant_info.get('results', []) # Renamed from 'results' to avoid confusion
            for result_item in results_list:
                funnel_step_names_set.add(result_item['step_name'])
        
        funnel_step_names_list = sorted(list(funnel_step_names_set))
        logging.info(f"Found unique funnel steps: {funnel_step_names_list}")

        funnel_step_map = {}
        for i, step_name in enumerate(funnel_step_names_list):
            funnel_step = FunnelStep(
                experiment_id=experiment_id,
                name=step_name,
                step_order=i + 1
            )
            session.add(funnel_step)
            session.flush()
            funnel_step_map[step_name] = funnel_step.id
        logging.info(f"Created funnel step records: {funnel_step_map}")

        # 3. Create Variant records and StepResult records
        for variant_info in variants_data:
            variant_name = variant_info.get('name', 'Unknown Variant')
            user_count = variant_info.get('user_count', 0)
            
            variant = Variant(
                experiment_id=experiment_id,
                variant_name=variant_name,
                user_count=user_count
                # No JSON field anymore
            )
            session.add(variant)
            session.flush() # Assigns ID to variant object
            variant_id = variant.id
            logging.info(f"Created variant record: name={variant_name}, id={variant_id}, users={user_count}")

            if not variant_id:
                 logging.error(f"Failed to get ID for variant: {variant_name}")
                 continue

            # Create StepResult record for each step in this variant's analysis results
            results_list = variant_info.get('results', [])
            for result_item in results_list:
                step_name = result_item['step_name']
                funnel_step_id = funnel_step_map.get(step_name)
                
                if funnel_step_id is None:
                    logging.warning(f"Could not find funnel step ID for step: {step_name} in variant {variant_name} when creating StepResult.")
                    continue

                # Extract metrics (handle potential None values)
                metrics = result_item.get('metrics') or {}
                converted_count = result_item.get('converted_count', 0)
                posterior_mean = metrics.get('posterior_mean_b')
                ci_lower = metrics.get('ci_lower_95_b')
                ci_upper = metrics.get('ci_upper_95_b')
                prob_vs_control = metrics.get('prob_b_better_than_a')
                
                step_result = StepResult(
                    variant_id=variant_id,
                    funnel_step_id=funnel_step_id,
                    converted_count=converted_count,
                    posterior_mean=posterior_mean,
                    ci_lower_95=ci_lower,
                    ci_upper_95=ci_upper,
                    prob_vs_control=prob_vs_control
                )
                session.add(step_result)
                logging.debug(f"Prepared StepResult for V:{variant_id}, S:{funnel_step_id}, Data:{step_result}")

        # 4. Commit the transaction
        session.commit()
        logging.info(f"Transaction committed successfully for experiment ID: {experiment_id}")
        return experiment_id

    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Database error in save_experiment_results: {e}", exc_info=True)
        raise Exception(f"Failed to save experiment results to database: {e}")
    except Exception as e:
        session.rollback()
        logging.error(f"Unexpected error in save_experiment_results: {e}", exc_info=True)
        raise Exception(f"An unexpected error occurred while saving experiment results: {e}")

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