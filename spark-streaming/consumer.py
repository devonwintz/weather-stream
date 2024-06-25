import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat, expr, from_json, lit, avg, window
from schemas import weather_data_json_schema
from dotenv import load_dotenv, find_dotenv
from utils import check_required_env_vars

load_dotenv(dotenv_path=find_dotenv())

logger = logging.getLogger(__name__)

# Check for required environment variables
try:
    check_required_env_vars()
except EnvironmentError as e:
    logger.error(f"Failed to initialize application: {e}")
    exit(1)

KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC')
KAFKA_BOOTSTRAP_SERVER = os.environ.get('KAFKA_HOST')
KAFKA_OFFSET = os.environ.get('AUTO_OFFSET_RESET')
DETAILED_SUMMARY = os.environ.get('DETAILED_SUMMARY')
FETCH_INTERVAL_SECONDS = int(os.environ.get('FETCH_INTERVAL_SECONDS'))
CASSANDRA_USER = os.environ.get('CASSANDRA_USER')
CASSANDRA_HOST = os.environ.get('CASSANDRA_HOST', '127.0.0.1')
CASSANDRA_PW = os.environ.get('CASSANDRA_PW')
CASSANDRA_KEYSPACE = os.environ.get('CASSANDRA_KEYSPACE')
CASSANDRA_TABLE = os.environ.get('CASSANDRA_TABLE')
WINDOW_TIME = (int(os.environ.get('WINDOW_INTERVAL_SECONDS')))/60



# Kafka options for streaming
kafka_options = {
    "kafka.bootstrap.servers": KAFKA_BOOTSTRAP_SERVER,
    "startingOffsets": KAFKA_OFFSET,
    "subscribe": KAFKA_TOPIC
}

def create_spark_session(app_name):
    """Create a Spark session."""
    return SparkSession.builder \
            .appName(app_name) \
            .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
            .config("spark.streaming.stopGracefullyOnShutdown", True) \
            .config("spark.cassandra.output.consistency.level", "ONE") \
            .config("spark.cassandra.auth.username", CASSANDRA_USER) \
            .config("spark.cassandra.auth.password", CASSANDRA_PW) \
            .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
                "com.datastax.spark:spark-cassandra-connector_2.12:3.3.0") \
            .config("spark.sql.extensions", "com.datastax.spark.connector.CassandraSparkExtensions") \
            .getOrCreate()

def write_to_cassandra(df):
    """Write data to a Cassandra table."""
    df.write \
        .format("org.apache.spark.sql.cassandra") \
        .mode("append") \
        .options(table=CASSANDRA_TABLE, keyspace=CASSANDRA_KEYSPACE) \
        .save()


def parse_weather_data(df):
    """Parse weather data from Kafka messages."""
    parsed_df = df.withColumn("value", expr("CAST(value AS STRING)")) \
                  .withColumn("weather_data", from_json(col("value"), weather_data_json_schema))

    summary_columns = [
        ("Precipitation", "PrecipitationSummary"),
        ("Temperature", "TemperatureSummary")
    ]

    for summary_type, summary_name in summary_columns:
        for time_window in ["Past6Hours", "Past12Hours", "Past24Hours"]:
            for metric_type in ["Metric", "Imperial"]:
                if summary_type == "Temperature":
                    for temperature_range in ["Minimum", "Maximum"]:
                        column_name = f"{summary_type}{time_window}{temperature_range}{metric_type}"
                        parsed_df = parsed_df.withColumn(
                            column_name,
                            concat(
                                col(f"weather_data.{summary_type}.{summary_name}.{time_window}.{temperature_range}.{metric_type}.Value"),
                                lit(" "),
                                col(f"weather_data.{summary_type}.{summary_name}.{time_window}.{temperature_range}.{metric_type}.Unit")
                            )
                        )
                else:
                    column_name = f"{summary_type}{time_window}{metric_type}"
                    parsed_df = parsed_df.withColumn(
                        column_name,
                        concat(
                            col(f"weather_data.{summary_type}.{summary_name}.{time_window}.{metric_type}.Value"),
                            lit(" "),
                            col(f"weather_data.{summary_type}.{summary_name}.{time_window}.{metric_type}.Unit")
                        )
                    )
    return parsed_df

