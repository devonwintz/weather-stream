from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, BooleanType, TimestampType, DoubleType
)

weather_data_json_schema = StructType([
    StructField("CityCode", StringType(), True),
    StructField("CityName", StringType(), True),
    StructField("LocalObservationDateTime", TimestampType(), True),
    StructField("WeatherText", StringType(), True),
    StructField("IsDayTime", BooleanType(), True),
    StructField("Humidity", IntegerType(), True),
    StructField("Wind", StructType([
        StructField("Direction", StructType([
            StructField("Degrees", IntegerType(), True),
            StructField("English", StringType(), True),
            StructField("Localized", StringType(), True),
        ]), True),
        StructField("Speed", StructType([
            StructField("Metric", StructType([
                StructField("Value", DoubleType(), True),
                StructField("Unit", StringType(), True),
                StructField("UnitType", IntegerType(), True),
            ]), True),
            StructField("Imperial", StructType([
                StructField("Value", DoubleType(), True),
                StructField("Unit", StringType(), True),
                StructField("UnitType", IntegerType(), True),
            ]), True),
        ]), True),
    ]), True),
    StructField("UVIndexText", StringType(), True),
    StructField("CloudCover", IntegerType(), True),
    StructField("Precipitation", StructType([
        StructField("CurrentPrecipitation", StructType([
            StructField("Metric", StructType([
                StructField("Value", DoubleType(), True),
                StructField("Unit", StringType(), True),
                StructField("UnitType", IntegerType(), True),
            ]), True),
            StructField("Imperial", StructType([
                StructField("Value", DoubleType(), True),
                StructField("Unit", StringType(), True),
                StructField("UnitType", IntegerType(), True),
            ]), True),
        ]), True),
        StructField("PrecipitationSummary", StructType([
            StructField("PastHour", StructType([
                StructField("Metric", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
                StructField("Imperial", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
            ]), True),
            StructField("Past3Hours", StructType([
                StructField("Metric", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
                StructField("Imperial", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
            ]), True),
            StructField("Past6Hours", StructType([
                StructField("Metric", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
                StructField("Imperial", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
            ]), True),
            StructField("Past9Hours", StructType([
                StructField("Metric", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
                StructField("Imperial", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
            ]), True),
            StructField("Past12Hours", StructType([
                StructField("Metric", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
                StructField("Imperial", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
            ]), True),
            StructField("Past18Hours", StructType([
                StructField("Metric", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
                StructField("Imperial", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
            ]), True),
            StructField("Past24Hours", StructType([
                StructField("Metric", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
                StructField("Imperial", StructType([
                    StructField("Value", DoubleType(), True),
                    StructField("Unit", StringType(), True),
                    StructField("UnitType", IntegerType(), True),
                ]), True),
            ]), True),
        ]), True),
    ]), True),
    StructField("Temperature", StructType([
        StructField("CurrentTemperature", StructType([
            StructField("Metric", StructType([
                StructField("Value", DoubleType(), True),
                StructField("Unit", StringType(), True),
                StructField("UnitType", IntegerType(), True),
            ]), True),
            StructField("Imperial", StructType([
                StructField("Value", DoubleType(), True),
                StructField("Unit", StringType(), True),
                StructField("UnitType", IntegerType(), True),
            ]), True),
        ]), True),
        StructField("TemperatureSummary", StructType([
            StructField("Past6Hours", StructType([
                StructField("Minimum", StructType([
                    StructField("Metric", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                    StructField("Imperial", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                ]), True),
                StructField("Maximum", StructType([
                    StructField("Metric", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                    StructField("Imperial", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                ]), True),
            ]), True),
            StructField("Past12Hours", StructType([
                StructField("Minimum", StructType([
                    StructField("Metric", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                    StructField("Imperial", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                ]), True),
                StructField("Maximum", StructType([
                    StructField("Metric", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                    StructField("Imperial", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                ]), True),
            ]), True),
            StructField("Past24Hours", StructType([
                StructField("Minimum", StructType([
                    StructField("Metric", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                    StructField("Imperial", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                ]), True),
                StructField("Maximum", StructType([
                    StructField("Metric", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                    StructField("Imperial", StructType([
                        StructField("Value", DoubleType(), True),
                        StructField("Unit", StringType(), True),
                        StructField("UnitType", IntegerType(), True),
                    ]), True),
                ]), True),
            ]), True),
        ]), True),
    ]), True),
])
