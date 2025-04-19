import os
import json
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'default_config.json')

def load_config(config_path=None):
    """
    Load configuration from file

    Args:
        config_path (str, optional): Path to configuration file

    Returns:
        dict: Configuration dictionary
    """

    # Load default configuration
    try:
        with open(DEFAULT_CONFIG_PATH, "r") as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load default configuration: {str(e)}")
        config = {}

    # Load user configuration
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception as e:
            logger.error(f"Failed to load user configuration: {str(e)}")

    return config

def save_config(config, config_path):
    """
    Save configuration to file
    
    Args:
        config (dict): Configuration dictionary
        config_path (str): Path to save configuration

    Returns:
        bool: Success or failure
    """
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save configuration: {str(e)}")
        return False