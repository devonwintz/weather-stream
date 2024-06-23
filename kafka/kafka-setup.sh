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
