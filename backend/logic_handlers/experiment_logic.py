"""
Handles the core business logic for processing and analyzing experiment data.
"""

import pandas as pd
from io import StringIO, BytesIO
from typing import Dict, Any, Tuple, List
from scipy.stats import beta
import numpy as np

# Import the DB handler
from backend.db_handlers.experiment_db import save_experiment_results, create_experiment_record, save_variant_data, get_experiment_with_variants, add_funnel_steps, get_experiment_name, get_variant_results

# Import the models
from backend.models.variant import Variant
from backend.models.funnel_step import FunnelStep

# Import the Bayesian logic
from backend.logic_handlers.bayesian_logic import calculate_bayesian_metrics


def _calculate_bayesian_metrics(conversions_a: int, trials_a: int, conversions_b: int, trials_b: int, num_samples: int = 20000) -> Dict[str, float]:
  """
  Performs Bayesian A/B test analysis using Beta-Binomial model.

  Calculates posterior distributions for A and B, and the probability that B is better than A.
  Also calculates the 95% credible interval for B's conversion rate.

  Args:
    conversions_a: Number of conversions for variant A (control).
    trials_a: Total number of trials (users) for variant A (control).
    conversions_b: Number of conversions for variant B (treatment).
    trials_b: Total number of trials (users) for variant B (treatment).
    num_samples: Number of samples to draw from posterior distributions.

  Returns:
    A dictionary containing:
      - posterior_mean_b: The mean of the posterior distribution for B.
      - ci_lower_95_b: The lower bound of the 95% credible interval for B.
      - ci_upper_95_b: The upper bound of the 95% credible interval for B.
      - prob_b_better_than_a: Probability that B's true rate is higher than A's.
  """
  # Parameters for the posterior Beta distributions (Beta(alpha, beta))
  # Using Beta(1, 1) prior (uniform)
  alpha_a, beta_a = 1 + conversions_a, 1 + (trials_a - conversions_a)
  alpha_b, beta_b = 1 + conversions_b, 1 + (trials_b - conversions_b)

  # Sample from the posterior distributions
  samples_a = beta.rvs(alpha_a, beta_a, size=num_samples)
  samples_b = beta.rvs(alpha_b, beta_b, size=num_samples)

  # Calculate probability B > A using numpy.mean and cast to float
  prob_b_better = float(np.mean(samples_b > samples_a))

  # Calculate posterior mean for B and cast to float
  posterior_mean_b = float(beta.mean(alpha_b, beta_b)) # type: ignore

  # Calculate 95% credible interval for B and cast to float
  ci_b = beta.interval(0.95, alpha_b, beta_b)
  ci_lower_b = float(ci_b[0]) # type: ignore
  ci_upper_b = float(ci_b[1]) # type: ignore

  # Return dictionary with float values
  return {
    'posterior_mean_b': posterior_mean_b,
    'ci_lower_95_b': ci_lower_b,
    'ci_upper_95_b': ci_upper_b,
    'prob_b_better_than_a': prob_b_better
  }

def _parse_csv_to_dataframe(file_stream: BytesIO) -> pd.DataFrame:
  """Reads the file stream and parses it into a pandas DataFrame."""
  try:
    csv_content = file_stream.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_content))
    # Basic validation
    required_columns = ["VARIATION_KEY", "Measure Names", "Measure Values"]
    if not all(col in df.columns for col in required_columns):
      raise ValueError(f"CSV must contain columns: {required_columns}")
    return df
  except pd.errors.EmptyDataError:
    raise ValueError("The uploaded CSV file is empty or invalid.")
  except Exception as e:
    raise ValueError(f"Failed to parse CSV content: {e}")

def _extract_experiment_structure(df: pd.DataFrame, control_key: str = 'off') -> Tuple[Dict[str, int], pd.DataFrame, List[str]]:
  """Extracts variant user counts, conversion pivot table, and step names from the DataFrame."""
  try:
    # 1. Get User Counts per Variant
    users_df = df[df["Measure Names"] == "Users"]
    if users_df.empty:
        raise ValueError("CSV does not contain 'Users' measure for variants.")
    users_df = users_df.astype({'Measure Values': int})
    variant_users = users_df.set_index("VARIATION_KEY")["Measure Values"].to_dict()
    if control_key not in variant_users:
        raise ValueError(f"Control key '{control_key}' not found in CSV variant users.")

    # 2. Get Funnel Steps and Conversion Counts
    conv_df = df[df["Measure Names"].str.startswith("Ct_", na=False)].copy()
    if conv_df.empty:
        raise ValueError("CSV does not contain any conversion step measures starting with 'Ct_'.")
    conv_df['Step Name'] = conv_df["Measure Names"].str.replace("Ct_", "", regex=False)
    conv_df = conv_df.astype({'Measure Values': int})
    conversion_pivot = pd.pivot_table(conv_df,
                                      values='Measure Values',
                                      index=['VARIATION_KEY'],
                                      columns=['Step Name'],
                                      fill_value=0)
    step_names = conv_df['Step Name'].unique().tolist()

    return variant_users, conversion_pivot, step_names
  except (KeyError, ValueError, TypeError) as e:
      # Catch specific parsing/conversion errors
      raise ValueError(f"Error extracting data structure from CSV: {e}")

