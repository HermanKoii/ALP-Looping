from typing import Dict, Any, Optional
from enum import Enum, auto
import logging
from src.iteration_state import IterationStatus  # Import unified enum

class IterationTracker:
    """
    A comprehensive iteration tracking mechanism for the Adaptive Learning Process.
    
    Manages iteration state, progression, and provides detailed tracking capabilities.
    
    Attributes:
        _current_iteration (int): Current iteration number
        _max_iterations (Optional[int]): Maximum number of iterations allowed
        _status (IterationStatus): Current status of the iteration process
        _metadata (Dict[str, Any]): Additional metadata for tracking
    """
    
    def __init__(self, max_iterations: Optional[int] = None):
        """
        Initialize the IterationTracker.
        
        Args:
            max_iterations (Optional[int], optional): Maximum number of iterations allowed. 
                Defaults to None (unlimited iterations).
        """
        self._current_iteration = 0
        self._max_iterations = max_iterations
        self._status = IterationStatus.INITIALIZED
        self._metadata: Dict[str, Any] = {}
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def start(self) -> None:
        """
        Start the iteration process, setting the initial state.
        
        Raises:
            RuntimeError: If iterations have already been started.
        """
        if self._status != IterationStatus.INITIALIZED:
            raise RuntimeError("Iteration process has already been started.")
        
        self._status = IterationStatus.IN_PROGRESS
        self._logger.info("Iteration process started.")
    
    def next_iteration(self) -> bool:
        """
        Advance to the next iteration.
        
        Returns:
            bool: True if iterations can continue, False otherwise.
        
        Raises:
            RuntimeError: If iteration process is not in progress.
        """
        if self._status != IterationStatus.IN_PROGRESS:
            raise RuntimeError("Iteration process is not in progress.")
        
        self._current_iteration += 1
        
        # Check iteration limit
        if (self._max_iterations is not None and 
            self._current_iteration >= self._max_iterations):
            self.complete()
            return False
        
        self._logger.info(f"Starting iteration {self._current_iteration}")
        return True
    
    def complete(self) -> None:
        """Mark the iteration process as completed."""
        self._status = IterationStatus.COMPLETED
        self._logger.info("Iteration process completed successfully.")
    
    def terminate(self, reason: Optional[str] = None) -> None:
        """
        Terminate the iteration process prematurely.
        
        Args:
            reason (Optional[str], optional): Reason for termination.
        """
        self._status = IterationStatus.TERMINATED
        self._logger.warning(f"Iteration process terminated. Reason: {reason}")
    
    def error(self, error_details: Optional[str] = None) -> None:
        """
        Mark the iteration process as encountering an error.
        
        Args:
            error_details (Optional[str], optional): Details of the error.
        """
        self._status = IterationStatus.ERROR
        self._logger.error(f"Iteration process encountered an error: {error_details}")
    
    @property
    def current_iteration(self) -> int:
        """
        Get the current iteration number.
        
        Returns:
            int: Current iteration number.
        """
        return self._current_iteration
    
    @property
    def status(self) -> IterationStatus:
        """
        Get the current iteration status.
        
        Returns:
            IterationStatus: Current status of the iteration process.
        """
        return self._status
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the iteration tracking.
        
        Args:
            key (str): Metadata key
            value (Any): Metadata value
        """
        self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """
        Retrieve metadata by key.
        
        Args:
            key (str): Metadata key
            default (Optional[Any], optional): Default value if key is not found
        
        Returns:
            Optional[Any]: Metadata value or default
        """
        return self._metadata.get(key, default)
    
    def is_iteration_allowed(self) -> bool:
        """
        Check if another iteration is allowed.
        
        Returns:
            bool: True if iteration can continue, False otherwise.
        """
        return (self._status == IterationStatus.IN_PROGRESS and 
                (self._max_iterations is None or 
                 self._current_iteration < self._max_iterations))