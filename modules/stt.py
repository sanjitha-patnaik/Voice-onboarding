import whisper
import numpy as np
import sounddevice as sd

class STT:
    def __init__(self, model="small"):
        print("🧠 Loading Whisper STT model...")
        self.model = whisper.load_model(model)
        print("✅ Whisper model loaded!")

    def listen(self, duration=8, sample_rate=16000):
        print("🎤 Listening...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()

        # Whisper expects 16kHz mono
        audio = audio.squeeze()

        # Transcribe (disable fp16 on CPU)
        result = self.model.transcribe(audio, fp16=False)
        text = result["text"].strip()

        if text:
            print(f"🧑‍🦰 You said: {text}")
        else:
            print("🔇 I didn't catch that.")

        return text
