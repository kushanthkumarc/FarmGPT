from datetime import datetime, timedelta
from db import pest_reports_collection, users_collection
import requests

def report_pest(user_id, lat, lon, disease_id, weather_data=None):
    """Logs a pest report and triggers outbreak check."""
    report = {
        "user_id": user_id,
        "disease_id": disease_id,
        "location": {
            "type": "Point",
            "coordinates": [lon, lat] # GeoJSON uses [Lon, Lat]
        },
        "weather": weather_data or {},
        "timestamp": datetime.now()
    }
    
    # Store the report
    pest_reports_collection.insert_one(report)
    
    # Check for outbreak
    is_outbreak, nearby_farmers = check_for_outbreak(lat, lon, disease_id)
    
    if is_outbreak:
        # PUSH MESSAGES TO ALL NEARBY FARMERS
        count = send_community_notifications(nearby_farmers, disease_id, lat, lon)
        return True, count
    
    return False, 0

def send_community_notifications(farmers, disease_id, lat, lon):
    """
    Simulates a WhatsApp-style notification by inserting a 
    SYSTEM message into the farmer's chat history.
    """
    from db import save_chat
    
    # Simple Translation Mapping for Alerts
    templates = {
        "Hindi": "🚨 **पेस्ट अलर्ट!** आपके 5km के क्षेत्र में *{disease}* की ३+ रिपोर्ट मिली हैं। कृपया अपनी फसल की सुरक्षा करें।",
        "Tamil": "🚨 **பூச்சித் தாக்குதல் எச்சரிக்கை!** உங்கள் பகுதிக்கு அருகில் *{disease}* பாதிப்பு கண்டறியப்பட்டுள்ளது.",
        "English": "🚨 **PEST ALERT!** 3+ reports of *{disease}* have been confirmed within 5km of your farm. Please inspect your crops immediately."
    }
    
    notified_count = 0
    for farmer in farmers:
        user_id = farmer.get("user_id")
        lang = farmer.get("language", "Hindi")
        msg_template = templates.get(lang, templates["English"])
        
        # Format and Push to MongoDB Chat History
        alert_text = msg_template.format(disease=disease_id.replace("_", " ").title())
        save_chat(user_id, "assistant", alert_text, lang)
        
        # If real FCM was configured:
        # send_fcm_push(farmer['fcm_token'], "FarmGPT Alert", alert_text)
        
        notified_count += 1
        
    return notified_count

def check_for_outbreak(lat, lon, disease_id):
    """
    Cluster Logic:
    1. Returns (True, List[user_ids]) if 3+ reports same disease within 5km in 48h.
    2. Accounts for humidity boost for alert priority.
    """
    forty_eight_hours_ago = datetime.now() - timedelta(hours=48)
    
    # Define query radius: 5000 meters
    radius_meters = 5000
    
    # Finding clusters of the SAME disease
    query = {
        "disease_id": disease_id,
        "timestamp": {"$gte": forty_eight_hours_ago},
        "location": {
            "$nearSphere": {
                "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                "$maxDistance": radius_meters
            }
        }
    }
    
    recent_reports = list(pest_reports_collection.find(query))
    count = len(recent_reports)
    
    # [LOGIC] Humidity Boost: If average humidity > 80%, we lower the threshold to 2 reports
    avg_humidity = 0
    if recent_reports:
        hs = [r.get("weather", {}).get("humidity", 0) for r in recent_reports]
        avg_humidity = sum(hs) / len(hs)
    
    outbreak_threshold = 3
    if avg_humidity > 80:
        outbreak_threshold = 2 # Higher risk in high humidity
        
    if count >= outbreak_threshold:
        # Identify OTHER farmers in this 5km radius to notify
        nearby_farmers_query = {
            "location": {
                "$nearSphere": {
                    "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "$maxDistance": radius_meters
                }
            }
        }
        # In reality, filter by primary_crop if needed
        potential_victims = list(users_collection.find(nearby_farmers_query, {"fcm_token": 1, "user_id": 1, "language": 1}))
        return True, potential_victims
        
    return False, []
