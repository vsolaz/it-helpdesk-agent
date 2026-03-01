import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from agent.graph import run_turn
from agent.session_repository import SessionRepository

logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app, origins=["http://localhost:4200"])
_repository = SessionRepository()

@app.post("/invoke")
def invoke():
    try:
        body = request.get_json(silent=True) or {}
        session_id = body.get("session_id", "")
        message = body.get("message", "")
        if not session_id: return jsonify({"error": "Missing required field: session_id"}), 400
        if not message: return jsonify({"error": "Missing required field: message"}), 400
        reply = run_turn(session_id=session_id, user_message=message, repository=_repository)
        return jsonify({"session_id": session_id, "reply": reply}), 200
    except Exception:
        logger.exception("Unexpected error")
        return jsonify({"error": "An unexpected error occurred."}), 500

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
