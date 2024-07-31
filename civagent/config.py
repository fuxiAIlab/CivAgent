import os
import yaml
from civagent import logger

config_path = os.environ.get('CIVAGENT_CONFIG_PATH')


def load_config():
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data


config_data = load_config()
logger.info(f"Loaded config from {config_path}: {config_data}")