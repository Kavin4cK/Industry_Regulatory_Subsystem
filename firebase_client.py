"""
firebase_client.py — Firebase Realtime Database wrapper.
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

    def push(self, node: str, data: dict):
        """Push a new timestamped entry under the given node."""
        if not self._available:
            log.info(f"[LOCAL] {data}")
            return None
        try:
            ref = firebase_db.reference(node)
            new_ref = ref.push(data)
            log.debug(f"Firebase push OK → /{node}/{new_ref.key}")
            return new_ref.key
        except Exception as e:
            log.error(f"Firebase push failed: {e}")
            return None