"""
Initialize the models package.
Imports models to make them accessible via the package.
"""

from .experiment import Experiment
from .variant import Variant
from .funnel_step import FunnelStep
from .step_result import StepResult

# You can optionally define __all__ to control `from .models import *` behavior
__all__ = ['Experiment', 'Variant', 'FunnelStep', 'StepResult']
