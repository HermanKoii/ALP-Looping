from typing import List, Dict, Any
import json
import os
from datetime import datetime

class LogParser:
    """
    A class responsible for parsing and analyzing iteration logs.
    
    This class provides methods to:
    - Read log files
    - Parse log entries
    - Analyze performance metrics
    - Generate summary reports
    """
    
    def __init__(self, log_directory: str = 'logs'):
        """
        Initialize the LogParser with a specific log directory.
        
        Args:
            log_directory (str): Directory containing log files. Defaults to 'logs'.
        """
        self.log_directory = log_directory
        
        # Ensure log directory exists
        os.makedirs(log_directory, exist_ok=True)
    
    def get_log_files(self) -> List[str]:
        """
        Retrieve all log files in the specified directory.
        
        Returns:
            List[str]: List of log file paths
        """
        return [
            os.path.join(self.log_directory, f) 
            for f in os.listdir(self.log_directory) 
            if f.endswith('.json')
        ]
    
    def parse_log_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse a single log file and return its contents.
        
        Args:
            file_path (str): Path to the log file
        
        Returns:
            List[Dict[str, Any]]: Parsed log entries
        
        Raises:
            FileNotFoundError: If the log file doesn't exist
            json.JSONDecodeError: If the log file is not valid JSON
        """
        try:
            with open(file_path, 'r') as log_file:
                return json.load(log_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in log file: {file_path}")
    
    def analyze_performance(self, log_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze performance metrics from log entries.
        
        Args:
            log_entries (List[Dict[str, Any]]): List of log entries to analyze
        
        Returns:
            Dict[str, Any]: Performance summary metrics
        """
        if not log_entries:
            return {}
        
        # Extract performance-related metrics
        performance_metrics = {
            'total_iterations': len(log_entries),
            'start_time': log_entries[0].get('timestamp'),
            'end_time': log_entries[-1].get('timestamp'),
            'error_rate': sum(1 for entry in log_entries if entry.get('status') == 'error') / len(log_entries),
            'performance_scores': [entry.get('performance_score', 0) for entry in log_entries]
        }
        
        # Calculate additional metrics
        if performance_metrics['performance_scores']:
            performance_metrics.update({
                'avg_performance': sum(performance_metrics['performance_scores']) / len(performance_metrics['performance_scores']),
                'max_performance': max(performance_metrics['performance_scores']),
                'min_performance': min(performance_metrics['performance_scores'])
            })
        
        return performance_metrics
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report by analyzing all log files.
        
        Returns:
            Dict[str, Any]: Comprehensive log analysis report
        """
        log_files = self.get_log_files()
        report = {
            'total_log_files': len(log_files),
            'file_analyses': []
        }
        
        for log_file in log_files:
            try:
                log_entries = self.parse_log_file(log_file)
                file_report = {
                    'file_name': os.path.basename(log_file),
                    'performance': self.analyze_performance(log_entries)
                }
                report['file_analyses'].append(file_report)
            except Exception as e:
                report['file_analyses'].append({
                    'file_name': os.path.basename(log_file),
                    'error': str(e)
                })
        
        return report