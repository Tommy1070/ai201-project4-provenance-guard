"""
detector.py

This file contains the detection signals:
1. Groq LLM classifier
2. Stylometric heuristic analysis
"""

import os
import json
import re
import string
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def classify_with_groq(text):
    """
    First signal: sends submitted text to Groq for AI detection.
    """

    if not GROQ_API_KEY:
        raise ValueError("Missing GROQ_API_KEY. Add it to your .env file.")

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are part of a content provenance system.

Analyze the following text and estimate whether it appears AI-generated or human-written.

Return ONLY valid JSON in this format:

{{
  "label":"likely_ai",
  "score":0.82,
  "reasoning":"short explanation"
}}

If the text appears human-written use:
"label":"likely_human"

If you cannot decide:
"label":"uncertain"

Score:
0.0 = strongly human
1.0 = strongly AI

Text:

{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    raw_output = response.choices[0].message.content

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError:
        result = {
            "label": "uncertain",
            "score": 0.50,
            "reasoning": "Groq response could not be parsed as JSON."
        }

    return result


def analyze_stylometrics(text):
    """
    Second signal: uses writing statistics to estimate whether text
    looks more AI-like or human-like.

    Higher score = more AI-like.
    """

    words = re.findall(r"\b\w+\b", text.lower())
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not words or not sentences:
        return {
            "score": 0.50,
            "metrics": {
                "sentence_length_variance": 0,
                "type_token_ratio": 0,
                "punctuation_density": 0,
                "repetition_rate": 0
            }
        }

    sentence_lengths = [
        len(re.findall(r"\b\w+\b", sentence))
        for sentence in sentences
    ]

    avg_length = sum(sentence_lengths) / len(sentence_lengths)

    variance = sum(
        (length - avg_length) ** 2 for length in sentence_lengths
    ) / len(sentence_lengths)

    unique_words = set(words)
    type_token_ratio = len(unique_words) / len(words)

    punctuation_count = sum(1 for char in text if char in string.punctuation)
    punctuation_density = punctuation_count / max(len(text), 1)

    repeated_words = len(words) - len(unique_words)
    repetition_rate = repeated_words / len(words)

    score = 0.0

    if variance < 8:
        score += 0.30

    if type_token_ratio < 0.55:
        score += 0.30

    if repetition_rate > 0.20:
        score += 0.25

    if punctuation_density < 0.04:
        score += 0.15

    return {
        "score": round(min(score, 1.0), 2),
        "metrics": {
            "sentence_length_variance": round(variance, 2),
            "type_token_ratio": round(type_token_ratio, 2),
            "punctuation_density": round(punctuation_density, 3),
            "repetition_rate": round(repetition_rate, 2)
        }
    }