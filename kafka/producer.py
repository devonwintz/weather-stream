import os
import time
import json
import asyncio
import aiohttp
import logging
from kafka import KafkaProducer
from dotenv import load_dotenv, find_dotenv
from utils import check_required_env_vars

load_dotenv(dotenv_path=find_dotenv())

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# Check for required environment variables
try:
    check_required_env_vars()
except EnvironmentError as e:
    logger.error(f"Failed to initialize application: {e}")
    exit(1)


CITY = os.environ.get('CITY')
API_URL = os.environ.get('API_URL')
FETCH_INTERVAL_SECONDS = int(os.environ.get('FETCH_INTERVAL_SECONDS'))
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC')
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_HOST')
MAX_RETRIES = int(os.environ.get('KAFKA_MAX_RETRY'))
RETRY_INTERVAL_SECONDS = int(os.environ.get('KAFKA_RETRY_INTERVAL_SECONDS'))


def serializer(message):
    """Serialize a message to JSON and encode it in UTF-8."""
    try:
        return json.dumps(message).encode('utf-8')
    except (TypeError, ValueError) as e:
        logger.error(f"Serialization error: {e}")
        raise


def create_kafka_producer():
    """Create and return a Kafka producer."""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=serializer
            )
            logger.info("Kafka producer created successfully.")
            return producer
        except Exception as e:
            logger.warning(f"Failed to create Kafka producer: {e}")
            logger.info(f"Retrying in {RETRY_INTERVAL_SECONDS} seconds...")
            time.sleep(RETRY_INTERVAL_SECONDS)
            retries += 1
    logger.error("Max retries exceeded. Could not create Kafka producer.")
    raise RuntimeError("Failed to create Kafka producer after max retries.")


async def fetch_weather_data(session):
    """Fetch weather data from the API."""
    try:
        async with session.get(url=f"{API_URL}/{CITY}") as response:
            response.raise_for_status()  # Raise an error for bad HTTP status codes
            return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"Error fetching weather data: {e}")
        return None


def publish_to_kafka(producer, topic, weather_data):
    """Publish weather data to Kafka."""
    try:
        producer.send(topic, value=weather_data)
        producer.flush()
        logger.info("Message sent to Kafka.")
    except Exception as e:
        logger.error(f"Failed to send message to Kafka: {e}")


async def check_for_changes_and_publish(producer, interval):
    """Fetch weather data and publish changes to Kafka."""
    prev_weather_data = {}
    async with aiohttp.ClientSession() as session:
        while True:
            weather_data = await fetch_weather_data(session)
            if weather_data and weather_data != prev_weather_data:
                prev_weather_data = weather_data
                publish_to_kafka(producer, KAFKA_TOPIC, weather_data)
            await asyncio.sleep(interval)


async def main():
    producer = create_kafka_producer()
    try:
        await check_for_changes_and_publish(producer, FETCH_INTERVAL_SECONDS)
    finally:
        producer.close(timeout=10)
        logger.info("Kafka producer closed.")

if __name__ == '__main__':
    asyncio.run(main())
