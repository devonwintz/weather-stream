# Function to check if Kafka is running using /dev/tcp
function check_kafka {
  HOST=$(echo $BOOTSTRAP_SERVER | cut -d':' -f1)
  PORT=$(echo $BOOTSTRAP_SERVER | cut -d':' -f2)
  if (echo > /dev/tcp/$HOST/$PORT) &>/dev/null; then
    return 0
  else
    return 1
  fi
}

# Retry logic
RETRY_COUNT=0
while ! check_kafka; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $KAFKA_MAX_RETRY ]; then
    echo "Kafka is not running after $KAFKA_MAX_RETRY attempts"
    exit 1
  fi
  echo "Kafka is not running, retrying in $KAFKA_RETRY_INTERVAL_SECONDS seconds... ($RETRY_COUNT/$KAFKA_MAX_RETRY)"
  sleep $KAFKA_RETRY_INTERVAL_SECONDS
done

echo "Kafka is running...creating topic..."

# Check if the topic already exists
/opt/bitnami/kafka/bin/kafka-topics.sh --describe --topic $TOPIC_NAME --bootstrap-server $BOOTSTRAP_SERVER > /dev/null 2>&1
EXIST_STATUS=$?

if [ $EXIST_STATUS -eq 0 ]; then
  echo "Topic '$TOPIC_NAME' already exists"
else
  # Create Kafka topic
  /opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $TOPIC_NAME --replication-factor $REPLICATION_FACTOR --partitions $PARTITIONS --bootstrap-server $BOOTSTRAP_SERVER
  CREATE_STATUS=$?

  if [ $CREATE_STATUS -eq 0 ]; then
    echo "Topic '$TOPIC_NAME' was created"
  else
    echo "Failed to create topic '$TOPIC_NAME'"
  fi
fi
