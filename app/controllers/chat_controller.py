from flask import request, jsonify, Response, stream_with_context
import logging
from app.chatbot import company_info_handler_streaming
from app.database import create_chat_session

# Handle user chat POST request and stream GPT response
def handle_chat():
    user_input = request.form["user_input"]
    session_id = request.form.get("session_id")

    # Create session if none provided
    if session_id == "None" or not session_id:
        session_id = create_chat_session()
        if not session_id:
            return jsonify({
                "response": "Sorry, I'm having trouble with your session. Please try again.",
                "session_id": None
            })

    # Convert session_id to integer
    try:
        session_id = int(session_id)
    except (ValueError, TypeError):
        session_id = create_chat_session()
        if not session_id:
            return jsonify({
                "response": "Sorry, I'm having trouble with your session. Please try again.",
                "session_id": None
            })

    # Stream GPT reply using generator
    def generate():
        yield from company_info_handler_streaming(user_input, session_id)

    return Response(stream_with_context(generate()), mimetype="text/plain")
