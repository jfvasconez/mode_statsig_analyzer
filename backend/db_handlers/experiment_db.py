"""
Handles database operations related to experiments.
"""

from typing import Dict, Any, List, Tuple
# Import Session and scoped_session for type hinting
from sqlalchemy.orm import Session, scoped_session

from ..extensions import db
# Import models needed for saving
from ..models import Experiment, Variant, FunnelStep, StepResult


def _create_experiment_record(session: scoped_session, original_filename: str | None) -> Experiment:
    """Creates and flushes a new Experiment record."""
    new_experiment = Experiment(original_filename=original_filename)
    session.add(new_experiment)
    session.flush() # Flush to get ID
    return new_experiment

def _create_variant_records(session: scoped_session, variants_data: List[Dict[str, Any]], experiment_id: int) -> Dict[str, Variant]:
    """Creates and flushes Variant records for an experiment."""
    variant_map = {}
    for variant_data in variants_data:
        new_variant = Variant(
            name=variant_data['name'],
            user_count=variant_data['user_count'],
            experiment_id=experiment_id
        )
        session.add(new_variant)
        session.flush()
        variant_map[variant_data['name']] = new_variant
    return variant_map

def _create_step_and_result_records(session: scoped_session, variants_data: List[Dict[str, Any]], variant_map: Dict[str, Variant], experiment_id: int):
    """Creates FunnelStep (if needed) and StepResult records."""
    step_map: Dict[str, FunnelStep] = {}
    for variant_data in variants_data:
        variant_name = variant_data['name']
        new_variant = variant_map[variant_name]

        for result_data in variant_data.get('results', []):
            step_name = result_data['step_name']

            # Find or Create FunnelStep
            if step_name not in step_map:
                # Check if step already exists for this experiment (scoped session query)
                existing_step = session.query(FunnelStep).filter_by(experiment_id=experiment_id, name=step_name).first()
                if existing_step:
                    step_map[step_name] = existing_step
                    new_step = existing_step
                else:
                    new_step = FunnelStep(name=step_name, experiment_id=experiment_id)
                    session.add(new_step)
                    session.flush()
                    step_map[step_name] = new_step
            else:
                new_step = step_map[step_name]

            # Create StepResult
            metrics = result_data.get('metrics')
            new_step_result = StepResult(
                variant_id=new_variant.id,
                funnel_step_id=new_step.id,
                converted_count=result_data['converted_count'],
                posterior_mean=metrics.get('posterior_mean_b') if metrics else None,
                ci_lower_95=metrics.get('ci_lower_95_b') if metrics else None,
                ci_upper_95=metrics.get('ci_upper_95_b') if metrics else None,
                prob_vs_control=metrics.get('prob_b_better_than_a') if metrics else None
            )
            session.add(new_step_result)


# --- Main Public Function --- 
def save_experiment_results(processed_data: Dict[str, Any]) -> int:
  """
  Saves the processed experiment data and analysis results to the database
  by orchestrating calls to helper functions within a single transaction.

  Args:
    processed_data: The structured data from the logic handler.

  Returns:
    The ID of the newly created Experiment record.

  Raises:
    Exception: If there is an error during the database transaction.
  """
  session = db.session
  try:
    # 1. Create Experiment
    new_experiment = _create_experiment_record(
        session,
        processed_data.get('original_filename')
    )
    experiment_id = new_experiment.id
    variants_data = processed_data.get('variants', [])

    # 2. Create Variants
    variant_map = _create_variant_records(session, variants_data, experiment_id)

    # 3. Create Steps and Results
    _create_step_and_result_records(session, variants_data, variant_map, experiment_id)

    # 4. Commit transaction
    session.commit()
    print(f"Successfully saved Experiment {experiment_id}")
    return experiment_id

  except Exception as e:
    session.rollback() # Roll back the transaction in case of error
    print(f"Database error saving experiment: {e}")
    # Log the error properly in a real application
    raise Exception("Failed to save experiment results to the database.") 