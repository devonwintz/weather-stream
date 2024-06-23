import os
import json
import logging

logger = logging.getLogger(__name__)

required_env_vars = [
    'CITY',
    'API_URL',
    'FETCH_INTERVAL_SECONDS',
    'KAFKA_TOPIC',
    'KAFKA_HOST',
    'KAFKA_MAX_RETRY',
    'KAFKA_RETRY_INTERVAL_SECONDS'
]

def check_required_env_vars():
    for var in required_env_vars:
        if var not in os.environ:
            logger.error(f"Missing required environment variable: {var}")
            raise EnvironmentError(f"Missing required environment variable: {var}")