import requests
from config import OLLAMA_API_URL, OLLAMA_API_KEY, OLLAMA_CHAT_MODEL

HEADERS = {
    "Authorization": f"Bearer {OLLAMA_API_KEY}",
    "Content-Type": "application/json"
}


def generate_answer(prompt):
    resp = requests.post(
        f"{OLLAMA_API_URL}/api/chat",
        headers=HEADERS,
        json={
            "model": OLLAMA_CHAT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=60
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]