"""
Flask AI Service — Main Application Entry Point
================================================
Provides the /ai/process endpoint for the React frontend.
Handles NLP processing, ingredient extraction, product matching,
and chatbot logic via the controller module.
"""

import os
import logging
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("flask-ai")

# Import controller (after env is loaded so API keys are available)
from chatbot.controller import process_message
from chatbot.session_manager import get_active_session_count

# ─── Flask App Setup ──────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, resources={
    r"/ai/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
    }
})


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/ai/process", methods=["POST"])
def ai_process():
    """
    Main AI processing endpoint.
    
    Request body:
    {
        "message": "Make butter chicken for 4 people",
        "user_id": "user-123"  (optional — auto-generated if missing)
    }
    
    Response:
    {
        "text": "Here's what you need...",
        "intent": "GET_RECIPE",
        "products": [...],
        "actions": [...],
        "show_cart": false
    }
    """
    try:
        data = request.get_json()

        if not data or not data.get("message", "").strip():
            return jsonify({
                "error": "Message is required",
                "text": "Please send a message.",
            }), 400

        message = data["message"].strip()
        user_id = data.get("user_id", f"anon-{uuid.uuid4().hex[:8]}")

        logger.info(f"Processing message from {user_id}: '{message[:80]}...'")

        # Process through chatbot controller
        response = process_message(user_id, message)

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "text": "Sorry, something went wrong. Please try again.",
            "intent": "ERROR",
            "products": [],
            "actions": [],
            "show_cart": False,
        }), 500


@app.route("/ai/health", methods=["GET"])
def health_check():
    """Health check endpoint for monitoring."""
    from ai.gemini_service import is_available

    return jsonify({
        "status": "healthy",
        "service": "flask-ai",
        "gemini_available": is_available(),
        "active_sessions": get_active_session_count(),
    }), 200


@app.route("/", methods=["GET"])
def index():
    """Root endpoint with service info."""
    return jsonify({
        "service": "Grocery AI Chatbot — Flask AI Service",
        "version": "2.0.0",
        "endpoints": {
            "POST /ai/process": "Process a chat message",
            "GET /ai/health": "Health check",
        },
    }), 200


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    logger.info(f"Starting Flask AI Service on port {port}")
    logger.info(f"Node.js backend URL: {os.getenv('NODE_BACKEND_URL', 'http://localhost:4000')}")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
    )
