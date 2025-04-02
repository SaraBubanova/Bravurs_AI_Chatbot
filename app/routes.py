from flask import Blueprint, request, jsonify, Response, stream_with_context
from app.controllers.chat_controller import handle_chat
from app.controllers.feedback_controller import handle_feedback_submission
from app.controllers.history_controller import handle_history_fetch
from app.database import create_chat_session

# Blueprint for all API v1 endpoints
routes = Blueprint("routes", __name__, url_prefix="/api/v1")

# POST /api/v1/chat – send user input, receive GPT reply (streamed)
@routes.route("/chat", methods=["POST"])
def chat():
    return handle_chat()

# POST /api/v1/feedback – submit or update rating and comment
@routes.route("/feedback", methods=["POST"])
def submit_feedback():
    return handle_feedback_submission()

# GET /api/v1/history – get all messages for a given session
@routes.route("/history", methods=["GET"])
def get_history():
    return handle_history_fetch()

# POST /api/v1/session/create – create a new chat session
@routes.route("/session/create", methods=["POST"])
def create_session():
    session_id = create_chat_session()
    if session_id:
        return jsonify({"session_id": session_id})
    return jsonify({"error": "Failed to create session"}), 500
