from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum, auto


class TerminationStatus(Enum):
    """Enumeration representing the status of termination conditions."""
    CONTINUE = auto()
    TERMINATE = auto()


@dataclass
class TerminationConditions:
    """
    Configuration and evaluation class for learning process termination conditions.

    Manages and evaluates conditions that determine when a learning process should stop.
    Supports configurable maximum iterations and performance thresholds.

    Attributes:
        max_iterations (int): Maximum number of iterations allowed.
        performance_threshold (float): Minimum performance threshold for continuation.
        current_iteration (int): Current iteration count.
        best_performance (float): Best performance achieved so far.
    """
    max_iterations: int = 100
    performance_threshold: float = 0.95
    current_iteration: int = field(default=0)
    best_performance: float = field(default=0.0)

    def evaluate_termination(self, current_performance: float) -> TerminationStatus:
        """
        Evaluate whether the learning process should terminate.

        Args:
            current_performance (float): Current performance metric to evaluate.

        Returns:
            TerminationStatus: Indicates whether to continue or terminate the process.
        """
        # Update iteration count
        self.current_iteration += 1

        # Update best performance if current performance is better
        self.best_performance = max(self.best_performance, current_performance)

        # Check termination conditions
        if self.current_iteration >= self.max_iterations:
            return TerminationStatus.TERMINATE

        if current_performance >= self.performance_threshold:
            return TerminationStatus.TERMINATE

        return TerminationStatus.CONTINUE

    def reset(self):
        """
        Reset the termination condition tracking to initial state.
        """
        self.current_iteration = 0
        self.best_performance = 0.0