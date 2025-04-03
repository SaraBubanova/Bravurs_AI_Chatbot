from flask import request, jsonify, Response, stream_with_context
import logging
from app.chatbot import company_info_handler_streaming, classify_intent, client
from app.database import create_chat_session, store_message

# Handle user chat POST request and stream GPT response
def handle_chat():
    user_input = request.form["user_input"]
    session_id = request.form.get("session_id")
    if session_id == "None" or not session_id:
        session_id = create_chat_session()
        if not session_id:
            return "Sorry, I'm having trouble with your session. Please try again."
    try:
        session_id = int(session_id)
    except (ValueError, TypeError):
        session_id = create_chat_session()
        if not session_id:
            return "Sorry, I'm having trouble with your session. Please try again."
    store_message(session_id, user_input, "user")
    detected_intent = classify_intent(user_input)
    if detected_intent == "Unknown":
        return "I'm here to answer questions about Bravur and IT services. How can I help?"
    if detected_intent == "Human Support Service Request":
        support_message = "For human support, contact us on WhatsApp at +31 6 12345678 or email support@bravur.com."
        if session_id:
            support_message += f" When contacting support, please mention your session ID: {session_id}"
        return support_message
    if detected_intent == "IT Services & Trends":
        gpt_prompt = [
            {"role": "system", "content": "You are a knowledgeable assistant providing insights on IT services and current industry trends. Format responses for display in a simple HTML website. Be concise. Use short paragraphs, barely use bullet points, make it look like a human chatbot and avoid long blocks of text. Keep responses very concise."},
            {"role": "user", "content": user_input}
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=gpt_prompt
        )
        bot_response = response.choices[0].message.content.strip()
        store_message(session_id, bot_response, "bot")
        return bot_response
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
