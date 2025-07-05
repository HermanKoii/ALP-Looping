import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json
import os


@dataclass
class IterationLogEntry:
    """
    Structured log entry for a single ALP iteration.
    
    Attributes:
        iteration_number (int): Unique identifier for the iteration
        timestamp (datetime): Timestamp of the iteration
        metadata (Dict[str, Any]): Additional metadata about the iteration
        performance_metrics (Dict[str, float]): Performance metrics for the iteration
        error_info (Optional[Dict[str, Any]]): Error information if an error occurred
        status (str): Status of the iteration (success, failure, warning)
    """
    iteration_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error_info: Optional[Dict[str, Any]] = None
    status: str = 'pending'

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert log entry to a dictionary for JSON serialization.
        
        Returns:
            Dict[str, Any]: Serializable dictionary representation of the log entry
        """
        entry_dict = asdict(self)
        entry_dict['timestamp'] = self.timestamp.isoformat()
        return entry_dict


class IterationLogger:
    """
    Utility class for managing and writing log entries for ALP iterations.
    
    Supports file-based and console logging with configurable log levels.
    """
    def __init__(
        self, 
        log_dir: str = 'logs', 
        log_file: str = 'iteration_log.json',
        console_log_level: int = logging.INFO
    ):
        """
        Initialize the IterationLogger.
        
        Args:
            log_dir (str): Directory to store log files
            log_file (str): Name of the log file
            console_log_level (int): Logging level for console output
        """
        self.log_dir = log_dir
        self.log_file = log_file
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Full path for log file
        self.log_path = os.path.join(log_dir, log_file)
        
        # Configure console logging
        logging.basicConfig(
            level=console_log_level,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def log_iteration(self, entry: IterationLogEntry) -> None:
        """
        Log an iteration entry to file and console.
        
        Args:
            entry (IterationLogEntry): Iteration log entry to record
        """
        try:
            # Log to console
            self._log_to_console(entry)
            
            # Append to JSON log file
            self._append_to_log_file(entry)
        except Exception as e:
            self.logger.error(f"Error logging iteration: {e}")

    def _log_to_console(self, entry: IterationLogEntry) -> None:
        """
        Log iteration details to console based on status.
        
        Args:
            entry (IterationLogEntry): Iteration log entry
        """
        log_method = {
            'success': self.logger.info,
            'failure': self.logger.error,
            'warning': self.logger.warning,
            'pending': self.logger.debug
        }.get(entry.status, self.logger.info)

        log_method(
            f"Iteration {entry.iteration_number} "
            f"Status: {entry.status} "
            f"Metrics: {entry.performance_metrics}"
        )

    def _append_to_log_file(self, entry: IterationLogEntry) -> None:
        """
        Append iteration log entry to JSON log file.
        
        Args:
            entry (IterationLogEntry): Iteration log entry
        """
        try:
            # Read existing log entries or initialize empty list
            log_entries = []
            if os.path.exists(self.log_path):
                with open(self.log_path, 'r') as f:
                    log_entries = json.load(f)

            # Append new entry
            log_entries.append(entry.to_dict())

            # Write updated log entries
            with open(self.log_path, 'w') as f:
                json.dump(log_entries, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to write log entry: {e}")

    def get_log_entries(self) -> list:
        """
        Retrieve all log entries from the log file.
        
        Returns:
            list: List of log entries
        """
        try:
            if os.path.exists(self.log_path):
                with open(self.log_path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Error reading log entries: {e}")
            return []