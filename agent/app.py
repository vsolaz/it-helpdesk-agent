"""Flask entry point for the IT Helpdesk Agent API."""
import logging
import logging.config
import os
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from agent.graph import run_turn
from agent.session_repository import SessionRepository

# Structured logging setup
logging.config.dictConfig({
    "version": 1,
    "formatters": {
        "default": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "default"}
    },
    "root": {"level": "INFO", "handlers": ["console"]},
})

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurable CORS origins
_cors_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:4200").split(",")]
CORS(app, origins=_cors_origins)

_repository = SessionRepository()

_MAX_MESSAGE_LENGTH = 2000
_HTML_RE = re.compile(r"<[^>]+>")


def _sanitize(text: str) -> str:
    """Strip HTML tags and truncate to max length."""
    return _HTML_RE.sub("", text).strip()[:_MAX_MESSAGE_LENGTH]


@app.post("/invoke")
def invoke():
    """Handle a conversation turn."""
    try:
        body = request.get_json(silent=True) or {}
        session_id = body.get("session_id", "").strip()
        message = _sanitize(body.get("message", ""))

        if not session_id:
            return jsonify({"error": "Missing required field: session_id"}), 400
        if not message:
            return jsonify({"error": "Missing required field: message"}), 400

        logger.info("Invoke session=%s message_len=%d", session_id, len(message))
        reply = run_turn(session_id=session_id, user_message=message, repository=_repository)
        return jsonify({"session_id": session_id, "reply": reply}), 200

    except Exception:
        logger.exception("Unexpected error in /invoke")
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


@app.get("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
