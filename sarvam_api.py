import os
import tempfile
import re
from typing import List, Dict

from sarvamai import SarvamAI
from config import SARVAM_API_KEY, STT_MODEL, LLM_MODEL, get_system_prompt

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


def get_llm_advisory(user_query: str, history: List[Dict], target_language: str) -> str:
    """Gets the LLM advice strictly bound to target_language."""
    if not client:
        raise ValueError("SARVAM_API_KEY missing - configure your environment.")

    # Apply strict language control
    system_prompt = get_system_prompt(target_language)
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-6:])  # last 3 turns
    messages.append({"role": "user", "content": user_query})

    response = client.chat.completions(
        model=LLM_MODEL,
        messages=messages,
    )
    
    reply = response.choices[0].message.content or ""
    
    # Clean reasoning tags if any
    reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL).strip()
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
