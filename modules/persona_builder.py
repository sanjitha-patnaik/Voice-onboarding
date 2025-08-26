from modules.llm import MistralBot
import json

# config/persona_schema.json
persona_schema = {
    "title": "UserPersona",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "values": {"type": "array", "items": {"type": "string"}},
        "goals": {"type": "array", "items": {"type": "string"}},
        "hobbies": {"type": "array", "items": {"type": "string"}},
        "lifestyle": {"type": "string"},
        "relationships": {"type": "string"},
        "struggles": {"type": "array", "items": {"type": "string"}},
        "dreams": {"type": "array", "items": {"type": "string"}},
        "humor_style": {"type": "string"},
        "decision_making": {"type": "string"},
        "ideal_day": {"type": "string"}
    },
    "required": ["values", "goals", "hobbies"]
}

class PersonaBuilder:
    def __init__(self):
        self.llm = MistralBot()

    def build(self, transcript):
        prompt = f"""
        Based on the following conversation, extract a deep user persona in JSON format.
        Use this schema:
        {json.dumps(persona_schema, indent=2)}

        Rules:
        - Only use info from the transcript.
        - Be concise but insightful.
        - Infer values, dreams, struggles from tone and content.

        Transcript:
        {transcript}

        Output only valid JSON:
        """

        raw = self.llm.generate(prompt)
        #print("raw",raw)
        try:
            persona = json.loads(raw)
            #print("persona",persona)
            return persona
        except:
            # Fallback cleaning
            import re
            json_str = re.search(r"\{.*\}", raw, re.DOTALL)
            if json_str:
                return json.loads(json_str.group())
            return {"error": "Could not parse persona", "raw": raw}
