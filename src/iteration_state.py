from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional, List
import json
import os
import logging


class IterationStatus(Enum):
    """
    Comprehensive enumeration of iteration statuses across the system.
    
    Combines statuses from different iteration tracking mechanisms.
    """
    # Initial and Pending States
    INITIALIZED = auto()  # From tracker
    PENDING = auto()      # From state
    
    # Active States
    IN_PROGRESS = auto()  # From tracker 
    RUNNING = auto()      # From state
    
    # Terminal States
    COMPLETED = auto()    # Common to both
    TERMINATED = auto()   # From tracker
    INTERRUPTED = auto()  # From state
    
    # Error States
    ERROR = auto()        # From tracker
    FAILED = auto()       # From state


@dataclass
class IterationState:
    """
    Represents the state of a single learning iteration.

    Provides comprehensive tracking of iteration details, including
    configuration, performance metrics, status, and context.
    """
    iteration_id: str
    status: IterationStatus = IterationStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    configuration: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_details: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def mark_started(self) -> None:
        """
        Mark the iteration as started and record the start time.
        """
        self.status = IterationStatus.RUNNING
        self.start_time = datetime.now()

    def mark_completed(self) -> None:
        """
        Mark the iteration as completed and record the end time.
        """
        self.status = IterationStatus.COMPLETED
        self.end_time = datetime.now()

    def mark_failed(self, error_message: str) -> None:
        """
        Mark the iteration as failed and store error details.

        Args:
            error_message: Description of the failure
        """
        self.status = IterationStatus.FAILED
        self.end_time = datetime.now()
        self.error_details = error_message

    def mark_interrupted(self) -> None:
        """
        Mark the iteration as interrupted.
        """
        self.status = IterationStatus.INTERRUPTED
        self.end_time = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the iteration state to a dictionary representation.

        Returns:
            Dict representation of the iteration state
        """
        return {
            'iteration_id': self.iteration_id,
            'status': self.status.name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'configuration': self.configuration,
            'metrics': self.metrics,
            'error_details': self.error_details,
            'context': self.context
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IterationState:
        """
        Create an IterationState instance from a dictionary.

        Args:
            data: Dictionary containing iteration state data

        Returns:
            Reconstructed IterationState
        """
        state = cls(iteration_id=data['iteration_id'])
        state.status = IterationStatus[data['status']]
        state.start_time = datetime.fromisoformat(data['start_time']) if data['start_time'] else None
        state.end_time = datetime.fromisoformat(data['end_time']) if data['end_time'] else None
        state.configuration = data['configuration']
        state.metrics = data['metrics']
        state.error_details = data['error_details']
        state.context = data['context']
        return state


class IterationStateManager:
    """
    Manages the storage, retrieval, and tracking of iteration states.
    """
    def __init__(self, state_dir: str = 'iteration_states'):
        """
        Initialize the IterationStateManager.

        Args:
            state_dir: Directory to store iteration states
        """
        self.state_dir = state_dir
        os.makedirs(state_dir, exist_ok=True)

    def save_state(self, iteration_state: IterationState) -> None:
        """
        Save an iteration state to a JSON file.

        Args:
            iteration_state: State to save
        """
        state_file = os.path.join(self.state_dir, f'{iteration_state.iteration_id}.json')
        with open(state_file, 'w') as f:
            json.dump(iteration_state.to_dict(), f, indent=2)

    def load_state(self, iteration_id: str) -> Optional[IterationState]:
        """
        Load an iteration state from a file.

        Args:
            iteration_id: ID of the iteration to load

        Returns:
            Loaded IterationState or None if not found
        """
        state_file = os.path.join(self.state_dir, f'{iteration_id}.json')
        try:
            with open(state_file, 'r') as f:
                state_data = json.load(f)
                return IterationState.from_dict(state_data)
        except FileNotFoundError:
            return None

    def get_states_by_status(self, status: IterationStatus) -> List[IterationState]:
        """
        Retrieve all iteration states with a specific status.

        Args:
            status: Status to filter by

        Returns:
            List of matching IterationState instances
        """
        states = []
        for filename in os.listdir(self.state_dir):
            if filename.endswith('.json'):
                state_path = os.path.join(self.state_dir, filename)
                with open(state_path, 'r') as f:
                    state_data = json.load(f)
                    if IterationStatus[state_data['status']] == status:
                        states.append(IterationState.from_dict(state_data))
        return states