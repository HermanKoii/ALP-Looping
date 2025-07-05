import os
import json
import pytest
from typing import List, Dict, Any
from src.log_analysis.log_parser import LogParser

@pytest.fixture
def sample_log_data() -> List[Dict[str, Any]]:
    """Generate sample log data for testing."""
    return [
        {
            'timestamp': '2023-01-01T00:00:00',
            'iteration': 1,
            'performance_score': 0.75,
            'status': 'success'
        },
        {
            'timestamp': '2023-01-01T00:01:00',
            'iteration': 2,
            'performance_score': 0.85,
            'status': 'success'
        },
        {
            'timestamp': '2023-01-01T00:02:00',
            'iteration': 3,
            'performance_score': 0.5,
            'status': 'error'
        }
    ]

@pytest.fixture
def log_directory(tmp_path, sample_log_data):
    """Create a temporary log directory with sample log files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    
    # Create multiple log files
    for i in range(3):
        log_file = log_dir / f"log_{i}.json"
        with open(log_file, 'w') as f:
            json.dump(sample_log_data, f)
    
    return str(log_dir)

def test_log_parser_initialization(log_directory):
    """Test LogParser initialization."""
    parser = LogParser(log_directory)
    assert parser.log_directory == log_directory
    assert os.path.exists(log_directory)

def test_get_log_files(log_directory):
    """Test retrieving log files."""
    parser = LogParser(log_directory)
    log_files = parser.get_log_files()
    
    assert len(log_files) == 3
    assert all(f.endswith('.json') for f in log_files)

def test_parse_log_file(log_directory, sample_log_data):
    """Test parsing a single log file."""
    parser = LogParser(log_directory)
    log_files = parser.get_log_files()
    parsed_logs = parser.parse_log_file(log_files[0])
    
    assert parsed_logs == sample_log_data
    assert len(parsed_logs) == 3

def test_analyze_performance(log_directory, sample_log_data):
    """Test performance analysis of log entries."""
    parser = LogParser(log_directory)
    performance_metrics = parser.analyze_performance(sample_log_data)
    
    assert performance_metrics['total_iterations'] == 3
    assert performance_metrics['error_rate'] == pytest.approx(1/3)
    assert performance_metrics['avg_performance'] == pytest.approx(0.7)
    assert performance_metrics['max_performance'] == 0.85
    assert performance_metrics['min_performance'] == 0.5

def test_generate_report(log_directory):
    """Test generating a comprehensive log report."""
    parser = LogParser(log_directory)
    report = parser.generate_report()
    
    assert report['total_log_files'] == 3
    assert len(report['file_analyses']) == 3
    
    for file_analysis in report['file_analyses']:
        assert 'file_name' in file_analysis
        assert 'performance' in file_analysis

def test_invalid_log_file(tmp_path):
    """Test handling of invalid log files."""
    invalid_log_dir = tmp_path / "invalid_logs"
    invalid_log_dir.mkdir()
    
    # Create an invalid JSON file
    with open(invalid_log_dir / "invalid.json", 'w') as f:
        f.write("Not a valid JSON")
    
    parser = LogParser(str(invalid_log_dir))
    
    with pytest.raises(ValueError):
        parser.parse_log_file(str(invalid_log_dir / "invalid.json"))

def test_nonexistent_log_file():
    """Test handling of nonexistent log files."""
    parser = LogParser('/nonexistent/path')
    
    with pytest.raises(FileNotFoundError):
        parser.parse_log_file('/nonexistent/path/log.json')