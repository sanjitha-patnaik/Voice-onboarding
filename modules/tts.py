from piper import PiperVoice
import numpy as np
import sounddevice as sd
import os

class TTS:
    def __init__(self, model_path="models/piper/en_US-lessac-medium.onnx"):
        self.model_path = model_path

        if not os.path.exists(self.model_path):
            raise RuntimeError(f"❌ Model not found at {self.model_path}")

        print(f"🔊 Loading voice model from {self.model_path}...")
        self.voice = PiperVoice.load(self.model_path)
        print("✅ Voice model loaded successfully!")

    def speak(self, text):
        """Speak text using correct audio extraction from AudioChunk."""
        print(f"🤖 AI says: {text}")

        # Synthesize returns a generator of AudioChunk objects
        audio_generator = self.voice.synthesize(text)

        # List to store audio chunks
        audio_arrays = []
        sample_rate = None

        for i, chunk in enumerate(audio_generator):
            # ✅ Extract the float audio array
            float_array = chunk.audio_float_array  # This is a proper numpy array

            # Store sample rate from first chunk
            if sample_rate is None:
                sample_rate = chunk.sample_rate

            # Append to list
            audio_arrays.append(float_array)

            print(f"📦 Chunk {i}: added {len(float_array)} samples")

        # 🔔 Concatenate only if we have data
        if len(audio_arrays) == 0:
            print("❌ No audio data generated!")
            return

        # ✅ Concatenate all audio chunks
        full_audio = np.concatenate(audio_arrays)

        # 🔊 Play the audio
        print(f"🔊 Playing {len(full_audio)} total samples at {sample_rate} Hz...")
        sd.play(full_audio, samplerate=sample_rate)
        sd.wait()  # Wait until speech finishes
        print("✅ Speech complete!")
