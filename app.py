from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timezone
import uuid

from detector import classify_with_groq, analyze_stylometrics
from scoring import combine_scores, get_attribution
from labels import generate_label
from appeals import submit_appeal
from audit import write_log, get_recent_logs

app = Flask(__name__)

# Limit API requests to reduce abuse
limiter = Limiter(
    key_func=get_remote_address,
    app=app
)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Provenance Guard API is running"
    })


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute")
def submit():
    data = request.get_json()

    if not data or "text" not in data or "creator_id" not in data:
        return jsonify({
            "error": "Request must include text and creator_id"
        }), 400

    text = data["text"]
    creator_id = data["creator_id"]
    content_id = str(uuid.uuid4())

    # -----------------------------
    # Signal 1: Groq LLM Detection
    # -----------------------------
    groq_result = classify_with_groq(text)

    # -----------------------------
    # Signal 2: Stylometric Analysis
    # -----------------------------
    stylometric_result = analyze_stylometrics(text)

    llm_score = groq_result["score"]
    stylometric_score = stylometric_result["score"]

    # Combine both signals into one confidence score
    confidence = combine_scores(llm_score, stylometric_score)

    # Determine the final attribution
    attribution = get_attribution(confidence)

    # Generate a transparency label for the user
    label = generate_label(attribution)

    # Save the classification to the audit log
    log_entry = {
        "event_type": "classification",
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text_preview": text[:120],
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "stylometric_score": stylometric_score,
        "stylometric_metrics": stylometric_result["metrics"],
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
            "llm_score": llm_score,
            "stylometric_score": stylometric_score,
            "stylometric_metrics": stylometric_result["metrics"]
        },
        "reasoning": groq_result["reasoning"],
        "status": "classified"
    })


@app.route("/appeal", methods=["POST"])
@limiter.limit("5 per minute")
def appeal():
    """
    Allows a creator to appeal a previous classification.
    """

    data = request.get_json()

    if (
        not data
        or "content_id" not in data
        or "creator_reasoning" not in data
    ):
        return jsonify({
            "error": "Request must include content_id and creator_reasoning."
        }), 400

    result = submit_appeal(
        data["content_id"],
        data["creator_reasoning"]
    )

    if result is None:
        return jsonify({
            "error": "Content ID not found."
        }), 404

    return jsonify({
        "message": "Appeal submitted successfully.",
        "appeal": result
    })


@app.route("/log", methods=["GET"])
@limiter.limit("20 per minute")
def get_log():
    return jsonify({
        "entries": get_recent_logs()
    })


if __name__ == "__main__":
    app.run(debug=True)