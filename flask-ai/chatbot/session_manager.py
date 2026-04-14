"""
Session Manager Module
======================
Manages per-user conversational context using an in-memory store.
Structure is Redis-ready — can be swapped to Redis by changing the storage backend.
"""

import time
import logging
import threading

logger = logging.getLogger(__name__)

# ─── Session Configuration ────────────────────────────────────────────────────
SESSION_TTL_SECONDS = 1800  # 30 minutes
CLEANUP_INTERVAL_SECONDS = 300  # Run cleanup every 5 minutes
MAX_CONVERSATION_HISTORY = 20  # Keep last 20 messages per session

# ─── In-Memory Session Store ──────────────────────────────────────────────────
# Redis-ready structure: each session is a flat dict suitable for Redis HSET
_sessions = {}
_lock = threading.Lock()


def _new_session():
    """Create a fresh session object with default values."""
    return {
        "last_intent": None,
        "last_dish": None,
        "suggested_products": [],      # Products shown to the user
        "pending_cart_items": [],       # Items ready to be added to cart
        "conversation_history": [],     # List of {role, message, timestamp}
        "last_activity": time.time(),
        "created_at": time.time(),
    }


def get_session(user_id):
    """
    Get or create a session for a user.
    
    Args:
        user_id: Unique user identifier (string).
    
    Returns:
        dict: The user's session data.
    """
    with _lock:
        if user_id not in _sessions:
            _sessions[user_id] = _new_session()
            logger.info(f"Created new session for user: {user_id}")
        
        session = _sessions[user_id]
        session["last_activity"] = time.time()
        return session


def update_session(user_id, data):
    """
    Update specific fields in a user's session.
    
    Args:
        user_id: Unique user identifier.
        data: Dict of fields to update.
    """
    with _lock:
        if user_id not in _sessions:
            _sessions[user_id] = _new_session()

        session = _sessions[user_id]
        session["last_activity"] = time.time()

        for key, value in data.items():
            if key in session:
                session[key] = value
            else:
                logger.warning(f"Unknown session field: {key}")


def add_to_conversation(user_id, role, message):
    """
    Add a message to the conversation history.
    
    Args:
        user_id: Unique user identifier.
        role: "user" or "bot".
        message: The message text.
    """
    with _lock:
        if user_id not in _sessions:
            _sessions[user_id] = _new_session()

        session = _sessions[user_id]
        session["last_activity"] = time.time()

        session["conversation_history"].append({
            "role": role,
            "message": message,
            "timestamp": time.time(),
        })

        # Trim history to prevent memory bloat
        if len(session["conversation_history"]) > MAX_CONVERSATION_HISTORY:
            session["conversation_history"] = session["conversation_history"][-MAX_CONVERSATION_HISTORY:]


def set_suggested_products(user_id, products):
    """
    Store the list of products suggested to the user.
    These become the candidates when the user says "add all".
    
    Args:
        user_id: Unique user identifier.
        products: List of product dicts to store.
    """
    update_session(user_id, {"suggested_products": products})


def set_pending_cart_items(user_id, items):
    """
    Store items that are pending to be added to cart.
    
    Args:
        user_id: Unique user identifier.
        items: List of cart item dicts.
    """
    update_session(user_id, {"pending_cart_items": items})


def clear_session(user_id):
    """
    Clear a user's session completely.
    
    Args:
        user_id: Unique user identifier.
    """
    with _lock:
        if user_id in _sessions:
            del _sessions[user_id]
            logger.info(f"Cleared session for user: {user_id}")


def get_session_context(user_id):
    """
    Get a summary of the session context for use in Gemini prompts.
    Returns a lighter version of the session suitable for AI context.
    
    Args:
        user_id: Unique user identifier.
    
    Returns:
        dict: Simplified context data.
    """
    session = get_session(user_id)
    return {
        "last_intent": session.get("last_intent"),
        "last_dish": session.get("last_dish"),
        "suggested_products": session.get("suggested_products", [])[:5],
        "pending_cart_items": session.get("pending_cart_items", [])[:5],
    }


def cleanup_expired_sessions():
    """Remove sessions that have been inactive for longer than TTL."""
    with _lock:
        now = time.time()
        expired = [
            uid for uid, session in _sessions.items()
            if (now - session.get("last_activity", 0)) > SESSION_TTL_SECONDS
        ]

        for uid in expired:
            del _sessions[uid]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")


def get_active_session_count():
    """Return the number of active sessions (for monitoring)."""
    with _lock:
        return len(_sessions)


# ─── Background Cleanup Thread ────────────────────────────────────────────────
def _start_cleanup_thread():
    """Start a daemon thread that periodically cleans up expired sessions."""
    def cleanup_loop():
        while True:
            time.sleep(CLEANUP_INTERVAL_SECONDS)
            try:
                cleanup_expired_sessions()
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")

    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    logger.info("Session cleanup thread started")


# Start cleanup on module load
_start_cleanup_thread()
