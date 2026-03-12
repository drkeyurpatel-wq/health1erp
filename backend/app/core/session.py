"""Session management and token blacklisting.

Provides:
- Token blacklist (in-memory with Redis upgrade path)
- Active session tracking per user
- Forced logout / session revocation
- Concurrent session limits (max 5 per user)
"""
import time
import logging
from collections import defaultdict
from typing import Optional

logger = logging.getLogger("health1erp.session")

MAX_SESSIONS_PER_USER = 5


class TokenBlacklist:
    """In-memory token blacklist with TTL-based auto-cleanup.

    In production, replace with Redis SET with TTL for persistence across restarts.
    """

    def __init__(self):
        # token_jti -> expiry timestamp
        self._blacklisted: dict[str, float] = {}
        self._cleanup_counter = 0

    def revoke(self, token_jti: str, expires_at: float):
        """Add a token to the blacklist."""
        self._blacklisted[token_jti] = expires_at
        self._maybe_cleanup()

    def is_revoked(self, token_jti: str) -> bool:
        """Check if a token has been revoked."""
        if token_jti in self._blacklisted:
            # Still valid blacklist entry?
            if self._blacklisted[token_jti] > time.time():
                return True
            # Expired — clean it up
            del self._blacklisted[token_jti]
        return False

    def _maybe_cleanup(self):
        self._cleanup_counter += 1
        if self._cleanup_counter >= 500:
            now = time.time()
            self._blacklisted = {k: v for k, v in self._blacklisted.items() if v > now}
            self._cleanup_counter = 0


class SessionManager:
    """Track active sessions per user."""

    def __init__(self):
        # user_id -> list of {session_id, token_jti, created_at, ip, user_agent, last_active}
        self._sessions: dict[str, list[dict]] = defaultdict(list)

    def register_session(
        self,
        user_id: str,
        token_jti: str,
        ip: str = "",
        user_agent: str = "",
    ) -> Optional[str]:
        """Register a new session. Returns evicted session JTI if over limit."""
        sessions = self._sessions[user_id]

        # Clean expired sessions
        now = time.time()
        sessions[:] = [s for s in sessions if s.get("expires_at", 0) > now]

        evicted_jti = None

        # Enforce concurrent session limit
        if len(sessions) >= MAX_SESSIONS_PER_USER:
            # Evict oldest session
            oldest = min(sessions, key=lambda s: s["created_at"])
            evicted_jti = oldest["token_jti"]
            sessions.remove(oldest)
            logger.info(f"Session evicted for user {user_id} — concurrent limit reached")

        sessions.append({
            "token_jti": token_jti,
            "created_at": now,
            "last_active": now,
            "ip": ip,
            "user_agent": user_agent[:200],
            "expires_at": now + 7 * 86400,  # 7 days max
        })
        return evicted_jti

    def get_active_sessions(self, user_id: str) -> list[dict]:
        """Get all active sessions for a user."""
        now = time.time()
        sessions = self._sessions.get(user_id, [])
        return [
            {
                "token_jti": s["token_jti"],
                "created_at": s["created_at"],
                "last_active": s["last_active"],
                "ip": s["ip"],
                "user_agent": s["user_agent"],
            }
            for s in sessions if s.get("expires_at", 0) > now
        ]

    def revoke_session(self, user_id: str, token_jti: str) -> bool:
        """Revoke a specific session."""
        sessions = self._sessions.get(user_id, [])
        for s in sessions:
            if s["token_jti"] == token_jti:
                sessions.remove(s)
                return True
        return False

    def revoke_all_sessions(self, user_id: str) -> list[str]:
        """Revoke all sessions for a user. Returns list of revoked JTIs."""
        sessions = self._sessions.pop(user_id, [])
        return [s["token_jti"] for s in sessions]

    def touch(self, user_id: str, token_jti: str):
        """Update last_active timestamp for a session."""
        for s in self._sessions.get(user_id, []):
            if s["token_jti"] == token_jti:
                s["last_active"] = time.time()
                break


# Singleton instances
token_blacklist = TokenBlacklist()
session_manager = SessionManager()
