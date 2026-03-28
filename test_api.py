import requests

URL = "http://localhost:8000/api/chat"
payload = {
    "text": "What is the best time to grow wheat?",
    "language": "Hindi",
    "history": "[]"
}

print("Sending request to FarmGPT API...")
try:
    response = requests.post(URL, data=payload)
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print("Query:", data.get("query"))
        print("Reply Snippet:", data.get("reply")[:100], "...")
        audio = data.get("audio_base64", "")
        if audio:
            print(f"✅ TTS Audio Base64 received! Length: {len(audio)}")
        else:
            print("❌ TTS Audio missing in response.")
    else:
        print(f"❌ API Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")
