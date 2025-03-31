from flask import request, jsonify, Response, stream_with_context
import logging
from app.chatbot import company_info_handler_streaming
from app.database import create_chat_session

def handle_chat():
    user_input = request.form["user_input"]
    session_id = request.form.get("session_id")

    if session_id == "None" or not session_id:
        session_id = create_chat_session()
        if not session_id:
            return jsonify({
                "response": "Sorry, I'm having trouble with your session. Please try again.",
                "session_id": None
            })

    try:
        session_id = int(session_id)
    except (ValueError, TypeError):
        session_id = create_chat_session()
        if not session_id:
            return jsonify({
                "response": "Sorry, I'm having trouble with your session. Please try again.",
                "session_id": None
            })

    def generate():
        yield from company_info_handler_streaming(user_input, session_id)

    return Response(stream_with_context(generate()), mimetype="text/plain")
