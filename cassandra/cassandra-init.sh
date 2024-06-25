# Function to wait for Cassandra to be available
wait_for_cassandra() {
    retries=0
    max_retries=$CASSANDRA_RETRY
    until printf "" 2>>/dev/null >>/dev/tcp/$CASSANDRA_HOST/$CASSANDRA_PORT; do
        sleep $CASSANDRA_RETRY_INTERVAL_SECONDS
        retries=$((retries + 1))
        echo "Attempt $retries: Waiting for Cassandra to be available on $CASSANDRA_HOST:$CASSANDRA_PORT..."
        if [ $retries -eq $max_retries ]; then
            echo "Max retries reached. Exiting."
            exit 1
        fi
    done
    echo "Cassandra is available on $CASSANDRA_HOST:$CASSANDRA_PORT."
}

# Function to create keyspace
create_keyspace() {
    create_keyspace_command="CREATE KEYSPACE IF NOT EXISTS $CASSANDRA_KEYSPACE WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': $CASSANDRA_REPLICATION_FACTOR};"
    cqlsh $CASSANDRA_HOST -u $CASSANDRA_USER -p $CASSANDRA_PW -e "$create_keyspace_command"

    if [ $? -eq 0 ]; then
        echo "Keyspace $CASSANDRA_KEYSPACE created successfully or already exists."
    else
        echo "Failed to create keyspace '$CASSANDRA_KEYSPACE'."
        exit 1
    fi
}

# Function to create table
create_table() {
    create_table_command="CREATE TABLE IF NOT EXISTS $CASSANDRA_KEYSPACE.$CASSANDRA_TABLE (
        event_time TIMESTAMP,
        city_code TEXT,
        city_name TEXT,
        avg_humidity DOUBLE,
        avg_wind_speed_metric DOUBLE,
        avg_wind_speed_imperial DOUBLE,
        avg_precipitation_metric DOUBLE,
        avg_precipitation_imperial DOUBLE,
        avg_temperature_metric DOUBLE,
        avg_temperature_imperial DOUBLE,
        PRIMARY KEY (city_code, event_time)
    );"
    cqlsh $CASSANDRA_HOST -u $CASSANDRA_USER -p $CASSANDRA_PW -e "$create_table_command"
    if [ $? -eq 0 ]; then
        echo "Table $CASSANDRA_TABLE created successfully in keyspace $CASSANDRA_KEYSPACE or already exists."
    else
        echo "Failed to create table $CASSANDRA_TABLE in keyspace $CASSANDRA_KEYSPACE."
        exit 1
    fi
}

# Check for required environment variables
if [ -z "$CASSANDRA_HOST" ] || [ -z "$CASSANDRA_PORT" ] || [ -z "$CASSANDRA_USER" ] || [ -z "$CASSANDRA_PW" ] || [ -z "$CASSANDRA_KEYSPACE" ] || [ -z "$CASSANDRA_TABLE" ] || [ -z "$CASSANDRA_REPLICATION_FACTOR" ]; then
    echo "One or more required environment variables are not set."
    echo "Please set CASSANDRA_HOST, CASSANDRA_PORT, CASSANDRA_USER, CASSANDRA_PW, CASSANDRA_KEYSPACE, CASSANDRA_TABLE, and CASSANDRA_REPLICATION_FACTOR."
    exit 1
fi

# Check if Cassandra is available
wait_for_cassandra

# Create keyspace
create_keyspace

# Create table
create_table
