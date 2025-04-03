from flask import request, jsonify, Response, stream_with_context
import logging
from app.chatbot import company_info_handler_streaming
from app.database import create_chat_session, store_message
from app.speech import speech_to_text

logging.basicConfig(level=logging.DEBUG)

# Handle text-based chat
def handle_chat():
    user_input = request.form.get("user_input")
    session_id = request.form.get("session_id")

    # Handle missing input
    if not user_input:
        return jsonify({"response": "No input provided.", "session_id": session_id})

    return process_chat(user_input, session_id)

# Handle voice-based chat
def handle_voice_chat():
    try:
        session_id = request.form.get("session_id", "unknown")

        logging.debug(f"Voice chat request received. Session ID: {session_id}")

        # Convert speech to text
        user_input = speech_to_text()

        if not user_input:
            logging.error("Speech recognition returned empty text.")
            return jsonify({"error": "Sorry, I couldn't recognize your speech."}), 400

        return process_chat(user_input, session_id)

    except Exception as e:
        logging.exception("Error processing voice chat")
        return jsonify({"error": f"Error processing voice: {str(e)}"}), 500

# Process chat messages
def process_chat(user_input, session_id):
    if not session_id or session_id == "None":
        session_id = create_chat_session()
        if not session_id:
            return jsonify({"response": "Error creating session.", "session_id": None})

    store_message(session_id, user_input, "user")

    def generate():
        full_reply = ""
        try:
            for chunk in company_info_handler_streaming(user_input, session_id):
                full_reply += chunk
                yield chunk
        finally:
            if full_reply.strip():
                store_message(session_id, full_reply.strip(), "bot")

    return Response(stream_with_context(generate()), mimetype="text/plain")
