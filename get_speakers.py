import requests
import sys
from config import SARVAM_API_KEY

URL = 'https://api.sarvam.ai/text-to-speech'
HEADERS = {
    'api-subscription-key': SARVAM_API_KEY,
    'Content-Type': 'application/json'
}
payload = {
    'inputs': ['नमस्ते'],
    'target_language_code': 'hi-IN',
    'speaker': 'invalid_speaker_name',
    'pitch': 0,
    'pace': 1.0,
    'loudness': 1.5,
    'speech_sample_rate': 8000,
    'enable_preprocessing': True,
    'model': 'aura-tts-hi-v1'
}
r = requests.post(URL, json=payload, headers=HEADERS)
data = r.json()
print("FULL ERROR MESSAGE FROM TTS:")
print(data)
