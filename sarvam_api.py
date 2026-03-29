import os
import tempfile
import re
import json
import requests
from typing import List, Dict

from sarvamai import SarvamAI
from config import SARVAM_API_KEY, STT_MODEL, LLM_MODEL
from rag import retrieve_context
from db import get_cached_response, cache_response, save_chat
from prompts import get_formatted_prompt

client = SarvamAI(api_subscription_key=SARVAM_API_KEY) if SARVAM_API_KEY else None

def transcribe_audio(audio_bytes: bytes) -> str:
    """Takes pure raw bytes and uses Saaras:v3 to return the transcript in original language."""
    if not client:
        raise ValueError("SARVAM_API_KEY missing - configure your environment.")
        
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            response = client.speech_to_text.transcribe(
                file=f,
                model=STT_MODEL,
                mode="transcribe",
                language_code="unknown",
                input_audio_codec="webm"
            )
        transcript = getattr(response, "transcript", "")
        if not transcript:
            raise ValueError("No transcript detected.")
        return transcript.strip()
    finally:
        os.unlink(tmp_path)


def get_llm_advisory(user_query: str, history: List[Dict], target_language: str, weather: str = "Unspecified") -> str:
    """
    Core AI logic:
    1. Check Redis Cache for identical queries.
    2. RAG retrieval.
    3. Weather context integration.
    4. LLM synthesis.
    5. Save to MongoDB Atlas.
    """
    if not client:
        raise ValueError("SARVAM_API_KEY missing - configure your environment.")

    # 1. Check Redis Cache
    cached = get_cached_response(user_query, target_language)
    if cached:
        print(f"[CACHE HIT] Serving response for: {user_query}")
        return cached

    # 2. Retrieval Augmented Generation (RAG)
    rag_context = retrieve_context(user_query)

    # REFACTORED:
    # 1. System: EXPERT PERSONA + VECTOR KNOWLEDGE (Specific to this QUERY)
    system_msg = get_formatted_prompt(rag_context, target_language, weather)
    
    # 2. Assembling Message History
    messages = [{"role": "system", "content": system_msg}]
    
    # Only use the last few turns of history to keep context focused
    for old_msg in history[-6:]: 
        messages.append(old_msg)
        
    # 3. Add CURRENT USER QUERY
    messages.append({"role": "user", "content": user_query})
    
    print(f"📡 Sending Chat Context to Sarvam (Conversation turns: {len(messages)})")
    
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.1 # Low temperature for diagnostic stability
    }
    
    try:
        # Added timeout=45 to prevent hanging the UI
        response = requests.post(
            "https://api.sarvam.ai/v1/chat/completions", 
            headers=headers, 
            json=payload,
            timeout=45
        )
        response.raise_for_status()
        data = response.json()
        raw_reply = data['choices'][0]['message']['content'] or ""
        
        # 🧪 ROBUST THOUGHT STRIPPING (handles partial tags or mixed blocks)
        # 1. Strip full tags
        reply = re.sub(r'<think>.*?</think>', '', raw_reply, flags=re.DOTALL).strip()
        # 2. Strip dangling opening tag if closing is missing
        reply = re.sub(r'<think>.*', '', reply, flags=re.DOTALL).strip()
        
        print(f"DEBUG: Processed LLM Output (Len: {len(reply)}): {reply[:100]}...")
        
        if len(reply) < 5:
            print("⚠️ WARNING: LLM returned an empty response after cleaning. Using fallback.")
            reply = "I understand. I am analyzing the symptoms you mentioned. Could you also please share the approximate temperature and humidity in your area today?"

    except Exception as e:
        print(f"❌ LLM API Error: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"DEBUG: Response body: {response.text}")
        return "I apologize, but I am currently having trouble connecting to my knowledge core. Please try again or visit your local KVK."
    
    # 3. Cache the result
    cache_response(user_query, target_language, reply)
    
    # [NOTE]: save_chat removed here and moved to background tasks in main.py
    # to avoid network latency blocking the user response.

    return reply

def get_tts_audio(text: str, target_language_code: str) -> str:
    """Gets base64 audio representation of the text via Sarvam TTS API.
    Uses 'abhilash' for general voice mapping across models."""
    import requests
    if not SARVAM_API_KEY: return ""
    
    URL = "https://api.sarvam.ai/text-to-speech"
    HEADERS = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    model_selected = "aura-tts-hi-v1" if target_language_code == "hi-IN" else "bulbul:v3"
    speaker_selected = "abhilash" if model_selected == "aura-tts-hi-v1" else "aditya"
    
    payload = {
        "inputs": [text[:500]], # Clip to 500 length to avoid rate limits/delays in testing
        "target_language_code": target_language_code,
        "speaker": speaker_selected, 
        "model": model_selected
    }
    
    try:
        r = requests.post(URL, json=payload, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            if 'audios' in data: return data['audios'][0]
            if 'audio_content' in data: return data['audio_content']
        raise Exception(f"HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"TTS Error: {e}")
        raise e

if __name__ == "__main__":
    print("--- SARVAM API: LOCAL LOGIC CHECK ---")
    if not SARVAM_API_KEY:
        print("❌ Error: SARVAM_API_KEY is not set.")
    else:
        # Simple Logic Test
        try:
            test_query = "Hello, how are you?"
            print(f"1. Testing LLM Advisory logic locally for: '{test_query}'...")
            # Using empty history for a simple test
            response = get_llm_advisory(test_query, [], "English")
            print(f"✅ Success! Response preview: {response[:100]}...")
            
            print("\n2. Testing TTS logic locally...")
            tts_data = get_tts_audio("Hello from Sarvam API", "en-IN")
            if tts_data:
                print(f"✅ Success! Received {len(tts_data)} bytes of audio data.")
            else:
                print("❌ TTS failed to return audio.")
                
        except Exception as e:
            print(f"❌ Error during local check: {e}")
            import traceback
            traceback.print_exc()
    print("--- CHECK COMPLETE ---")
