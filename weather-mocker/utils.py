import json
import time
import random
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def load_json_file(file_path):
    """Load JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded JSON data from {file_path}.")
        return data
    except FileNotFoundError:
        logger.error(f"Error: The file '{file_path}' does not exist.")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error: Failed to decode JSON in '{file_path}'.")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

cities = load_json_file('repo/cities.json')

def generate_fake_weather_data(city_code='nyc'):
    if city_code not in cities:
        error_msg = f"{city_code} does not exist in repo."
        logger.error(error_msg)
        return {
            "status": "error",
            "faultString": error_msg
        }

    weather_conditions = {
        'Sunny': 0.5,
        'Cloudy': 0.2,
        'Rainy': 0.15,
        'Snowy': 0.05,
        'Windy': 0.05,
        'Foggy': 0.03,
        'Thunderstorm': 0.02
    }

    wind_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

    city_data = cities[city_code]

    now = datetime.utcnow() + timedelta(hours=city_data['timezone'])
    is_daytime = 6 <= now.hour <= 18

    # Adjust temperature ranges based on city and whether it's day or night
    if is_daytime:
        temp_range = city_data['avg_temp_range']
    else:
        temp_range = (city_data['avg_temp_range'][0] - 5,
                      city_data['avg_temp_range'][1] - 5)

    temperature_celsius = round(random.uniform(*temp_range), 2)
    temperature_fahrenheit = round(temperature_celsius * 9/5 + 32, 2)

    # Select weather condition based on predefined probabilities
    weather_condition = random.choices(
        list(weather_conditions.keys()), weights=weather_conditions.values(), k=1)

    # Select a random wind direction
    wind_direction = random.choice(wind_directions)

    weather_data = {
        'CityCode': city_code,
        'CityName': cities[city_code]['name'],
        'LocalObservationDateTime': now.isoformat(),
        'EpochTime': int(time.time()),
        'WeatherText': random.choice(weather_condition),
        'IsDayTime': is_daytime,
        'Humidity': random.randint(20, 100),
        'Wind': {
            'Direction': {
                'Degrees': random.randint(0, 360),
                'English': random.choice(wind_direction),
                'Localized': random.choice(wind_direction)
            },
            'Speed': {
                'Metric': {
                    'Value': round(random.uniform(0, 50), 2),
                    'Unit': 'km/h',
                    'UnitType': 7
                },
                'Imperial': {
                    'Value': round(random.uniform(0, 31), 2),
                    'Unit': 'mph',
                    'UnitType': 9
                }
            }
        },
        'UVIndexText': random.choice(['Low', 'Moderate', 'High', 'Very High', 'Extreme']),
        'CloudCover': random.randint(0, 100),
        'Precipitation': {
            'CurrentPrecipitation': {
                'Metric': {
                    'Value': round(random.uniform(0, 50), 2),
                    'Unit': 'mm',
                    'UnitType': 3
                },
                'Imperial': {
                    'Value': round(random.uniform(0, 2), 2),
                    'Unit': 'in',
                    'UnitType': 1
                }
            },
            'PrecipitationSummary': {
                'PastHour': {
                    'Metric': {
                        'Value': round(random.uniform(0, 50), 2),
                        'Unit': 'mm',
                        'UnitType': 3
                    },
                    'Imperial': {
                        'Value': round(random.uniform(0, 2), 2),
                        'Unit': 'in',
                        'UnitType': 1
                    }
                },
                'Past3Hours': {
                    'Metric': {
                        'Value': round(random.uniform(0, 100), 2),
                        'Unit': 'mm',
                        'UnitType': 3
                    },
                    'Imperial': {
                        'Value': round(random.uniform(0, 4), 2),
                        'Unit': 'in',
                        'UnitType': 1
                    }
                },
                'Past6Hours': {
                    'Metric': {
                        'Value': round(random.uniform(0, 150), 2),
                        'Unit': 'mm',
                        'UnitType': 3
                    },
                    'Imperial': {
                        'Value': round(random.uniform(0, 6), 2),
                        'Unit': 'in',
                        'UnitType': 1
                    }
                },
                'Past9Hours': {
                    'Metric': {
                        'Value': round(random.uniform(0, 200), 2),
                        'Unit': 'mm',
                        'UnitType': 3
                    },
                    'Imperial': {
                        'Value': round(random.uniform(0, 8), 2),
                        'Unit': 'in',
                        'UnitType': 1
                    }
                },
                'Past12Hours': {
                    'Metric': {
                        'Value': round(random.uniform(0, 250), 2),
                        'Unit': 'mm',
                        'UnitType': 3
                    },
                    'Imperial': {
                        'Value': round(random.uniform(0, 10), 2),
                        'Unit': 'in',
                        'UnitType': 1
                    }
                },
                'Past18Hours': {
                    'Metric': {
                        'Value': round(random.uniform(0, 300), 2),
                        'Unit': 'mm',
                        'UnitType': 3
                    },
                    'Imperial': {
                        'Value': round(random.uniform(0, 12), 2),
                        'Unit': 'in',
                        'UnitType': 1
                    }
                },
                'Past24Hours': {
                    'Metric': {
                        'Value': round(random.uniform(0, 350), 2),
                        'Unit': 'mm',
                        'UnitType': 3
                    },
                    'Imperial': {
                        'Value': round(random.uniform(0, 14), 2),
                        'Unit': 'in',
                        'UnitType': 1
                    }
                }
            }
        },
        'Temperature': {
            'CurrentTemperature': {
                'Metric': {
                    'Value': temperature_celsius,
                    'Unit': 'C',
                    'UnitType': 17
                },
                'Imperial': {
                    'Value': temperature_fahrenheit,
                    'Unit': 'F',
                    'UnitType': 18
                }
            },
            'TemperatureSummary': {
                'Past6HourRange': {
                    'Minimum': {
                        'Metric': {
                            'Value': round(random.uniform(-10, 40), 2),
                            'Unit': 'C',
                            'UnitType': 17
                        },
                        'Imperial': {
                            'Value': round(random.uniform(14, 104), 2),
                            'Unit': 'F',
                            'UnitType': 18
                        }
                    },
                    'Maximum': {
                        'Metric': {
                            'Value': round(random.uniform(-10, 40), 2),
                            'Unit': 'C',
                            'UnitType': 17
                        },
                        'Imperial': {
                            'Value': round(random.uniform(14, 104), 2),
                            'Unit': 'F',
                            'UnitType': 18
                        }
                    }
                },
                'Past12HourRange': {
                    'Minimum': {
                        'Metric': {
                            'Value': round(random.uniform(-10, 40), 2),
                            'Unit': 'C',
                            'UnitType': 17
                        },
                        'Imperial': {
                            'Value': round(random.uniform(14, 104), 2),
                            'Unit': 'F',
                            'UnitType': 18
                        }
                    },
                    'Maximum': {
                        'Metric': {
                            'Value': round(random.uniform(-10, 40), 2),
                            'Unit': 'C',
                            'UnitType': 17
                        },
                        'Imperial': {
                            'Value': round(random.uniform(14, 104), 2),
                            'Unit': 'F',
                            'UnitType': 18
                        }
                    }
                },
                'Past24HourRange': {
                    'Minimum': {
                        'Metric': {
                            'Value': round(random.uniform(-10, 40), 2),
                            'Unit': 'C',
                            'UnitType': 17
                        },
                        'Imperial': {
                            'Value': round(random.uniform(14, 104), 2),
                            'Unit': 'F',
                            'UnitType': 18
                        }
                    },
                    'Maximum': {
                        'Metric': {
                            'Value': round(random.uniform(-10, 40), 2),
                            'Unit': 'C',
                            'UnitType': 17
                        },
                        'Imperial': {
                            'Value': round(random.uniform(14, 104), 2),
                            'Unit': 'F',
                            'UnitType': 18
                        }
                    }
                }
            }
        }
    }

    return weather_data
