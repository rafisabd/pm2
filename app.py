from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_pm02():
    try:
        url = "https://api.airgradient.com/public/api/v1/locations/164620/measures/current?token=90e01a45-09c0-461e-acad-b88ec065e6ab"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return jsonify({"pm02": data["pm02"]})
    except Exception as e:
        return jsonify({"error": "pm02 can't be loaded from render"}), 502

if __name__ == '__main__':
    app.run()
