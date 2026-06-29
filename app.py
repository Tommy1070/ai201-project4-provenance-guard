from flask import Flask, request, jsonify
from datetime import datetime, timezone
import uuid

from detector import classify_with_groq
from audit import write_log, get_recent_logs

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Provenance Guard API is running"
    })


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()

    if not data or "text" not in data or "creator_id" not in data:
        return jsonify({
            "error": "Request must include text and creator_id"
        }), 400

    text = data["text"]
    creator_id = data["creator_id"]
    content_id = str(uuid.uuid4())

    groq_result = classify_with_groq(text)

    attribution = groq_result["label"]
    confidence = groq_result["score"]

    label = "Temporary label for Milestone 3. Full transparency labels will be added in Milestone 5."

    log_entry = {
        "event_type": "classification",
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text_preview": text[:120],
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": confidence,
        "stylometric_score": None,
        "llm_reasoning": groq_result["reasoning"],
        "status": "classified"
    }

    write_log(log_entry)

    return jsonify({
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": label,
        "signals": {
            "llm_score": confidence,
            "stylometric_score": None
        },
        "reasoning": groq_result["reasoning"],
        "status": "classified"
    })


@app.route("/log", methods=["GET"])
def get_log():
    return jsonify({
        "entries": get_recent_logs()
    })


if __name__ == "__main__":
    app.run(debug=True)