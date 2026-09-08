import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI not set in environment")
if not DB_NAME:
    raise ValueError("DB_NAME not set in environment")