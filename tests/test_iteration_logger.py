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