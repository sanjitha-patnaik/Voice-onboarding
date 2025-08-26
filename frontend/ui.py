# frontend/ui.py
import streamlit as st
import requests
import os
import glob
import json
from pathlib import Path

st.set_page_config(page_title="Voice Onboarding", layout="centered")

st.markdown("<h1 style='text-align: center;'>🎙️ Voice Onboarding with Alex</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Your AI twin is ready to chat.</p>", unsafe_allow_html=True)

# Resolve project root and output directories regardless of current working directory
BASE_DIR = Path(__file__).resolve().parents[1]
TRANSCRIPTS_DIR = BASE_DIR / "output" / "transcripts"
PERSONAS_DIR = BASE_DIR / "output" / "personas"

# Start Onboarding Button
if st.button("🎙️ Start Onboarding Session"):
    with st.spinner("Starting voice session... Speak to the AI. Say 'wrap up' to finish."):
        try:
            # Call backend to start the session
            response = requests.post("http://127.0.0.1:8000/start")
            if response.status_code == 200:
                st.success("✅ Onboarding complete! You can now view your results.")
            else:
                st.error(f"❌ Failed to start: {response.status_code}")
        except requests.ConnectionError:
            st.error("❌ Backend not running. Run: `uvicorn backend.main:app --reload`")

# Fetch Results Button
if st.button("📄 Get Latest Persona & Transcript"):
    with st.spinner("Fetching latest results..."):

        # Find latest transcript
        transcript_files = sorted(glob.glob(str(TRANSCRIPTS_DIR / "*.txt")), reverse=True)
        if transcript_files:
            with open(transcript_files[0], "r", encoding="utf-8") as f:
                transcript = f.read()
            st.markdown("### 📜 Conversation Transcript")
            st.text_area("", transcript, height=300)
        else:
            st.warning("No transcript found. Run an onboarding session first.")

        # Find latest persona
        persona_files = sorted(glob.glob(str(PERSONAS_DIR / "*.json")), reverse=True)
        if persona_files:
            with open(persona_files[0], "r", encoding="utf-8") as f:
                persona = json.load(f)
            st.markdown("### 🧠 Your Deep User Persona")
            st.json(persona)

            # Creative summary
            name = persona.get("name", "You")
            values = ", ".join(persona.get("values", [])[:3])
            dreams = ", ".join(persona.get("dreams", [])[:2])
            ideal_day = persona.get("ideal_day", "a day full of surprises")

            st.markdown(f"""
            <div style="background:#f0f2f6; padding:15px; border-radius:10px; font-family:monospace;">
            <strong>{name}</strong> — a person who values <em>{values}</em>, dreams of <em>{dreams}</em>, 
            and finds joy in <em>{ideal_day}</em>.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("No persona found. Run an onboarding session and say 'wrap up' to generate one.")

# Optional: Reset session state
if st.button("🔁 Reset UI"):
    st.experimental_rerun()
