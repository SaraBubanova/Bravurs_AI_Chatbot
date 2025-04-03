from flask import Blueprint, request, jsonify, Response, stream_with_context, render_template
from app.controllers.chat_controller import handle_chat, handle_voice_chat
from app.controllers.feedback_controller import handle_feedback_submission
from app.controllers.history_controller import handle_history_fetch
from app.database import create_chat_session
from app.speech import speech_to_text

# === API ROUTES under /api/v1 ===
routes = Blueprint("routes", __name__, url_prefix="/api/v1")

@routes.route("/chat", methods=["POST"])
def chat():
    return handle_chat()

@routes.route("/voice-chat", methods=["POST"])
def voice_chat():
    return handle_voice_chat()

@routes.route("/feedback", methods=["POST"])
def submit_feedback():
    return handle_feedback_submission()

@routes.route("/history", methods=["GET"])
def get_history():
    return handle_history_fetch()

@routes.route("/session/create", methods=["POST"])
def create_session():
    session_id = create_chat_session()
    if session_id:
        return jsonify({"session_id": session_id})
    return jsonify({"error": "Failed to create session"}), 500

@routes.route("/speech-to-text", methods=["GET"])
def speech_to_text_route():
    text = speech_to_text()
    return jsonify({"recognized_text": text})

# === Frontend Routes ===
frontend = Blueprint("frontend", __name__)

@frontend.route("/", methods=["GET"])
def serve_home():
    session_id = create_chat_session()
    return render_template("index.html", session_id=session_id)
