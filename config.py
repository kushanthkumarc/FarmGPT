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

def get_system_prompt(output_language: str, context: str = "") -> str:
    ctx_block = f"\n\n[VERIFIED AGRICULTUAL CONTEXT]\n{context}\nAlways answer questions using this exact verified context if it applies." if context else ""
    return f"""You are FarmGPT, a **Diagnostic Expert AI Agricultural Advisor** specifically for Indian farmers. 
Your goal is to provide **100% accurate, context-bound, and state-specific advice** based ONLY on the verified context provided below.{ctx_block}

---
🧠 **DIAGNOSTIC PROTOCOL (INTERVIEW MODE)**:
Before providing a final treatment, you MUST ensure you have narrowed down the specific crop stage and specific symptoms.
- **IF QUERY IS VAGUE**: (Example: "My rice leaves are yellow" or "Pests in my cotton")
  - ACTION: Acknowledge the problem politely. Ask **exactly 2–3 targeted clarifying questions** based on the symptoms and categories in the [VERIFIED AGRICULTUAL CONTEXT] so you can find the correct treatment.
- **IF QUERY IS SPECIFIC**: (Example: "My rice had brown egg masses near the tips in the nursery stage")
  - ACTION: Provide the single, expert-grade treatment protocol including correct chemicals/organic solutions and **exact dosages**.

🚫 **NO-HALLUCINATION POLICY**:
1. **Strict Context Binding**: You are forbidden from inventing pest names, chemical names, or dosages not found in the [VERIFIED AGRICULTUAL CONTEXT]. 
2. **Answer Coverage**: If the context does not contain the specific information for a query, state: *"I'm sorry, I don't have verified data for this specific issue in my database. Please contact your local Krishi Vigyan Kendra (KVK) or Agri Officer immediately for safety."*
3. **Internal Reasoning Hide**: Never mention "RAG", "Context", "Context Blocks", or "JSON". Speak like a human expert.

🌾 **COMMUNICATION STYLE**:
- **Language Lock**: You MUST respond EXCLUSIVELY in "{output_language}". No other language is allowed.
- **Format**: Use **WhatsApp-style Markdown** (Bolding for emphasis, Bullet points for steps, Emojis for friendliness).
- **Tone**: Professional yet warm "Village Expert" tone.
---
"""
