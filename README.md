# Provenance Guard

## Overview

Provenance Guard is a Flask-based API that estimates whether submitted text is likely AI-generated or human-written. The system combines two independent detection signals—a Groq large language model and a stylometric analysis—to produce a confidence score and attribution. Every classification is stored in an audit log, and creators can submit appeals for review.

---

## Features

- AI text classification using Groq
- Stylometric analysis
- Combined confidence scoring
- Transparency labels
- Audit logging
- Appeal workflow
- Rate limiting using Flask-Limiter

---

## Technologies Used

- Python 3
- Flask
- Groq API
- Flask-Limiter
- python-dotenv
- JSON

---

## Project Structure

```
app.py
detector.py
scoring.py
labels.py
appeals.py
audit.py
audit_log.json
requirements.txt
README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Tommy1070/ai201-project4-provenance-guard.git
cd ai201-project4-provenance-guard
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

---

## Running the Application

```bash
python app.py
```

The API will run at:

```
http://127.0.0.1:5000
```

---

## API Endpoints

### GET /

Returns a status message indicating the API is running.

---

### POST /submit

Classifies submitted text.

Example request:

```json
{
  "text": "This is my sample text.",
  "creator_id": "tom"
}
```

Example response:

```json
{
  "content_id": "...",
  "attribution": "likely_human",
  "confidence": 0.29,
  "label": "...",
  "signals": {
    "llm_score": 0.21,
    "stylometric_score": 0.45
  }
}
```

---

### POST /appeal

Submit an appeal for a previous classification.

Example request:

```json
{
  "content_id": "YOUR_CONTENT_ID",
  "creator_reasoning": "I wrote this myself."
}
```

---

### GET /log

Returns recent audit log entries.

---

## Detection Pipeline

1. User submits text.
2. Groq analyzes the text.
3. Stylometric analysis computes writing characteristics.
4. Both scores are combined into a final confidence score.
5. A transparency label is generated.
6. The result is stored in the audit log.
7. Users may submit an appeal if they disagree with the classification.

---

## Author

**Tomiwa Olanrewaju**

Texas A&M University–Kingsville

Computer Science | Mathematics | Cyber Intelligence