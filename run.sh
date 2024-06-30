# Load environment variables from .env file
set -a
source .env
set +a

# Remove all services including volumes
echo "Removing all services including volumes..."
docker-compose down -v

# Clear the terminal
clear

echo "Building all services..."
docker-compose build

# Clear the terminal
clear

# Start all services in detached mode
echo "Starting all services..."
docker-compose up -d

# Clear the terminal
clear

# Check if the Cassandra plugin is installed by checking the directory
plugin_installed=$(docker-compose exec -T grafana /bin/bash -c '[ -d "/var/lib/grafana/plugins/$GRAFANA_DATASOURCE_TYPE" ] && echo "installed" || echo "not installed"')

msg="Cassandra plugin not installed. Waiting"
echo -n "$msg"
while [ "$plugin_installed" != "installed" ]; do
    echo -n "."
    sleep 5
    plugin_installed=$(docker-compose exec -T grafana /bin/bash -c '[ -d "/var/lib/grafana/plugins/$GRAFANA_DATASOURCE_TYPE" ] && echo "installed" || echo "not installed"')
done

# Plugin installed, restart Grafana container
echo "Cassandra plugin installed. Restarting Grafana container..."
docker-compose restart grafana