from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from config import MONGODB_URI, DB_NAME

_client = None
_db = None

COLLECTIONS = [
    "users",
    "procurement_centres",
    "booking_slots",
    "slot_requests",
    "procurement_records",
    "centre_status",
    "simulations",
    "financial_exposure",
    "notifications",
    "risk_snapshots",
]


def get_client():
    global _client
    if _client is None:
        try:
            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        except ConfigurationError:
            raise ConnectionError("MongoDB configuration error. Check setup.")
    return _client


def get_db():
    global _db
    if _db is None:
        client = get_client()
        _db = client[DB_NAME] # type: ignore
    return _db


def get_collection(name):
    if name not in COLLECTIONS:
        raise ValueError(f"Unknown collection: {name}")
    return get_db()[name]


def test_connection():
    try:
        client = get_client()
        client.admin.command("ping")
        return True, "MongoDB connection successful"
    except ConnectionFailure:
        return False, "MongoDB connection failed"
    except Exception:
        return False, "MongoDB connection failed"