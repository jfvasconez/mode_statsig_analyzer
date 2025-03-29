"""
Implements Bayesian analysis for experiment results.
"""

from typing import Dict, Tuple, List, Any
import numpy as np
from scipy import stats

def calculate_bayesian_metrics(
    control_conversion_rate: float,
    variant_conversion_rate: float,
    control_sample_size: int,
    variant_sample_size: int,
    simulations: int = 10000
) -> Dict[str, Any]:
    """
    Calculate Bayesian metrics for A/B test analysis.
    
    Args:
        control_conversion_rate: Conversion rate for the control group
        variant_conversion_rate: Conversion rate for the variant group
        control_sample_size: Number of users in the control group
        variant_sample_size: Number of users in the variant group
        simulations: Number of Monte Carlo simulations to run
        
    Returns:
        Dict containing:
            - chance_to_beat_control: Probability that variant beats control
            - relative_uplift: Relative uplift (percentage improvement)
            - credible_interval: 95% credible interval for the uplift
    """
    # Ensure we don't have zero values
    if control_sample_size == 0 or variant_sample_size == 0:
        return {
            "chance_to_beat_control": 0.5,
            "relative_uplift": 0.0,
            "credible_interval": [0.0, 0.0]
        }
    
    # Convert rates to counts
    control_conversions = round(control_conversion_rate * control_sample_size)
    variant_conversions = round(variant_conversion_rate * variant_sample_size)
    
    # Set up beta distributions with Bayesian priors
    # Using Beta(1, 1) = Uniform(0, 1) as a non-informative prior
    a_control = control_conversions + 1  # Beta prior alpha parameter
    b_control = control_sample_size - control_conversions + 1  # Beta prior beta parameter
    
    a_variant = variant_conversions + 1
    b_variant = variant_sample_size - variant_conversions + 1
    
    # Generate samples from the posterior distributions
    control_samples = np.random.beta(a_control, b_control, simulations)
    variant_samples = np.random.beta(a_variant, b_variant, simulations)
    
    # Calculate probability that variant beats control
    chance_to_beat_control = np.mean(variant_samples > control_samples)
    
    # Calculate relative uplift
    rel_uplift_samples = (variant_samples - control_samples) / control_samples
    relative_uplift = np.mean(rel_uplift_samples)
    
    # Calculate credible interval
    lower_bound, upper_bound = np.percentile(rel_uplift_samples, [2.5, 97.5])
    
    return {
        "chance_to_beat_control": float(chance_to_beat_control),
        "relative_uplift": float(relative_uplift),
        "credible_interval": [float(lower_bound), float(upper_bound)]
    } 