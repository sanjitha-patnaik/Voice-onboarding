import time
import random
import re
from modules.stt import STT
from modules.tts import TTS
from modules.llm import MistralBot
import json


class ConversationEngine:
    def __init__(self):
        self.stt = STT()
        self.tts = TTS()
        self.llm = MistralBot()
        self.memory = []
        self.start_time = time.time()
        self.question_count = 0
        self.answered_core = set()

        # Load prompts and configs
        with open("prompts/question_bank.json", "r", encoding="utf-8") as f:
            self.questions = json.load(f)

        with open("prompts/system_prompt.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

        with open("prompts/humor_templates.txt", "r", encoding="utf-8") as f:
            self.humor_templates = self._parse_humor_sections(f.read())

    def _parse_humor_sections(self, content: str) -> dict:
        """Parse humor_templates.txt into labeled sections."""
        sections = {}
        current_section = None
        for line in content.splitlines():
            if line.startswith("#") and not line.startswith("##"):
                if "—" in line or "RULES" in line:
                    continue
                # New section header like "1. Playful Teasing"
                match = re.search(r"\d+\.\s*([^#]+)", line)
                if match:
                    current_section = match.group(1).strip()
                    sections[current_section] = []
            elif line.strip().startswith('"') and current_section:
                sections[current_section].append(line.strip().strip('"'))
        return sections

    def _get_relevant_humor_hint(self, user_text: str) -> str:
        """Select a humor style and example based on user input."""
        user_text = user_text.lower()

        # Keyword-based routing to humor style
        if any(w in user_text for w in ["hate mornings", "can't wake up", "coffee first", "not a morning person"]):
            return random.choice(self.humor_templates.get("Playful Teasing", [""]))
        elif any(w in user_text for w in ["simple life", "minimalist", "declutter", "less is more"]):
            return random.choice(self.humor_templates.get("Dry / Sarcastic", [""]))
        elif any(w in user_text for w in ["absurd", "silly", "doesn't make sense", "just for fun"]):
            return random.choice(self.humor_templates.get("Absurd / Whimsical", [""]))
        elif any(w in user_text for w in ["baking", "hiking", "photography", "guitar"]):
            return random.choice(self.humor_templates.get("Puns & Wordplay", [""]))
        elif "?" in user_text and len(user_text) > 50:
            # Deep or philosophical question
            return random.choice(self.humor_templates.get("Meta / AI Self-Awareness", [""]))

        # Default: if user is funny, respond in kind
        if any(phrase in user_text for phrase in ["just kidding", "lol", "only half serious", "tongue in cheek"]):
            return random.choice([s for sec in self.humor_templates.values() for s in sec])

        return ""

    def get_context_prompt(self):
        # Get recent conversation history
        history = "\n".join([f"User: {u}\nAI: {a}" for u, a in self.memory[-5:]])

        # Get humor hint based on latest user input
        last_user = self.memory[-1][0] if self.memory else ""
        humor_hint = self._get_relevant_humor_hint(last_user)

        # Build full prompt
        prompt_parts = [self.system_prompt]

        if humor_hint:
            prompt_parts.append(f"\n# HUMOR GUIDANCE\nWhen appropriate, respond with a tone like this:\n\"{humor_hint}\"")

        prompt_parts.append(f"\nConversation so far:\n{history}\nUser:")

        return "\n".join(prompt_parts)

    def should_ask_personalized(self):
        recent = " ".join([m[0] for m in self.memory[-3:]]).lower()
        for q in self.questions:
            if q["type"] == "personalized" and q["trigger"] in recent and q["question"] not in self.answered_core:
                return q["question"]
        return None

    def run(self):
        self.tts.speak("Hey there! I'm Alex — your witty onboarding buddy. Ready to dive into a fun, 40-minute chat to build your personal AI twin? No pressure, just vibes. Let's go!")

        while self.duration() < 40 * 60 or self.question_count < 15:
            # Listen
            user_text = self.stt.transcribe()
            if not user_text:
                continue

            self.memory.append((user_text, ""))

            # Generate prompt (now with humor!)
            prompt = self.get_context_prompt()

            # Check for personalized question
            p_q = self.should_ask_personalized()
            if p_q and random.random() < 0.7:
                ai_response = p_q
            else:
                ai_response = self.llm.generate(prompt)

            # Speak
            self.tts.speak(ai_response)
            self.memory[-1] = (user_text, ai_response)
            self.question_count += 1

            # Check exit cue
            if any(word in user_text.lower() for word in ["wrap up", "done", "finish", "that's enough", "ready to stop"]):
                break

            time.sleep(1)

        self.tts.speak("That was awesome! Let me generate your deep user persona now.")
        return self.get_transcript()

    def duration(self):
        return time.time() - self.start_time

    def get_transcript(self):
        return "\n".join([f"User: {u}\nAI: {a}" for u, a in self.memory])
