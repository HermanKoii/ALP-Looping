import pytest
from src.alp.iteration_tracker import IterationTracker, IterationStatus

def test_iteration_tracker_initialization():
    """Test basic initialization of IterationTracker."""
    tracker = IterationTracker()
    assert tracker.current_iteration == 0
    assert tracker.status == IterationStatus.INITIALIZED

def test_iteration_tracker_start():
    """Test starting the iteration process."""
    tracker = IterationTracker()
    tracker.start()
    assert tracker.status == IterationStatus.IN_PROGRESS

def test_iteration_tracker_next_iteration():
    """Test advancing to next iteration."""
    tracker = IterationTracker()
    tracker.start()
    assert tracker.next_iteration() is True
    assert tracker.current_iteration == 1

def test_iteration_tracker_max_iterations():
    """Test iteration limit."""
    tracker = IterationTracker(max_iterations=3)
    tracker.start()
    
    # Simulate iterations
    for _ in range(3):
        assert tracker.next_iteration() is True
    
    # Fourth iteration should return False
    assert tracker.next_iteration() is False
    assert tracker.status == IterationStatus.COMPLETED

def test_iteration_tracker_manual_complete():
    """Test manual completion of iterations."""
    tracker = IterationTracker()
    tracker.start()
    tracker.complete()
    assert tracker.status == IterationStatus.COMPLETED

def test_iteration_tracker_terminate():
    """Test termination of iterations."""
    tracker = IterationTracker()
    tracker.start()
    tracker.terminate(reason="Test termination")
    assert tracker.status == IterationStatus.TERMINATED

def test_iteration_tracker_error():
    """Test error handling in iterations."""
    tracker = IterationTracker()
    tracker.start()
    tracker.error(error_details="Test error")
    assert tracker.status == IterationStatus.ERROR

def test_iteration_tracker_metadata():
    """Test metadata management."""
    tracker = IterationTracker()
    tracker.add_metadata("test_key", "test_value")
    assert tracker.get_metadata("test_key") == "test_value"
    assert tracker.get_metadata("nonexistent_key") is None

def test_iteration_tracker_is_iteration_allowed():
    """Test iteration allowance checks."""
    tracker = IterationTracker(max_iterations=2)
    assert not tracker.is_iteration_allowed()  # Not started
    
    tracker.start()
    assert tracker.is_iteration_allowed()
    
    tracker.next_iteration()
    assert tracker.is_iteration_allowed()
    
    tracker.next_iteration()
    assert not tracker.is_iteration_allowed()  # Max iterations reached

def test_iteration_tracker_invalid_state_errors():
    """Test error handling for invalid state transitions."""
    tracker = IterationTracker()
    
    # Trying to get next iteration before start
    with pytest.raises(RuntimeError):
        tracker.next_iteration()
    
    # Start the tracker
    tracker.start()
    
    # Trying to start again
    with pytest.raises(RuntimeError):
        tracker.start()