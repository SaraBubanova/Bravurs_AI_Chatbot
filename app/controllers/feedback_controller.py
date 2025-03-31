from flask import request, jsonify
import logging
from app.database import get_db_connection

def handle_feedback_submission():
    session_id = request.form.get("session_id")
    rating = request.form.get("rating")
    comment = request.form.get("comment", "")

    if not session_id or not rating:
        return jsonify({"message": "Missing session ID or rating"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"message": "Failed to connect to DB"}), 500

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT feedback_id FROM feedback WHERE session_id = %s;", (session_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE feedback
                SET rating = %s, comment = %s, timestamp = NOW()
                WHERE session_id = %s;
                """,
                (rating, comment, session_id)
            )
            message = "Feedback updated successfully!"
        else:
            cursor.execute(
                """
                INSERT INTO feedback (session_id, rating, comment, timestamp)
                VALUES (%s, %s, %s, NOW());
                """,
                (session_id, rating, comment)
            )
            message = "Feedback submitted successfully!"

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": message})
    except Exception as e:
        logging.error(f"Feedback save failed: {e}")
        return jsonify({"message": "Failed to save feedback"}), 500
