import os
import pytest
from src.iteration_state import (
    IterationState, 
    IterationStatus, 
    IterationStateManager
)
from datetime import datetime, timedelta


def test_iteration_state_creation():
    """Test basic iteration state creation and attributes."""
    state = IterationState(iteration_id='test_001')
    assert state.iteration_id == 'test_001'
    assert state.status == IterationStatus.PENDING


def test_iteration_state_marking():
    """Test marking iteration states."""
    state = IterationState(iteration_id='test_002')
    
    # Test marking as started
    state.mark_started()
    assert state.status == IterationStatus.RUNNING
    assert state.start_time is not None
    
    # Test marking as completed
    state.mark_completed()
    assert state.status == IterationStatus.COMPLETED
    assert state.end_time is not None


def test_iteration_state_error_handling():
    """Test handling of failed and interrupted states."""
    state = IterationState(iteration_id='test_003')
    
    # Test marking as failed
    state.mark_failed('Test error occurred')
    assert state.status == IterationStatus.FAILED
    assert state.error_details == 'Test error occurred'
    
    # Test marking as interrupted
    state = IterationState(iteration_id='test_004')
    state.mark_interrupted()
    assert state.status == IterationStatus.INTERRUPTED


def test_iteration_state_serialization():
    """Test state serialization and deserialization."""
    original_state = IterationState(iteration_id='test_005')
    original_state.configuration = {'learning_rate': 0.01}
    original_state.metrics = {'accuracy': 0.95}
    original_state.mark_started()
    
    # Convert to dict
    state_dict = original_state.to_dict()
    
    # Recreate from dict
    reconstructed_state = IterationState.from_dict(state_dict)
    
    assert reconstructed_state.iteration_id == original_state.iteration_id
    assert reconstructed_state.status == original_state.status
    assert reconstructed_state.configuration == original_state.configuration
    assert reconstructed_state.metrics == original_state.metrics


def test_iteration_state_manager():
    """Test IterationStateManager functionality."""
    temp_dir = 'test_iteration_states'
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        manager = IterationStateManager(state_dir=temp_dir)
        
        # Create and save a state
        state = IterationState(iteration_id='test_006')
        state.mark_started()
        state.metrics = {'loss': 0.1}
        manager.save_state(state)
        
        # Load the state
        loaded_state = manager.load_state('test_006')
        assert loaded_state is not None
        assert loaded_state.iteration_id == 'test_006'
        assert loaded_state.metrics == {'loss': 0.1}
        
        # Get states by status
        manager.save_state(IterationState(iteration_id='test_007'))
        failed_state = IterationState(iteration_id='test_008')
        failed_state.mark_failed('Test failure')
        manager.save_state(failed_state)
        
        pending_states = manager.get_states_by_status(IterationStatus.PENDING)
        failed_states = manager.get_states_by_status(IterationStatus.FAILED)
        
        assert len(pending_states) > 0
        assert len(failed_states) > 0
    
    finally:
        # Clean up test directory
        for filename in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, filename))
        os.rmdir(temp_dir)