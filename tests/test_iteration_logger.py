import os
import json
import pytest
import logging
from datetime import datetime
from src.iteration_logger import IterationLogger, IterationLogEntry


@pytest.fixture
def iteration_logger(tmp_path):
    """Create a temporary IterationLogger for testing."""
    log_dir = str(tmp_path)
    return IterationLogger(log_dir=log_dir)


def test_iteration_log_entry_creation():
    """Test creating an IterationLogEntry."""
    entry = IterationLogEntry(
        iteration_number=1,
        metadata={'model': 'test_model'},
        performance_metrics={'accuracy': 0.95}
    )
    
    assert entry.iteration_number == 1
    assert entry.metadata == {'model': 'test_model'}
    assert entry.performance_metrics == {'accuracy': 0.95}
    assert isinstance(entry.timestamp, datetime)


def test_log_iteration(iteration_logger, caplog):
    """Test logging an iteration entry."""
    caplog.set_level(logging.INFO)
    
    entry = IterationLogEntry(
        iteration_number=1,
        status='success',
        performance_metrics={'accuracy': 0.95}
    )
    
    iteration_logger.log_iteration(entry)
    
    # Check console log
    assert 'Iteration 1 Status: success' in caplog.text
    
    # Check log file
    log_entries = iteration_logger.get_log_entries()
    assert len(log_entries) == 1
    assert log_entries[0]['iteration_number'] == 1
    assert log_entries[0]['status'] == 'success'


def test_log_multiple_iterations(iteration_logger):
    """Test logging multiple iterations."""
    for i in range(3):
        entry = IterationLogEntry(
            iteration_number=i,
            status='success',
            performance_metrics={'accuracy': 0.9 + 0.01 * i}
        )
        iteration_logger.log_iteration(entry)
    
    log_entries = iteration_logger.get_log_entries()
    assert len(log_entries) == 3
    
    # Verify log entries
    for i, entry in enumerate(log_entries):
        assert entry['iteration_number'] == i
        assert entry['status'] == 'success'


def test_log_iteration_with_error(iteration_logger):
    """Test logging an iteration with error information."""
    entry = IterationLogEntry(
        iteration_number=1,
        status='failure',
        error_info={'type': 'ValueError', 'message': 'Test error'}
    )
    
    iteration_logger.log_iteration(entry)
    
    log_entries = iteration_logger.get_log_entries()
    assert len(log_entries) == 1
    assert log_entries[0]['error_info'] == {'type': 'ValueError', 'message': 'Test error'}


def test_log_entries_serialization(iteration_logger):
    """Test JSON serialization of log entries."""
    entry = IterationLogEntry(
        iteration_number=1,
        metadata={'key': 'value'},
        performance_metrics={'accuracy': 0.95}
    )
    
    iteration_logger.log_iteration(entry)
    
    log_entries = iteration_logger.get_log_entries()
    log_entry = log_entries[0]
    
    # Verify timestamp is serialized
    assert 'timestamp' in log_entry
    assert isinstance(log_entry['timestamp'], str)
    
    # Verify other fields
    assert log_entry['iteration_number'] == 1
    assert log_entry['metadata'] == {'key': 'value'}
    assert log_entry['performance_metrics'] == {'accuracy': 0.95}


def test_filter_log_entries(iteration_logger):
    """Test filtering log entries."""
    # Log multiple entries with different statuses and iteration numbers
    entries = [
        IterationLogEntry(iteration_number=1, status='success', performance_metrics={'accuracy': 0.9}),
        IterationLogEntry(iteration_number=2, status='failure', performance_metrics={'accuracy': 0.7}),
        IterationLogEntry(iteration_number=3, status='success', performance_metrics={'accuracy': 0.95}),
    ]
    
    for entry in entries:
        iteration_logger.log_iteration(entry)
    
    # Test filtering by status
    success_entries = iteration_logger.filter_log_entries(status='success')
    assert len(success_entries) == 2
    assert all(entry['status'] == 'success' for entry in success_entries)
    
    # Test filtering by minimum iteration
    min_iteration_entries = iteration_logger.filter_log_entries(min_iteration=2)
    assert len(min_iteration_entries) == 2
    assert all(entry['iteration_number'] >= 2 for entry in min_iteration_entries)
    
    # Test combined filtering
    combined_filter = iteration_logger.filter_log_entries(status='success', min_iteration=2)
    assert len(combined_filter) == 1
    assert combined_filter[0]['iteration_number'] == 3
    assert combined_filter[0]['status'] == 'success'