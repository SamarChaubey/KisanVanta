import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
OLLAMA_API_URL = "https://ollama.com"
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "gpt-oss:120b")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not set in environment")
if not DB_NAME:
    raise ValueError("DB_NAME not set in environment")
if not OLLAMA_API_KEY:
    raise ValueError("OLLAMA_API_KEY not set in environment")