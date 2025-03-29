"""
Handles the core business logic for processing and analyzing experiment data.
"""

import pandas as pd
from io import StringIO, BytesIO
from typing import Dict, Any, Tuple, List
from scipy.stats import beta
import numpy as np

# Import the DB handler
from ..db_handlers.experiment_db import save_experiment_results


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