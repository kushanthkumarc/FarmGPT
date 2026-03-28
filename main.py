from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import json

from config import LANGUAGES, LANGUAGE_CODES
from sarvam_api import transcribe_audio, get_llm_advisory, get_tts_audio

app = FastAPI(title="FarmGPT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/client", StaticFiles(directory="static", html=True), name="static")


@app.get("/api/languages")
def get_languages():
    return LANGUAGES

@app.post("/api/chat")
async def chat_endpoint(
    text: str = Form(None),
    audio: UploadFile = File(None),
    history: str = Form("[]"),
    language: str = Form("Hindi")
):
    try:
        chat_history = json.loads(history)
        
        # 1. Input Processing
        user_query = ""
        if audio and audio.filename:
            audio_bytes = await audio.read()
            user_query = transcribe_audio(audio_bytes)
        elif text:
            user_query = text.strip()
            
        if not user_query:
            return JSONResponse({"error": "No input provided"}, status_code=400)
            
        # 2. Contextual LLM execution in selected TARGET language
        reply = get_llm_advisory(user_query, chat_history, language)
        
        return {
            "query": user_query,
            "reply": reply
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/tts")
async def tts_endpoint(text: str = Form(...), language: str = Form("Hindi")):
    try:
        target_code = LANGUAGE_CODES.get(language, "en-IN")
        tts_base64 = get_tts_audio(text, target_code)
        if not tts_base64:
            return JSONResponse({"error": "TTS api failed to return valid audio"}, status_code=500)
            
        return {"audio_base64": tts_base64}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