def select_flattened_df(parsed_df, detailed_summary=DETAILED_SUMMARY):
    """Select columns for the flattened DataFrame."""
    common_columns = [
        col("weather_data.LocalObservationDateTime").alias("EventTime"),
        col("weather_data.CityCode").alias("CityCode"),
        col("weather_data.CityName").alias("CityName"),
        col("weather_data.WeatherText").alias("Weather"),
        col("weather_data.IsDayTime").alias("IsDayTime"),
        col("weather_data.Humidity").alias("Humidity"),
        col("weather_data.UVIndexText").alias("UVIndex"),
        col("weather_data.CloudCover").alias("CloudCover"),
        concat(
            col("weather_data.Wind.Direction.Degrees"),
            lit(" "),
            col("weather_data.Wind.Direction.English")
        ).alias("WindDirection"),
        col("weather_data.Wind.Speed.Metric.Value").alias("WindSpeedMetric"),
        col("weather_data.Wind.Speed.Imperial.Value").alias("WindSpeedImperial"),
        col("weather_data.Precipitation.CurrentPrecipitation.Metric.Value").alias("CurrentPrecipitationMetric"),
        col("weather_data.Precipitation.CurrentPrecipitation.Imperial.Value").alias("CurrentPrecipitationImperial"),
        col("weather_data.Temperature.CurrentTemperature.Metric.Value").alias("CurrentTemperatureMetric"),
        col("weather_data.Temperature.CurrentTemperature.Imperial.Value").alias("CurrentTemperatureImperial"),
    ]

    if detailed_summary:
        additional_columns = [
            col("PrecipitationPast6HoursMetric"),
            col("PrecipitationPast6HoursImperial"),
            col("PrecipitationPast12HoursMetric"),
            col("PrecipitationPast12HoursImperial"),
            col("PrecipitationPast24HoursMetric"),
            col("PrecipitationPast24HoursImperial"),
            col("TemperaturePast6HoursMinimumMetric"),
            col("TemperaturePast6HoursMinimumImperial"),
            col("TemperaturePast6HoursMaximumMetric"),
            col("TemperaturePast6HoursMaximumImperial"),
            col("TemperaturePast12HoursMinimumMetric"),
            col("TemperaturePast12HoursMinimumImperial"),
            col("TemperaturePast12HoursMaximumMetric"),
            col("TemperaturePast12HoursMaximumImperial"),
            col("TemperaturePast24HoursMinimumMetric"),
            col("TemperaturePast24HoursMinimumImperial"),
            col("TemperaturePast24HoursMaximumMetric"),
            col("TemperaturePast24HoursMaximumImperial"),
        ]
        return parsed_df.select(*common_columns, *additional_columns)
    else:
        return parsed_df.select(*common_columns)

if __name__ == '__main__':
    # Set up Spark session
    spark = create_spark_session("weather_stream")
    spark.sparkContext.setLogLevel("ERROR")

    # Read Kafka stream
    kafka_df = spark.readStream \
        .format("kafka") \
        .options(**kafka_options) \
        .load()

    # Parse weather data
    parsed_df = parse_weather_data(kafka_df)

    # Select columns for flattened DataFrame
    flattened_df = select_flattened_df(parsed_df)

    # Define tumbling window for aggregation
    windowed_df = flattened_df \
        .withWatermark("EventTime", f"{WINDOW_TIME + 1} minutes") \
        .groupBy(
            window(col("EventTime"), f"{WINDOW_TIME} mintes").alias("time_window"),
            col("CityCode").alias("city_code"),
            col("CityName").alias("city_name")
        ) \
        .agg(
            avg("Humidity").alias("avg_humidity"),
            avg("WindSpeedMetric").alias("avg_wind_speed_metric"),
            avg("WindSpeedImperial").alias("avg_wind_speed_imperial"),
            avg("CurrentPrecipitationMetric").alias("avg_precipitation_metric"),
            avg("CurrentPrecipitationImperial").alias("avg_precipitation_imperial"),
            avg("CurrentTemperatureMetric").alias("avg_temperature_metric"),
            avg("CurrentTemperatureImperial").alias("avg_temperature_imperial")
        ) \
        .withColumn("event_time", col("time_window.start")) \
            .select(
                col("event_time"),
                col("city_code"),
                col("city_name"),
                col("avg_humidity"),
                col("avg_wind_speed_metric"),
                col("avg_wind_speed_imperial"),
                col("avg_precipitation_metric"),
                col("avg_precipitation_imperial"),
                col("avg_temperature_metric"),
                col("avg_temperature_imperial")
            )
    # Write results to console
    console_query = windowed_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    # Write results to Cassandra
    cassandra_query = windowed_df.writeStream \
        .outputMode("append") \
        .foreachBatch(lambda batch_df, batch_id: write_to_cassandra(batch_df)) \
        .start()

    # Await termination for both queries
    console_query.awaitTermination()
    cassandra_query.awaitTermination()