def _perform_analysis(variant_users: Dict[str, int], conversion_pivot: pd.DataFrame, step_names: List[str], control_key: str = 'off') -> Dict[str, List[Dict[str, Any]]]:
    """Performs Bayesian analysis for each variant/step against the control."""
    analysis_results: Dict[str, List[Dict[str, Any]]] = {}
    
    if control_key not in variant_users or control_key not in conversion_pivot.index:
        raise ValueError("Control data is missing for analysis.")

    control_trials = variant_users[control_key]
    control_conversions = conversion_pivot.loc[control_key]

    for variant_key, variant_trials in variant_users.items():
        variant_analysis = []
        variant_conversions = conversion_pivot.loc[variant_key]

        for step in step_names:
            try:
                # Access step conversion using .loc, handle potential KeyError
                step_conversions_variant = int(variant_conversions.loc[step]) # type: ignore
            except KeyError:
                step_conversions_variant = 0 # Default to 0 if step not found

            metrics = None

            if variant_key != control_key:
                try:
                    # Access control conversion for the step using .loc
                    step_conversions_control = int(control_conversions.loc[step]) # type: ignore
                except KeyError:
                    step_conversions_control = 0 # Should ideally exist
                    print(f"Warning: Control conversion data missing for step: {step}")

                if control_trials > 0 and variant_trials > 0:
                    try:
                        metrics = _calculate_bayesian_metrics(
                            conversions_a=step_conversions_control,
                            trials_a=control_trials,
                            conversions_b=step_conversions_variant,
                            trials_b=variant_trials
                        )
                    except Exception as calc_e:
                        print(f"Error calculating metrics for {variant_key}/{step}: {calc_e}")
                else:
                    print(f"Skipping metrics for {variant_key}/{step} due to zero trials.")

            variant_analysis.append({
                'step_name': step,
                'converted_count': step_conversions_variant,
                'metrics': metrics
            })
        analysis_results[variant_key] = variant_analysis
    return analysis_results

