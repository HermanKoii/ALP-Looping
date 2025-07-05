import os
import json
from typing import Any, Dict, Optional
from copy import deepcopy
from src.alp_config import AdaptiveLearningProcessConfig, validate_alp_config, LearningAlgorithm, LoggingLevel

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass

class ConfigurationManager:
    """
    Enhanced Configuration Manager that supports multiple configuration sources
    and integrates with the AdaptiveLearningProcessConfig model.
    
    Supports:
    - Default configuration
    - JSON file configuration
    - Environment variable configuration
    - Runtime configuration overrides
    """
    
    DEFAULT_CONFIG_PATH = 'config.json'
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the ConfigurationManager.
        
        Args:
            config_path (Optional[str]): Path to the configuration file. 
                                         Uses default path if not provided.
        """
        self._config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config = self._load_configuration()
    
    def _parse_env_value(self, field_name: str, value: str, default_value: Any) -> Any:
        """
        Parse environment variable value with validation.
        
        Args:
            field_name (str): Name of the configuration field
            value (str): Environment variable value
            default_value (Any): Default value for type inference
        
        Returns:
            Parsed and validated value
        
        Raises:
            ConfigurationError: If value cannot be parsed or validated
        """
        try:
            if field_name == 'custom_parameters':
                return json.loads(value)
            elif field_name == 'learning_algorithm':
                return LearningAlgorithm(value)
            elif field_name == 'logging_level':
                return LoggingLevel(value)
            elif isinstance(default_value, float):
                parsed_value = float(value)
                if parsed_value <= 0:
                    raise ValueError("Value must be positive")
                return parsed_value
            elif isinstance(default_value, int):
                parsed_value = int(value)
                if parsed_value <= 0:
                    raise ValueError("Value must be positive")
                return parsed_value
            else:
                return value
        except (ValueError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"Invalid environment variable {field_name}: {e}")
    
    def _load_configuration(self) -> AdaptiveLearningProcessConfig:
        """
        Load configuration from multiple sources with precedence.
        
        Precedence order:
        1. Configuration file
        2. Environment variables
        3. Default configuration
        
        Returns:
            AdaptiveLearningProcessConfig: Loaded and merged configuration
        """
        # Start with default configuration
        config = AdaptiveLearningProcessConfig()
        config_dict = config.model_dump()
        
        # Try loading from JSON file if path exists
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    file_config = json.load(f)
                    # Update config_dict with file_config, prioritizing file values
                    for key, value in file_config.items():
                        if value is not None:
                            config_dict[key] = value
            except (json.JSONDecodeError, IOError) as e:
                raise ConfigurationError(f"Error reading configuration file: {e}")
        
        # Override with environment variables
        for field_name, value in config_dict.items():
            env_var = f'ALP_{field_name.upper()}'
            env_value = os.environ.get(env_var)
            
            if env_value is not None:
                try:
                    config_dict[field_name] = self._parse_env_value(field_name, env_value, value)
                except ConfigurationError:
                    raise
        
        return validate_alp_config(config_dict)
    
    def get_config(self) -> AdaptiveLearningProcessConfig:
        """
        Get the current configuration.
        
        Returns:
            AdaptiveLearningProcessConfig: Current configuration
        """
        return deepcopy(self._config)
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration with provided parameters.
        
        Args:
            **kwargs: Configuration parameters to update
        
        Raises:
            ConfigurationError: If invalid configuration parameters are provided
        """
        try:
            # Create a copy of current config to update
            config_dict = self._config.model_dump()
            
            # Update with provided kwargs
            for key, value in kwargs.items():
                if value is not None:
                    config_dict[key] = value
            
            # Recreate configuration object
            self._config = validate_alp_config(config_dict)
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration update: {e}")
    
    def save_config(self, path: Optional[str] = None) -> None:
        """
        Save current configuration to a JSON file.
        
        Args:
            path (Optional[str]): Path to save configuration. 
                                  Uses default path if not provided.
        """
        save_path = path or self._config_path
        with open(save_path, 'w') as f:
            json.dump(self._config.model_dump(), f, indent=4)