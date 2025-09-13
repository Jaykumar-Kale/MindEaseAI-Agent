import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import requests

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

openai.api_key = OPENAI_KEY

app = FastAPI(title="MindEaseAI-Agent (Prototype)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RISK_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die", "i will die",
    "hurt myself", "no reason to live"
]
HELPLINES = {
    "IN": {"Tele-MANAS": "14416", "KIRAN": "1800-599-0019"},
    "GLOBAL_EMERGENCY": {"Emergency": "Local emergency services"}
}

def risk_score(text: str) -> int:
    s = text.lower()
    score = 0
    for k in RISK_KEYWORDS:
        if k in s:
            score += 2
    return score

class TextRequest(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/respond")
async def respond(req: TextRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text required")

    score = risk_score(text)
    if score >= 2:
        helplines = HELPLINES.get("IN", {})
        hl = "; ".join([f"{n}: {num}" for n, num in helplines.items()])
        safe_msg = (
            "I'm really sorry you're feeling this way. If you are in immediate danger, please contact local emergency services. "
            f"Here are local helplines you can call: {hl}. Would you like me to connect you to a human counselor?"
        )
        return JSONResponse({"reply": safe_msg, "risk": True})

    system_prompt = (
        "You are MindEaseAI, an empathetic mental-health assistant. "
        "Always be non-judgemental, validate feelings, offer short practical coping steps (breathing, grounding, distraction), "
        "do NOT give medical diagnoses or prescribe medication. Suggest seeing a professional when appropriate."
    )

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            max_tokens=400,
            temperature=0.7
        )
        reply = resp.choices[0].message.content.strip()
    except Exception as e:
        print("LLM error:", e)
        reply = "Sorry, I'm having trouble right now. Can you try again in a moment?"

    return {"reply": reply, "risk": False}

@app.post("/tts")
def tts(payload: TextRequest):
    text = payload.text
    if not ELEVEN_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs API key not configured")

    voice = DEFAULT_VOICE
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    body = {"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.6}}
    resp = requests.post(tts_url, headers=headers, json=body, stream=True)

    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"ElevenLabs TTS failed: {resp.status_code} {resp.text}")

    return StreamingResponse(resp.iter_content(chunk_size=1024), media_type="audio/mpeg")