def _structure_processed_data(original_filename: str, variant_users: Dict[str, int], analysis_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
  """Combines users counts and analysis results into the final structure for saving."""
  processed_data = {
    'original_filename': original_filename,
    'variants': []
  }
  for variant_key, user_count in variant_users.items():
      processed_data['variants'].append({
          'name': variant_key,
          'user_count': user_count,
          'results': analysis_results.get(variant_key, []) # Get results for this variant
      })
  return processed_data


# --- Main Public Function --- 
def process_and_analyze_experiment(file_stream: BytesIO, original_filename: str) -> Dict[str, Any]:
  """
  Orchestrates the reading, parsing, analysis, and saving of experiment data.

  Args:
    file_stream: The file stream object.
    original_filename: The original name of the uploaded file.

  Returns:
    A dictionary containing the ID of the saved experiment and a success message.
  Raises:
    ValueError: If CSV parsing or data extraction fails.
    Exception: For other processing or database errors.
  """
  try:
    # 1. Parse CSV to DataFrame
    df = _parse_csv_to_dataframe(file_stream)

    # 2. Extract structure (can be replaced for different CSV formats)
    control_key = 'off' # Define control key here or pass as arg
    variant_users, conversion_pivot, step_names = _extract_experiment_structure(df, control_key)

    # 3. Perform Bayesian Analysis (reusable core logic)
    analysis_results = _perform_analysis(variant_users, conversion_pivot, step_names, control_key)
    
    # 4. Structure data for saving
    processed_data = _structure_processed_data(original_filename, variant_users, analysis_results)

    # 5. Save to Database
    experiment_id = save_experiment_results(processed_data)

    # 6. Return success
    return {
        'experiment_id': experiment_id,
        'message': f'experiment_{experiment_id} processed and saved successfully.'
    }

  except ValueError as ve:
      # Catch specific parsing/extraction errors
      print(f"Data processing error for {original_filename}: {ve}")
      raise # Re-raise ValueError to be caught by API handler
  except Exception as e:
    # Catch unexpected errors during processing or saving
    print(f"Unexpected error processing file {original_filename}: {e}")
    raise Exception("An error occurred during experiment processing.")

def process_experiment_upload(file_path: str) -> Tuple[int, str]:
    """
    Process a CSV file containing experiment data and save it to the database.
    Returns the experiment ID and name.
    """
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(file_path)
        
        # Normalize column names (strip whitespace)
        df.columns = df.columns.str.strip()

        required_columns = ['experiment_name', 'variant', 'user_id']
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            raise ValueError(f"Missing required columns: {', '.join(missing)}")
            
        # Extract experiment name from the first row
        experiment_name = df['experiment_name'].iloc[0]
        
        # Create the experiment record
        experiment_id = create_experiment_record(experiment_name)
        
        # Process variants
        variants = df['variant'].unique()
        
        # Identify funnel steps (all columns except required ones)
        funnel_columns = [col for col in df.columns if col not in ['experiment_name', 'variant', 'user_id']]
        
        if not funnel_columns:
            raise ValueError("No funnel steps found in the CSV")
            
        # Add funnel steps to the database
        add_funnel_steps(experiment_id, funnel_columns)
        
        # Process each variant
        for variant_name in variants:
            variant_df = df[df['variant'] == variant_name]
            user_count = len(variant_df)
            
            # Save variant data to database
            save_variant_data(experiment_id, variant_name, user_count, variant_df, funnel_columns)
        
        # Calculate Bayesian metrics
        # This will be done when retrieving results to ensure all data is available
        
        return experiment_id, experiment_name
    
    except Exception as e:
        # Log the error in a real application
        print(f"Error processing experiment upload: {e}")
        raise

def get_experiment_results(experiment_id: str) -> Dict[str, Any]:
    """
    Retrieve the experiment results by ID.
    Returns formatted experiment data including variants and their metrics.
    """
    try:
        # Convert string ID to int
        experiment_id_int = int(experiment_id)
        
        # Get experiment data from database
        experiment_data = get_experiment_with_variants(experiment_id_int)
        if not experiment_data:
            return {}  # Return empty dict instead of None
            
        experiment, variants, funnel_steps_map = experiment_data
        
        # Get the experiment name
        experiment_name = get_experiment_name(experiment_id_int)
        
        # Find the control variant (assuming it's named 'control')
        control_variant = next((v for v in variants if v.variant_name.lower() == 'control'), None)
        if not control_variant:
            # If no variant is named 'control', use the first one
            control_variant = variants[0]
            
        # Get other variants
        other_variants = [v for v in variants if v.id != control_variant.id]
        
        # Get variant results including conversion rates for each funnel step
        variant_results = get_variant_results(experiment_id_int)
        
        # Calculate Bayesian metrics for each variant compared to control
        bayesian_results = {}
        for variant in other_variants:
            # Get control and variant conversion rates
            try:
                control_rates = [r['conversion_rate'] for r in variant_results.get(control_variant.variant_name, [])]
                variant_rates = [r['conversion_rate'] for r in variant_results.get(variant.variant_name, [])]
                
                # Calculate Bayesian metrics for the last funnel step
                if control_rates and variant_rates:
                    bayesian_metrics = calculate_bayesian_metrics(
                        control_rates[-1], 
                        variant_rates[-1],
                        control_variant.user_count,
                        variant.user_count
                    )
                    bayesian_results[variant.variant_name] = bayesian_metrics
            except Exception as e:
                print(f"Error calculating Bayesian metrics for {variant.variant_name}: {e}")
                # Continue with other variants if one fails
                continue
        
        # Format response data
        response = {
            "experiment_name": experiment_name,
            "control": format_variant_data(control_variant, variant_results),
            "variants": [format_variant_data(variant, variant_results) for variant in other_variants],
            "bayesian_results": bayesian_results
        }
        
        return response
    
    except ValueError:
        raise ValueError(f"Invalid experiment ID: {experiment_id}")
    except Exception as e:
        print(f"Error retrieving experiment results: {e}")
        raise

def format_variant_data(variant: Variant, variant_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """
    Format variant data for API response.
    """
    results = variant_results.get(variant.variant_name, [])
    
    funnel_steps = []
    for result in results:
        funnel_steps.append({
            "step_name": result['step_name'],
            "overall_conversion": result['conversion_rate']
        })
    
    return {
        "variant_name": variant.variant_name,
        "user_count": variant.user_count,
        "funnel_steps": funnel_steps,
        "relative_uplift": None  # This will be calculated in Bayesian results
    } 