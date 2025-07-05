import pytest
from src.alp.termination_conditions import TerminationConditions, TerminationStatus


def test_initial_state():
    """Test the initial state of termination conditions."""
    conditions = TerminationConditions()
    assert conditions.current_iteration == 0
    assert conditions.best_performance == 0.0


def test_max_iterations_termination():
    """Test termination due to reaching maximum iterations."""
    conditions = TerminationConditions(max_iterations=3)
    
    # Run first iteration
    status = conditions.evaluate_termination(0.5)
    assert status == TerminationStatus.CONTINUE
    assert conditions.current_iteration == 1

    # Run second iteration
    status = conditions.evaluate_termination(0.6)
    assert status == TerminationStatus.CONTINUE
    assert conditions.current_iteration == 2

    # Run third iteration (should terminate)
    status = conditions.evaluate_termination(0.7)
    assert status == TerminationStatus.TERMINATE
    assert conditions.current_iteration == 3


def test_performance_threshold_termination():
    """Test termination due to reaching performance threshold."""
    conditions = TerminationConditions(performance_threshold=0.8)
    
    # Iterations below threshold
    status1 = conditions.evaluate_termination(0.5)
    assert status1 == TerminationStatus.CONTINUE

    status2 = conditions.evaluate_termination(0.7)
    assert status2 == TerminationStatus.CONTINUE

    # Iteration reaching threshold
    status3 = conditions.evaluate_termination(0.8)
    assert status3 == TerminationStatus.TERMINATE


def test_best_performance_tracking():
    """Test tracking of best performance."""
    conditions = TerminationConditions()
    
    conditions.evaluate_termination(0.5)
    assert conditions.best_performance == 0.5

    conditions.evaluate_termination(0.3)
    assert conditions.best_performance == 0.5

    conditions.evaluate_termination(0.7)
    assert conditions.best_performance == 0.7


def test_reset_method():
    """Test reset method for termination conditions."""
    conditions = TerminationConditions()
    
    # Run some iterations
    conditions.evaluate_termination(0.5)
    conditions.evaluate_termination(0.6)
    
    # Verify state
    assert conditions.current_iteration == 2
    assert conditions.best_performance == 0.6

    # Reset
    conditions.reset()
    
    # Check reset state
    assert conditions.current_iteration == 0
    assert conditions.best_performance == 0.0