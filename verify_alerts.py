from db import chat_history_collection

def verify_chat_alerts():
    print("🔍 Verifying Individual Farmer Chat Alerts...")
    
    users = ["farmer_A", "farmer_B", "farmer_C"]
    
    for uid in users:
        print(f"\n📂 History for {uid}:")
        # Find the latest alert for this user
        alerts = list(chat_history_collection.find({"user_id": uid, "role": "assistant"}).sort("timestamp", -1).limit(1))
        
        if alerts:
            print(f"[{alerts[0]['language']}] {alerts[0]['content']}")
        else:
            print("❌ No alert found for this user.")

if __name__ == "__main__":
    verify_chat_alerts()
