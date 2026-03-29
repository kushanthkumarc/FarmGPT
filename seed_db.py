from db import users_collection
from datetime import datetime

def seed_users():
    print("🌱 Seeding dummy users for Pest Alert System...")
    
    if users_collection is None:
        print("❌ Error: DB connection failed. Check your MONGO_URI and IP whitelist.")
        return

    users = [
        {
            "user_id": "farmer_A",
            "name": "Arjun",
            "primary_crop": "Rice",
            "fcm_token": "token_A",
            "language": "Hindi",
            "location": {"type": "Point", "coordinates": [77.5946, 12.9716]}
        },
        {
            "user_id": "farmer_B",
            "name": "Bala",
            "primary_crop": "Tamil",
            "fcm_token": "token_B",
            "language": "Tamil",
            "location": {"type": "Point", "coordinates": [77.5948, 12.9718]}
        },
        {
            "user_id": "farmer_C",
            "name": "Chandra",
            "primary_crop": "Rice",
            "fcm_token": "token_C",
            "language": "English",
            "location": {"type": "Point", "coordinates": [77.5950, 12.9720]}
        }
    ]
    
    try:
        # Clear old test users if any
        users_collection.delete_many({"user_id": {"$in": ["farmer_A", "farmer_B", "farmer_C"]}})
        
        # Insert new ones
        users_collection.insert_many(users)
        print("✅ 3 Test Farmers successfully added to MongoDB Atlas.")
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    seed_users()
