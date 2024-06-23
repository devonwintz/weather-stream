import os
import json
import logging

logger = logging.getLogger(__name__)


def load_json_file(file_path):
    """Load JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded JSON data from {file_path}.")
        return data
    except FileNotFoundError:
        logger.error(f"Error: The file '{file_path}' does not exist.")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error: Failed to decode JSON in '{file_path}'.")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

required_env_vars = [
    'KAFKA_TOPIC',
    'KAFKA_HOST',
    'AUTO_OFFSET_RESET',
    'DETAILED_SUMMARY',
    'FETCH_INTERVAL_SECONDS'
]

def check_required_env_vars():
    for var in required_env_vars:
        if var not in os.environ:
            logger.error(f"Missing required environment variable: {var}")
            raise EnvironmentError(f"Missing required environment variable: {var}")