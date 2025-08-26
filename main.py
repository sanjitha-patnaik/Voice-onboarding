from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import sys, os
from onboarding import OnboardingSession
import json


app = FastAPI(title="Voice Onboarding API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

session: OnboardingSession = None

@app.get("/")
def home():
    return {"message": "🎙️ Voice Onboarding Backend Running!"}

@app.post("/start")
def start_onboarding():
    global session
    if session and session.is_running:
        raise HTTPException(status_code=400, detail="Session already in progress")
    
    session = OnboardingSession()
    return EventSourceResponse(
        session.run(),
        media_type="text/plain"
    )

@app.get("/persona/latest")
def get_latest_persona():
    persona_dir = "output/personas"
    if not os.path.exists(persona_dir):
        raise HTTPException(status_code=404, detail="No personas found")
    
    files = sorted([f for f in os.listdir(persona_dir) if f.endswith(".json")])
    if not files:
        raise HTTPException(status_code=404, detail="No persona generated yet")
    
    latest = files[-1]
    with open(f"{persona_dir}/{latest}", "r") as f:
        return json.load(f)

@app.get("/status")
def get_status():
    return {"running": session.is_running if session else False}