import firebase_admin
import os

from dotenv import load_dotenv
from firebase_admin import credentials, db
from typing import Any, Dict, Optional


load_dotenv()

# --- Firebase Initialization ---

try:
    cred = credentials.Certificate(os.getenv("DATABASE_ACCOUNT_FILE"))
    firebase_admin.initialize_app(
        cred,
        {"databaseURL": os.getenv("DATABASE_URL")}
    )
except Exception as e:
    print(f"[DB INIT ERROR] Failed to initialize Firebase: {e}")


# --- Core CRUD operations ---
def add_data(ref: str, key: str | int, data: Dict[str, Any]) -> bool:
    """Add new data to the given reference path."""
    try:
        db.reference(ref).child(str(key)).set(data)
        return True
    except Exception as e:
        print(f"[DB ERROR:add_data] {e}")
        return False


def get_data(ref: str, key: str | int) -> Optional[Dict[str, Any]]:
    """Retrieve data from a specific document (by key)."""
    try:
        data = db.reference(f"{ref}/{key}").get()
        return data
    except Exception as e:
        print(f"[DB ERROR:get_data] {e}")
        return None


def update_data(ref: str, key: str | int, updates: Dict[str, Any]) -> bool:
    """Update specific fields in a document."""
    try:
        db.reference(f"{ref}/{key}").update(updates)
        return True
    except Exception as e:
        print(f"[DB ERROR:update_data] {e}")
        return False


def delete_data(ref: str, key: str | int) -> bool:
    """Delete document by key."""
    try:
        db.reference(f"{ref}/{key}").delete()
        return True
    except Exception as e:
        print(f"[DB ERROR:delete_data] {e}")
        return False


def get_all(ref: str) -> Dict[str, Any]:
    """Return all data from a given reference (collection)."""
    try:
        data = db.reference(ref).get()
        return data or {}
    except Exception as e:
        print(f"[DB ERROR:get_all] {e}")
        return {}


# --- Helpers ---
def exists(ref: str, key: str | int) -> bool:
    """Check if a document exists."""
    try:
        snapshot = db.reference(f"{ref}/{key}").get()
        return snapshot is not None
    except Exception as e:
        print(f"[DB ERROR:exists] {e}")
        return False


def push_data(ref: str, data: Dict[str, Any]) -> Optional[str]:
    """Push new data with auto-generated key."""
    try:
        new_ref = db.reference(ref).push(data)
        return new_ref.key
    except Exception as e:
        print(f"[DB ERROR:push_data] {e}")
        return None