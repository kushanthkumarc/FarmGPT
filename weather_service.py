import requests

def get_weather(lat, lon):
    """
    Fetches real-time weather using Open-Meteo API.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("current_weather", {})
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

def generate_alert(weather):
    """
    Generates smart alerts based on current weather conditions.
    """
    if not weather:
        return "Weather data unavailable."
    
    temp = weather.get("temperature", 0)
    wind_speed = weather.get("windspeed", 0)

    alerts = []
    if temp > 35:
        alerts.append("Heatwave Warning: Ensure crops are well hydrated.")
    elif temp < 5:
        alerts.append("Frost Warning: Take measures to protect sensitive plants.")
        
    if wind_speed > 30:
        alerts.append("High Wind Warning: Secure any loose farming equipment.")
        
    if not alerts:
        alerts.append("Conditions normal. No immediate action needed.")
        
    return " | ".join(alerts)
