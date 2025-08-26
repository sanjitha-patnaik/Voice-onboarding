# modules/llm.py
from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

class MistralBot:
    def __init__(self, model_id="llama-3.3-70b-versatile"):
        # Get API key from .env
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found in .env file. "
                "Please add it to your .env file and try again."
            )

        print("🧠 Connecting to Groq cloud LLM...")
        self.agent = Agent(
            model=Groq(
                id=model_id,
                api_key=self.api_key  # Pass key explicitly
            ),
        )
        print("✅ Connected to Groq!")

    def generate(self, prompt):
        """Generate a response from the LLM."""
        try:
            response = self.agent.run(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return "I'm having trouble thinking right now. Let's try again."
