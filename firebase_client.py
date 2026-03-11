"""
firebase_client.py — Uses REST API with Database Secret.
No JWT, no clock sync issues.
"""

import logging
import json
import urllib.request
import urllib.parse

log = logging.getLogger(__name__)


class FirebaseClient:
    def __init__(self, credentials_path: str, database_url: str):
        self._db_url = database_url.rstrip("/")
        self._secret = None

        try:
            with open(credentials_path) as f:
                data = json.load(f)
                self._secret = data.get("database_secret")
            if self._secret:
                log.info("Firebase REST client ready.")
            else:
                log.error("No 'database_secret' found in credentials file.")
        except Exception as e:
            log.error(f"Firebase init failed: {e}")

    def set(self, node: str, data: dict):
        if not self._secret:
            log.info(f"[LOCAL] {data}")
            return
        try:
            url = f"{self._db_url}/{node}.json?auth={self._secret}"
            body = json.dumps(data).encode("utf-8")
            req  = urllib.request.Request(url, data=body, method="PUT")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=5) as resp:
                log.debug(f"Firebase set OK: {resp.status}")
        except Exception as e:
            log.error(f"Firebase set failed: {e}")

    def push(self, node: str, data: dict):
        if not self._secret:
            log.info(f"[LOCAL] {data}")
            return
        try:
            url  = f"{self._db_url}/{node}.json?auth={self._secret}"
            body = json.dumps(data).encode("utf-8")
            req  = urllib.request.Request(url, data=body, method="POST")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req, timeout=5) as resp:
                log.debug(f"Firebase push OK: {resp.status}")
        except Exception as e:
            log.error(f"Firebase push failed: {e}")
