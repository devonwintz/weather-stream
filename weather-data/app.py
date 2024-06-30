from flask import Flask, jsonify
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import os

app = Flask(__name__)

CASSANDRA_HOST = os.environ.get('CASSANDRA_HOST', '127.0.0.1')
CASSANDRA_USER = os.environ.get('CASSANDRA_USER')
CASSANDRA_PW = os.environ.get('CASSANDRA_PW')
CASSANDRA_KEYSPACE = os.environ.get('CASSANDRA_KEYSPACE')
CASSANDRA_TABLE = os.environ.get('CASSANDRA_TABLE')

def get_cassandra_session():
    auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PW)
    cluster = Cluster([CASSANDRA_HOST], auth_provider=auth_provider)
    session = cluster.connect(CASSANDRA_KEYSPACE)
    return session

@app.route('/weather-data', methods=['GET'])
def get_weather_data():
    session = get_cassandra_session()
    query = f"SELECT * FROM {CASSANDRA_TABLE} LIMIT 100;"
    rows = session.execute(query)
    results = []
    for row in rows:
        results.append({
            "event_time": row.event_time,
            "city_code": row.city_code,
            "city_name": row.city_name,
            "avg_humidity": row.avg_humidity,
            "avg_wind_speed_metric": row.avg_wind_speed_metric,
            "avg_wind_speed_imperial": row.avg_wind_speed_imperial,
            "avg_precipitation_metric": row.avg_precipitation_metric,
            "avg_precipitation_imperial": row.avg_precipitation_imperial,
            "avg_temperature_metric": row.avg_temperature_metric,
            "avg_temperature_imperial": row.avg_temperature_imperial
        })
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
