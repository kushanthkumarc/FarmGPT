import os
import redis
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI", "")
client = MongoClient(MONGO_URI) if MONGO_URI else None
db = client['FarmGPT'] if client else None

# Collections
users_collection = db['users'] if db is not None else None
chat_history_collection = db['chat_history'] if db is not None else None
doc_metadata_collection = db['doc_metadata'] if db is not None else None
pest_reports_collection = db['pest_reports'] if db is not None else None

# Geospatial Indexing for Location-based Alerts
if pest_reports_collection is not None:
    try:
        # Create a 2dsphere index for both reports and users
        pest_reports_collection.create_index([("location", "2dsphere")])
        if users_collection is not None:
            users_collection.create_index([("location", "2dsphere")])
        print("✅ Geospatial 2dsphere indexes verified for 'pest_reports' and 'users'.")
    except Exception as e:
        print(f"Index creation warning: {e}")

# Redis Cache
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

redis_client = None
try:
    if REDIS_HOST:
        redis_client = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            password=REDIS_PASSWORD, 
            decode_responses=True
        )
except Exception as e:
    print(f"Redis Connection Error: {e}")

def cache_response(query, lang, response):
    """Caches an LLM response to save tokens and time if same query occurs."""
    if not redis_client: return
    key = f"farmgpt:{lang}:{query.lower().strip()}"
    try:
        redis_client.setex(key, 3600*24, json.dumps(response)) # 24h cache
    except: pass

def get_cached_response(query, lang):
    """Retrieves a previously cached response."""
    if not redis_client: return None
    key = f"farmgpt:{lang}:{query.lower().strip()}"
    try:
        cached = redis_client.get(key)
        if cached: return json.loads(cached)
    except: pass
    return None

from datetime import datetime

def save_chat(user_id, role, content, language):
    """Persistently stores chat history in MongoDB Atlas."""
    if chat_history_collection is None: return
    try:
        chat_history_collection.insert_one({
            "user_id": user_id,
            "role": role,
            "content": content,
            "language": language,
            "timestamp": datetime.now()
        })
    except: pass
def get_chat_history(user_id, limit=20):
    """Retrieves the last N messages for a specific user from MongoDB."""
    if chat_history_collection is None: return []
    try:
        cursor = chat_history_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
        history = []
        for doc in cursor:
            history.append({
                "role": doc.get("role"),
                "content": doc.get("content"),
                "language": doc.get("language")
            })
        return history[::-1] # Reverse back to chronological order
    except:
        return []
