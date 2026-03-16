
from flask import Flask, render_template, request, jsonify, session
from chatbot_engine import RuleBasedChatbot
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "rulebot-secret-2024"

bot = RuleBasedChatbot()

SUGGESTIONS = [
    "Hello 👋",
    "Tell me a joke 😄",
    "What time is it? ⏰",
    "What's today's date? 📅",
    "12 * 8",
    "Help me 🆘",
    "Who are you? 🤖",
    "Goodbye 👋",
]


@app.route("/")
def index():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())[:8]
    return render_template("index.html", suggestions=SUGGESTIONS)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    reply = bot.respond(user_msg)
    timestamp = datetime.now().strftime("%I:%M %p")

    return jsonify({
        "reply": reply,
        "timestamp": timestamp,
        "session": session.get("session_id", "—"),
    })


@app.route("/api/clear", methods=["POST"])
def clear():
    session["session_id"] = str(uuid.uuid4())[:8]
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)