# Function to check if Grafana is running
check_grafana_running() {
    local RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $GRAFANA_MAX_RETRY ]; do
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $GRAFANA_URL/login)
        if [ "$HTTP_STATUS" -eq 200 ]; then
            return 0
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            echo "Waiting for Grafana to start... Retry $RETRY_COUNT/$GRAFANA_MAX_RETRY"
            sleep $GRAFANA_RETRY_INTERVAL_SECONDS
        fi
    done

    echo "Grafana did not start within the expected time."
    return 1
}

# Function to check if Grafana Cassandra plugin is installed
check_cassandra_plugin_installed() {
    if [ -d "/var/lib/grafana/plugins/$GRAFANA_DATASOURCE_TYPE" ]; then
        echo "Cassandra plugin is already installed."
        return 0
    else
        echo "Cassandra plugin not found."
        return 1
    fi
}

# Function to install Grafana Cassandra plugin
install_grafana_plugin() {
    # Check if plugin is installed
    if check_cassandra_plugin_installed; then
        return 0  # Cassandra plugin already installed, exit successfully
    fi

    # Attempt to install Cassandra plugin with retries
    echo "Installing Cassandra plugin..."
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $GRAFANA_MAX_RETRY ]; do
        grafana cli plugins install $GRAFANA_DATASOURCE_TYPE
        INSTALL_STATUS=$?

        if [ $INSTALL_STATUS -eq 0 ]; then
            # Check again if plugin installation was successful
            if check_cassandra_plugin_installed; then
                echo "Cassandra plugin installed successfully."
                return 0
            else
                echo "Installation reported success but plugin not found. Retrying..."
            fi
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            echo "Installation failed. Retry $RETRY_COUNT/$GRAFANA_MAX_RETRY..."
        fi
        sleep $GRAFANA_RETRY_INTERVAL_SECONDS
    done

    # Installation failed after max retries
    echo "Failed to install Cassandra plugin after $GRAFANA_MAX_RETRY attempts."
    return 1
}

# Function to generate a random API key name
generate_random_key_name() {
    echo "API_Key_$(date +%s)_$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 8)"
}

# Function to get API key from Grafana
get_api_key() {
    local key_name=$(generate_random_key_name)
    local response=$(curl -s -w "\n%{http_code}" -X POST "$GRAFANA_URL/api/auth/keys" \
        -H "Content-Type: application/json" \
        -H "Authorization: Basic $(echo -n $GRAFANA_USER:$GRAFANA_PW | base64)" \
        -d "{\"name\": \"$key_name\", \"role\": \"Admin\"}")

    local http_code=$(echo "$response" | tail -n1)
    local api_key=$(echo "$response" | head -n1 | sed -n 's/.*"key":"\([^"]*\)".*/\1/p')

    if [ "$http_code" -eq 200 ]; then
        echo "$api_key"
    else
        echo "Failed to create API key. HTTP status code: $http_code"
        echo "Response: $response"
        exit 1
    fi
}

# Function to check if a datasource already exists
datasource_exists() {
    local api_key=$1
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$GRAFANA_URL/api/datasources/name/$GRAFANA_DATASOURCE_NAME" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $api_key")

    if [ "$HTTP_STATUS" -eq 200 ]; then
        return 0
    else
        return 1
    fi
}

