import os
from datetime import datetime

def generate_session_id():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        import json
        json.dump(data, f, indent=2, ensure_ascii=False)
