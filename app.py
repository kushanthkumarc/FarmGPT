from flask import Flask, request, jsonify, render_template
from weather_service import get_weather, generate_alert

app = Flask(__name__)

# 1. Simple in-memory session store
user_session = {
    "lat": None,
    "lon": None
}

@app.route("/")
def index():
    """Renders the frontend page"""
    return render_template("index.html")

@app.route("/set-location", methods=["POST"])
def set_location():
    """
    2. Endpoint to set the location via POST request.
    Stores the location in `user_session`.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON body."}), 400
            
        lat = data.get("lat")
        lon = data.get("lon")

        # Validate existence
        if lat is None or lon is None:
            return jsonify({"error": "Missing lat or lon in request."}), 400
            
        # Validate type and range
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return jsonify({"error": "Invalid coordinates format."}), 400

        if not (-90 <= lat <= 90):
            return jsonify({"error": "lat must be between -90 and 90"}), 400
            
        if not (-180 <= lon <= 180):
            return jsonify({"error": "lon must be between -180 and 180"}), 400

        # Store in session
        user_session["lat"] = lat
        user_session["lon"] = lon

        return jsonify({
            "message": "Location set successfully",
            "lat": lat,
            "lon": lon
        }), 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@app.route("/location", methods=["GET"])
def get_location():
    """
    5. Returns current stored GPS location.
    """
    if user_session["lat"] is None or user_session["lon"] is None:
        return jsonify({"error": "No location stored."}), 404
        
    return jsonify({
        "lat": user_session["lat"],
        "lon": user_session["lon"]
    }), 200


@app.route("/weather", methods=["GET"])
def get_weather_endpoint():
    """
    3. Modify existing /weather endpoint to use query params if available,
    otherwise fallback to `user_session`.
    """
    query_lat = request.args.get("lat")
    query_lon = request.args.get("lon")
    
    # Validation logic for query parameter bounds if present
    if query_lat is not None and query_lon is not None:
        try:
            lat = float(query_lat)
            lon = float(query_lon)
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return jsonify({"error": "Invalid query coordinates."}), 400
        except ValueError:
            return jsonify({"error": "Invalid query coordinates format."}), 400
    else:
        # Fallback to stored user_session location
        lat = user_session["lat"]
        lon = user_session["lon"]

    if lat is None or lon is None:
        return jsonify({
            "error": "Location not set. Provide lat/lon or call /set-location first."
        }), 400

    # 4. Weather flow
    weather = get_weather(lat, lon)
    if weather is None:
         # 6. API failure handling
         return jsonify({"error": "Weather API failed to retrieve data"}), 502

    alert = generate_alert(weather)

    return jsonify({
        "weather": weather,
        "alert": alert
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
