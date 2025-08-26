import time
import os
import json
from typing import Generator
from modules.stt import STT
from modules.tts import TTS
from modules.llm import MistralBot
from modules.persona_builder import PersonaBuilder
from modules.utils import generate_session_id, save_json

class OnboardingSession:
    def __init__(self):
        self.transcript = []
        self.is_running = False
        self.session_id = generate_session_id()

        # Paths
        self.transcript_path = f"output/transcripts/session_{self.session_id}.txt"
        self.persona_path = f"output/personas/user_{self.session_id}.json"

        # Initialize voice components
        self.tts = TTS()
        self.stt = STT(model="small")
        self.llm = MistralBot()

        # Load prompt
        with open("prompts/system_prompt.txt", "r") as f:
            self.system_prompt = f.read()

        # Exit phrases
        self.exit_phrases = [
            "wrap up", "done", "finish", "stop", "goodbye", "bye", "thank you", "thanks",
            "that's all", "i'm done", "end session", "see you", "take care"
        ]

    def run(self) -> Generator[str, None, None]:
        """Run the onboarding and yield events in real-time."""
        self.is_running = True
        start_time = time.time()

        # Intro
        self.tts.speak("Hey there! I'm Alex — your witty onboarding buddy. Ready for a fun 40-minute chat to build your AI twin? Just say 'start' when you're ready.")
        yield "AI: Hey there! I'm Alex — your witty onboarding buddy..."

        # Wait for start
        user_ready = self.stt.listen(duration=10)
        if "no" in user_ready.lower():
            self.tts.speak("No worries! Restart me when you're ready.")
            yield "AI: No worries! Restart me when you're ready."
            self.is_running = False
            return

        self.tts.speak("Awesome! Let's begin.")
        yield "AI: Awesome! Let's begin."

        # Main loop
        while self.is_running:
            if (time.time() - start_time) > 60 * 60:  # Max 60 mins
                self.tts.speak("We've been chatting for a while — let me wrap up and build your AI twin.")
                yield "AI: Session complete. Generating your persona..."
                break

            # Listen
            user_text = self.stt.listen(duration=15)
            if not user_text.strip():
                continue

            self.transcript.append(f"User: {user_text}")
            yield f"USER: {user_text}"

            # Check exit
            if any(phrase in user_text.lower() for phrase in self.exit_phrases):
                self.tts.speak("Got it! Thanks for such a great conversation. Let me generate your deep user persona now.")
                yield "AI: Got it! Thanks for such a great conversation..."
                break

            # Generate AI response
            history = "\n".join(self.transcript[-6:])
            prompt = f"{self.system_prompt}\n\n{history}\nAI:"
            ai_response = self.llm.generate(prompt)
            self.transcript.append(f"AI: {ai_response}")

            # Speak
            self.tts.speak(ai_response)
            yield f"AI: {ai_response}"

            time.sleep(0.5)

        # Finalize
        self.tts.speak("That was awesome! Let me build your deep user persona now.")
        yield "AI: Building your deep user persona..."

        # Save transcript
        os.makedirs(os.path.dirname(self.transcript_path), exist_ok=True)
        with open(self.transcript_path, "w") as f:
            f.write("\n".join(self.transcript))

        # Build persona
        builder = PersonaBuilder()
        persona = builder.build("\n".join(self.transcript))
        save_json(persona, self.persona_path)

        self.is_running = False
        self.tts.speak("Onboarding complete! Your AI twin now understands you deeply. Welcome aboard!")
        yield f"PERSONA: {json.dumps(persona)}"
        yield "DONE"