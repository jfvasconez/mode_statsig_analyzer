"""
Models package for the application.
"""

# Import all models here for easy access
from .experiment import Experiment
from .variant import Variant
from .funnel_step import FunnelStep
from .user_event import UserEvent
from .step_result import StepResult

# You can optionally define __all__ to control `from .models import *` behavior
__all__ = ['Experiment', 'Variant', 'FunnelStep', 'StepResult']
