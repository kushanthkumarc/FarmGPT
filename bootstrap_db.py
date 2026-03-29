import json
import os
from db import doc_metadata_collection

def sync_metadata():
    """Syncs the cleaned JSON knowledge base metadata to MongoDB Atlas."""
    if doc_metadata_collection is None:
        print("❌ MongoDB connection not established. Check MONGO_URI in .env")
        return

    knowledge_path = 'data/rag_knowledge_base.json'
    if not os.path.exists(knowledge_path):
        print(f"❌ Could not find {knowledge_path}. Run clean_json_v2.py first.")
        return

    with open(knowledge_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Clear old metadata to prevent duplicates (optional, based on need)
    # doc_metadata_collection.delete_many({}) 

    print(f"Syncing {len(data)} items to MongoDB Atlas...")
    
    success_count = 0
    for item in data:
        # Check if already exists by source URL to avoid duplicates
        exists = doc_metadata_collection.find_one({"metadata.source": item['metadata']['source']})
        if not exists:
            doc_metadata_collection.insert_one(item)
            success_count += 1

    print(f"✅ Successfully synced {success_count} new knowledge items to MongoDB Atlas.")

if __name__ == '__main__':
    sync_metadata()
