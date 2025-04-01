from flask import Blueprint, render_template
from app.database import create_chat_session
from app.controllers.chat_controller import handle_chat
from app.controllers.feedback_controller import handle_feedback_submission
from app.controllers.history_controller import handle_history_fetch

routes = Blueprint("routes", __name__)

@routes.route("/")
def home():
    session_id = create_chat_session()
    return render_template("index.html", session_id=session_id)

@routes.route("/chat", methods=["POST"])
def chat():
    return handle_chat()

@routes.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    return handle_feedback_submission()

@routes.route("/history", methods=["GET"])
def get_history():
    return handle_history_fetch()
