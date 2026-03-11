"""
firebase_client.py — Firebase Realtime Database wrapper.
Uses set() to overwrite a single node (no push, no history).
"""

import logging

try:
    import firebase_admin
    from firebase_admin import credentials, db as firebase_db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

log = logging.getLogger(__name__)


class FirebaseClient:
    def __init__(self, credentials_path: str, database_url: str):
        self._available = False

        if not FIREBASE_AVAILABLE:
            log.warning("firebase-admin not installed — data printed locally only.")
            return

        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred, {"databaseURL": database_url})
            self._available = True
            log.info("Firebase Realtime Database connected.")
        except Exception as e:
            log.error(f"Firebase init failed: {e}")

    def set(self, node: str, data: dict):
        """Overwrite the node entirely with new data every cycle."""
        if not self._available:
            log.info(f"[LOCAL] {data}")
            return
        try:
            firebase_db.reference(node).set(data)
        except Exception as e:
            log.error(f"Firebase set failed: {e}")

    def push(self, node: str, data: dict):
        """Keep push available if needed later."""
        if not self._available:
            log.info(f"[LOCAL] {data}")
            return
        try:
            firebase_db.reference(node).push(data)
        except Exception as e:
            log.error(f"Firebase push failed: {e}")