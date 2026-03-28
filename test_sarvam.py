import os
import io
import time
import base64
from config import SARVAM_API_KEY
from sarvamai import SarvamAI

def run_checks():
    print("--- SARVAM AI CAPABILITY CHECK ---")
    if not SARVAM_API_KEY:
        print("❌ Error: SARVAM_API_KEY is not set.")
        return

    client = SarvamAI(api_subscription_key=SARVAM_API_KEY)

    # 1. Test LLM
    print("1. Testing LLM (Chat Completions)...")
    try:
        t0 = time.time()
        r = client.chat.completions(
            model="sarvam-m", 
            messages=[{"role": "user", "content": "Say 'hello' in Hindi"}]
        )
        reply = getattr(r.choices[0].message, "content", r.choices[0].message)
        print(f"   ✅ LLM working. Reply: {str(reply)[:30]}... ({time.time()-t0:.2f}s)")
    except Exception as e:
        print(f"   ❌ LLM failed: {e}")

    # 2. Test TTS
    print("\n2. Testing TTS (Text-to-Speech)...")
    try:
        t0 = time.time()
        # the SDK defines client.text_to_speech.synthesize or we can use requests
        import requests
        URL = "https://api.sarvam.ai/text-to-speech"
        HEADERS = {
            "api-subscription-key": SARVAM_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": ["नमस्ते, आप कैसे हैं?"],
            "target_language_code": "hi-IN",
            "speaker": "meera",
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": "aura-tts-hi-v1" 
        }
        response = requests.post(URL, json=payload, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            # If audios field is present (Aura TTS format)
            if 'audios' in data:
                audio_str = data['audios'][0]
                print(f"   ✅ TTS working (Aura format). Returned {len(audio_str)} chars of base64 audio. ({time.time()-t0:.2f}s)")
            elif 'audio_content' in data:
                print(f"   ✅ TTS working. Returned base64 audio. ({time.time()-t0:.2f}s)")
            else:
                print(f"   ❌ TTS missing audio field: {data.keys()}")
        else:
            print(f"   ❌ TTS failed with {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ TTS Exception: {e}")

    print("\n--- CHECK COMPLETE ---")

if __name__ == "__main__":
    run_checks()