# Function to add Cassandra datasource to Grafana
add_grafana_datasource() {
    local api_key=$(get_api_key)

    if datasource_exists $api_key; then
        echo "Datasource '$GRAFANA_DATASOURCE_NAME' already exists. Skipping datasource creation..."
        return 0
    fi

    local JSON_PAYLOAD=$(cat <<EOF
{
  "name": "$GRAFANA_DATASOURCE_NAME",
  "type": "$GRAFANA_DATASOURCE_TYPE",
  "access": "proxy",
  "url": "$CASSANDRA_HOST:$CASSANDRA_PORT",
  "user": "$CASSANDRA_USER",
  "database": "$CASSANDRA_TABLE",
  "basicAuth": true,
  "basicAuthUser": "$CASSANDRA_USER",
  "withCredentials": true,
  "isDefault": false,
  "jsonData": {
    "consistency": "ONE",
    "keyspace": "$CASSANDRA_KEYSPACE",
    "user": "$CASSANDRA_USER",
    "connectTimeout": 10
  },
  "secureJsonFields": {
    "basicAuthPassword": true,
    "password": true
  },
  "secureJsonData": {
    "password": "$CASSANDRA_PW"
  }
}
EOF
    )

    # Add the data source to Grafana
    response=$(curl -s -X POST "$GRAFANA_URL/api/datasources" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $api_key" \
    -d "$JSON_PAYLOAD")

    # Check if the JSON response contains "Datasource added"
    if [[ "$response" == *"Datasource added"* ]]; then
        echo "Cassandra data source added successfully."
    else
        echo "Failed to add Cassandra data source to Grafana."
        exit 1
    fi
}

# Function to build Grafana dashboard
build_dashboard() {
    local api_key=$(get_api_key)
    local refresh_seconds=$((WINDOW_INTERVAL_SECONDS + 60))

    local JSON_PAYLOAD=$(cat <<EOF
{
    "dashboard": {
        "id": null,
        "uid": null,
        "title": "WeatherStream Metrics For $CITY",
        "tags": [],
        "timezone": "browser",
        "schemaVersion": 16,
        "refresh": "$refresh_seconds",
        "panels": [
            {
                "type": "graph",
                "title": "Average Humidity",
                "datasource": "grafana-cassandra",
                "targets": [
                    {
                        "refId": "A",
                        "datasource": "grafana-cassandra",
                        "queryType": "query",
                        "rawQuery": true,
                        "target": "SELECT event_time, avg_humidity FROM weather_keyspace.weather_data;"
                    }
                ],
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": 0,
                    "y": 0
                },
                "legend": {
                    "show": true,
                    "values": true,
                    "avg": true,
                    "alignAsTable": true
                }
            },
            {
                "type": "graph",
                "title": "Average Wind Speed",
                "datasource": "grafana-cassandra",
                "targets": [
                    {
                        "refId": "B",
                        "datasource": "grafana-cassandra",
                        "queryType": "query",
                        "rawQuery": true,
                        "target": "SELECT event_time, avg_wind_speed_metric FROM weather_keyspace.weather_data;"
                    }
                ],
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": 12,
                    "y": 0
                },
                "legend": {
                    "show": true,
                    "values": true,
                    "avg": true,
                    "alignAsTable": true
                }
            },
            {
                "type": "graph",
                "title": "Average Precipitation",
                "datasource": "grafana-cassandra",
                "targets": [
                    {
                        "refId": "C",
                        "datasource": "grafana-cassandra",
                        "queryType": "query",
                        "rawQuery": true,
                        "target": "SELECT event_time, avg_precipitation_metric FROM weather_keyspace.weather_data;"
                    }
                ],
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": 0,
                    "y": 8
                },
                "legend": {
                    "show": true,
                    "values": true,
                    "avg": true,
                    "alignAsTable": true
                }
            },
            {
                "type": "graph",
                "title": "Average Temperature",
                "datasource": "grafana-cassandra",
                "targets": [
                    {
                        "refId": "D",
                        "datasource": "grafana-cassandra",
                        "queryType": "query",
                        "rawQuery": true,
                        "target": "SELECT event_time, avg_temperature_metric FROM weather_keyspace.weather_data;"
                    }
                ],
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": 12,
                    "y": 8
                },
                "legend": {
                    "show": true,
                    "values": true,
                    "avg": true,
                    "alignAsTable": true
                }
            }
        ]
    },
    "overwrite": true
}
EOF
    )

    # Make API call to create/update dashboard
    local response=$(curl --location --request POST "$GRAFANA_URL/api/dashboards/db" \
    --header 'Content-Type: application/json' \
    --header "Authorization: Bearer $api_key" \
    --data-raw "$JSON_PAYLOAD")

    # Check response for success
    if [[ "$response" == *"success"* ]]; then
        echo "Dashboard created successfully."
    else
        echo "Failed to create dashboard in Grafana."
        echo "Response: $response"
        exit 1
    fi
}

# Check for required environment variables
if [ -z "$GRAFANA_DATASOURCE_TYPE" ] || [ -z "$CASSANDRA_HOST" ] || [ -z "$CASSANDRA_PORT" ] || [ -z "$CASSANDRA_USER" ] || \
   [ -z "$CASSANDRA_PW" ] || [ -z "$GRAFANA_URL" ] || [ -z "$GRAFANA_DATASOURCE_NAME" ] || [ -z "$CASSANDRA_KEYSPACE" ] || \
   [ -z "$CASSANDRA_TABLE" ] || [ -z "$GRAFANA_MAX_RETRY" ] || [ -z "$GRAFANA_RETRY_INTERVAL_SECONDS" ] || [ -z "$WINDOW_INTERVAL_SECONDS" ] || [ -z "$CITY" ]; then
    echo "One or more required environment variables are not set."
    echo "Please set GRAFANA_MAX_RETRY, GRAFANA_RETRY_INTERVAL_SECONDS, GRAFANA_DATASOURCE_TYPE, CASSANDRA_HOST, CASSANDRA_PORT, CASSANDRA_USER, CASSANDRA_PW, GRAFANA_URL, GRAFANA_DATASOURCE_NAME, CASSANDRA_KEYSPACE, CASSANDRA_TABLE, CITY, WINDOW_INTERVAL_SECONDS."
    exit 1
fi

# Main execution flow
if check_grafana_running; then
    if install_grafana_plugin; then
        if add_grafana_datasource; then
            build_dashboard
        else
            echo "Failed to add or verify Grafana Cassandra datasource. Exiting."
            exit 1
        fi
    else
        echo "Failed to install Grafana Cassandra plugin. Exiting."
        exit 1
    fi
else
    echo "Grafana is not running. Exiting."
    exit 1
fi
