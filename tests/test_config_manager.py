import os
import json
import pytest
from src.config.config_manager import ConfigurationManager, ConfigurationError
from src.alp_config import LearningAlgorithm, LoggingLevel

def test_default_configuration():
    """Test default configuration initialization."""
    config_manager = ConfigurationManager()
    config = config_manager.get_config()
    
    assert config.learning_algorithm == LearningAlgorithm.ADAM
    assert config.logging_level == LoggingLevel.INFO
    assert config.iteration_config.max_iterations == 1000
    assert config.hyperparameters.learning_rate == 0.01

def test_file_configuration(tmp_path):
    """Test loading configuration from a JSON file."""
    config_file = tmp_path / "config.json"
    test_config = {
        "learning_algorithm": "stochastic_gradient_descent",
        "logging_level": "DEBUG",
        "hyperparameters": {
            "learning_rate": 0.05,
            "batch_size": 64
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(test_config, f)
    
    config_manager = ConfigurationManager(str(config_file))
    config = config_manager.get_config()
    
    assert config.learning_algorithm == LearningAlgorithm.SGD
    assert config.logging_level == LoggingLevel.DEBUG
    assert config.hyperparameters.learning_rate == 0.05
    assert config.hyperparameters.batch_size == 64

def test_env_configuration(monkeypatch):
    """Test configuration from environment variables."""
    monkeypatch.setenv('ALP_LEARNING_ALGORITHM', 'gradient_descent')
    monkeypatch.setenv('ALP_LOGGING_LEVEL', 'WARNING')
    monkeypatch.setenv('ALP_CUSTOM_PARAMETERS', '{"key": "value"}')
    
    config_manager = ConfigurationManager()
    config = config_manager.get_config()
    
    assert config.learning_algorithm == LearningAlgorithm.GRADIENT_DESCENT
    assert config.logging_level == LoggingLevel.WARNING
    assert config.custom_parameters == {"key": "value"}

def test_configuration_update():
    """Test updating configuration at runtime."""
    config_manager = ConfigurationManager()
    
    config_manager.update_config(
        learning_algorithm=LearningAlgorithm.REINFORCEMENT,
        logging_level=LoggingLevel.ERROR
    )
    
    config = config_manager.get_config()
    
    assert config.learning_algorithm == LearningAlgorithm.REINFORCEMENT
    assert config.logging_level == LoggingLevel.ERROR

def test_save_and_load_configuration(tmp_path):
    """Test saving and loading configuration."""
    config_file = tmp_path / "saved_config.json"
    
    config_manager = ConfigurationManager()
    config_manager.update_config(
        learning_algorithm=LearningAlgorithm.SGD,
        hyperparameters={
            "learning_rate": 0.03,
            "batch_size": 128
        }
    )
    
    config_manager.save_config(str(config_file))
    
    # Load saved configuration
    loaded_config_manager = ConfigurationManager(str(config_file))
    loaded_config = loaded_config_manager.get_config()
    
    assert loaded_config.learning_algorithm == LearningAlgorithm.SGD
    assert loaded_config.hyperparameters.learning_rate == 0.03
    assert loaded_config.hyperparameters.batch_size == 128

def test_configuration_error_handling(tmp_path, monkeypatch):
    """Test error handling for invalid configurations."""
    # Invalid JSON file
    invalid_config_file = tmp_path / "invalid_config.json"
    with open(invalid_config_file, 'w') as f:
        f.write("{invalid json}")
    
    with pytest.raises(ConfigurationError, match="Error reading configuration file"):
        ConfigurationManager(str(invalid_config_file))
    
    # Invalid environment variable type for numeric fields
    monkeypatch.setenv('ALP_LEARNING_RATE', 'not a number')
    with pytest.raises(ConfigurationError, match="could not convert string to float"):
        # Temporarily remove existing ALP_LEARNING_RATE to prevent interference
        old_env_value = os.environ.pop('ALP_LEARNING_RATE', None)
        try:
            ConfigurationManager()
        finally:
            # Restore the environment variable if it existed
            if old_env_value is not None:
                os.environ['ALP_LEARNING_RATE'] = old_env_value

    # Invalid enum values
    monkeypatch.setenv('ALP_LEARNING_ALGORITHM', 'invalid_algorithm')
    with pytest.raises(ConfigurationError, match="is not a valid LearningAlgorithm"):
        # Temporarily remove existing ALP_LEARNING_ALGORITHM to prevent interference
        old_env_value = os.environ.pop('ALP_LEARNING_ALGORITHM', None)
        try:
            ConfigurationManager()
        finally:
            # Restore the environment variable if it existed
            if old_env_value is not None:
                os.environ['ALP_LEARNING_ALGORITHM'] = old_env_value