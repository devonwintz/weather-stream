from flask import Flask, jsonify
from utils import load_json_file, generate_fake_weather_data

app = Flask(__name__)

cities = load_json_file('repo/cities.json')

def get_city_codes():
    city_codes = []
    for code, city_info in cities.items():
        city_codes.append({'code': code, 'name': city_info['name']})
    return city_codes

@app.route('/fakeweather/currentconditions/<city_code>', methods=['GET'])
def get_current_weather(city_code):
    try:
        weather_data = generate_fake_weather_data(city_code.upper())
        return jsonify(weather_data), 200
    except ValueError as e:
        return str(e), 404

@app.route('/fakeweather/city-codes', methods=['GET'])
def retrieve_city_codes():
    try:
        city_codes = get_city_codes()
        return jsonify(city_codes), 200
    except ValueError as e:
        return str(e), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
