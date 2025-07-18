from flask import Flask, jsonify
import requests

app = Flask(__name__)

def pm25_to_aqi(pm25):
    # Define the breakpoint table for PM2.5 and AQI
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500)
    ]

    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= pm25 <= bp_high:
            # Apply the EPA formula
            aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (pm25 - bp_low) + aqi_low
            return round(aqi)
    
    return None  # If out of range

def pm25_to_cigarettes(pm25, hours_exposed=8):
    # 1 cigarette ≈ 22 µg/m³ over 24 hours
    cigarettes = (pm25 * hours_exposed) / (22 * 24)
    return round(cigarettes, 1), hours_exposed

def aqi_to_health_level(aqi):
    if 0 <= aqi <= 50:
        return 1
    elif 51 <= aqi <= 100:
        return 2
    elif 101 <= aqi <= 150:
        return 3
    elif 151 <= aqi <= 200:
        return 4
    elif 201 <= aqi <= 300:
        return 5
    elif aqi >= 301:
        return 6
    else:
        return None
    
def aqi_to_health_status(aqi):
    if 0 <= aqi <= 50:
        return "GOOD"
    elif 51 <= aqi <= 100:
        return "MODERATE"
    elif 101 <= aqi <= 150:
        return "UNHEALTHY FOR SENSITIVE GROUPS"
    elif 151 <= aqi <= 200:
        return "UNHEALTHY"
    elif 201 <= aqi <= 300:
        return "VERY UNHEALTHY"
    elif aqi >= 301:
        return "HAZARDOUS"
    else:
        return "Invalid AQI"

@app.route('/', methods=['GET'])
def get_pm02():
    try:
        url = "https://api.airgradient.com/public/api/v1/locations/164620/measures/current?token=90e01a45-09c0-461e-acad-b88ec065e6ab"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        pm02 = float(data["pm02"])
        aqi = pm25_to_aqi(pm02)
        
        cigarettes_arr = pm25_to_cigarettes(pm02)
        cigarettes = cigarettes_arr[0]
        cigarettes_hour = cigarettes_arr[1]
        
        health_level = aqi_to_health_level(aqi)
        health_status = aqi_to_health_status(aqi)
        
        return jsonify(
            {
               "aqi": aqi, 
               "cigarettes": cigarettes, 
               "cigarettes_hour": cigarettes_hour , 
               "health_level": health_level,
               "health_status": health_status,
               "pm02": pm02, 
             })
    except Exception as e:
        return jsonify({"error": "pm02 can't be loaded from api gradient"}), 502

if __name__ == '__main__':
    app.run()
