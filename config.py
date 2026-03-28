import os
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
STT_MODEL = "saaras:v3"
LLM_MODEL = "sarvam-m"

# Maps human-readable UI names to the exact request prompt language names
LANGUAGES = {
    "English": "English",
    "Hindi (हिंदी)": "Hindi",
    "Bengali (বাংলা)": "Bengali",
    "Tamil (தமிழ்)": "Tamil",
    "Telugu (తెలుగు)": "Telugu",
    "Marathi (मराठी)": "Marathi",
    "Gujarati (ગુજરાતી)": "Gujarati",
    "Kannada (ಕನ್ನಡ)": "Kannada",
    "Malayalam (മലയാളം)": "Malayalam",
    "Punjabi (ਪੰਜਾਬੀ)": "Punjabi",
    "Odia (ଓଡ଼ିଆ)": "Odia"
}

LANGUAGE_CODES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Punjabi": "pa-IN",
    "Odia": "od-IN"
}

def get_system_prompt(output_language: str) -> str:
    return f"""You are FarmGPT, an expert agricultural advisor for Indian farmers. 
Your primary job is to provide highly actionable, practical, and clear farming advice.

CRITICAL INSTRUCTION:
You MUST respond EXCLUSIVELY in "{output_language}". 
Even if the user asks their question in a different language, or there are mixed languages, your final response MUST ONLY be written in {output_language}.
Do NOT use internal reasoning tags like <think> or output structural steps unless requested.
Format your answer elegantly using Markdown (emojis, bolding, bullet points) as if chatting on WhatsApp.
Keep it concise, friendly, and highly localized to Indian agriculture.
"""
