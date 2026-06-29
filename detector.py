"""
detector.py

This file contains our first detection signal:
a Groq LLM classifier.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Read the API key from the environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def classify_with_groq(text):
    """
    Sends submitted text to Groq for AI detection.

    Returns:
    {
        "label": "...",
        "score": ...,
        "reasoning": "..."
    }
    """

    # DEBUG: Confirms this function is actually being called
    print("\n>>> classify_with_groq() is running")

    # Make sure the API key exists
    if not GROQ_API_KEY:
        raise ValueError("Missing GROQ_API_KEY. Add it to your .env file.")

    # Create the Groq client
    client = Groq(api_key=GROQ_API_KEY)

    # Prompt sent to the model
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

    # DEBUG
    print(">>> About to call Groq API...")

    # Call Groq
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

    # Get the model's reply
    raw_output = response.choices[0].message.content

    # DEBUG
    print(">>> Groq returned:")
    print(raw_output)

    # Try converting JSON text into a Python dictionary
    try:
        result = json.loads(raw_output)

    except json.JSONDecodeError:
        print(">>> JSON parsing failed!")

        result = {
            "label": "uncertain",
            "score": 0.50,
            "reasoning": "Groq response could not be parsed as JSON."
        }

    # DEBUG
    print(">>> Final parsed result:")
    print(result)

    return result