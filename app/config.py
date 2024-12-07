import os
import yaml
from notifications import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

DEFAULT_CONFIG = {
    "app": {
        "host": "0.0.0.0",
        "port": 5235,
        "debug": True
    },
    "email": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "simonaTest23@gmail.com",
        "app_password": "rqsj obct otjo vcsh",
        "recipient_email": "simonaettari@libero.it"
    },
    "storage": {
        "max_snapshots_per_volume": 3,
        "max_total_size_gb": 50,
    },
    "monitoring": {
        "interval_minutes": 2
    }
}

def load_config():
    
    # Load the configuration from the config.yaml file.
    # If the file does not exist or is empty, create a default configuration.
    
    try:
        if not os.path.exists(CONFIG_PATH) or os.stat(CONFIG_PATH).st_size == 0:
            logging.info("Config file not found or empty. Initializing with default configuration.")
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG

        with open(CONFIG_PATH, "r") as file:
            config = yaml.safe_load(file) or {}
        return config
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")

def save_config(new_config):
    
    # Save the updated configuration in the config.yaml file.
    
    try:
        with open(CONFIG_PATH, "w") as file:
            yaml.dump(new_config, file)
        logging.info("Configuration saved successfully.")
    except Exception as e:
        raise Exception(f"Error saving configuration: {e}")

def update_config(new_data):
    
    # Update the existing configuration with the data provided.
    
    try:
        # Load the actual configuration
        current_config = load_config()

        # Update existing sections or add new ones
        for section, values in new_data.items():
            if section in current_config and isinstance(current_config[section], dict):
                current_config[section].update(values)
            else:
                current_config[section] = values

        # Save the updated configuration
        save_config(current_config)
        return current_config
    except Exception as e:
        raise Exception(f"Error updating configuration: {e}")
