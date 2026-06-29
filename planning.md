# Provenance Guard Planning

## Project Overview

Provenance Guard is a backend system designed for creative content platforms to help determine whether submitted text is likely AI-generated or human-written. Instead of making absolute decisions, the system combines multiple detection signals to estimate a confidence score, communicate uncertainty through transparency labels, and provide an appeals process for creators who believe their work has been misclassified.

The system emphasizes fairness by reducing false positives, especially for human creators, while maintaining accountability through structured audit logging and rate limiting.

---

# Architecture

## Submission Flow

```text
POST /submit
        |
        v
Validate Request
(text + creator_id)
        |
        v
Detection Pipeline
        |
        +-----------------------------+
        |                             |
        |                             |
Signal 1                     Signal 2
Groq LLM                 Stylometric Analysis
        |                             |
        +-------------+---------------+
                      |
                      v
             Confidence Scoring
                      |
                      v
          Transparency Label Generator
                      |
                      v
                Audit Log Storage
                      |
                      v
             JSON Response Returned
```

## Appeal Flow

```text
POST /appeal
        |
        v
Validate content_id
        |
        v
Find Existing Decision
        |
        v
Update Status
(under_review)
        |
        v
Append Appeal to Audit Log
        |
        v
Return Confirmation
```

### Architecture Narrative

When a creator submits text through the `/submit` endpoint, the request is validated before entering the detection pipeline. Two independent detection signals analyze the content. Their scores are combined into a single confidence score, which is converted into a transparency label for the user. Every decision is stored in the audit log before the API returns the final response.

If the creator believes the classification is incorrect, they can submit an appeal using the `/appeal` endpoint. The appeal updates the content status to **under_review**, stores the creator's reasoning, and records the event in the audit log without deleting the original decision.


---

# API Surface

## POST /submit

Accepts a text submission and creator ID.

Example request:

```json
{
  "text": "The sun dipped below the horizon as I sat on the porch with coffee in my hand.",
  "creator_id": "creator-123"
}
```

Example response:

```json
{
  "content_id": "unique-content-id",
  "creator_id": "creator-123",
  "attribution": "likely_ai | likely_human | uncertain",
  "confidence": 0.82,
  "label": "Transparency label text shown to users.",
  "signals": {
    "llm_score": 0.88,
    "stylometric_score": 0.71
  },
  "status": "classified"
}
```

## POST /appeal

Allows a creator to contest a classification.

Example request:

```json
{
  "content_id": "unique-content-id",
  "creator_reasoning": "I wrote this myself from personal experience."
}
```

Example response:

```json
{
  "content_id": "unique-content-id",
  "status": "under_review",
  "message": "Appeal received and logged for review."
}
```

## GET /log

Returns recent structured audit log entries.

Example response:

```json
{
  "entries": [
    {
      "event_type": "classification",
      "content_id": "unique-content-id",
      "creator_id": "creator-123",
      "timestamp": "2026-06-29T12:00:00Z",
      "attribution": "likely_ai",
      "confidence": 0.82,
      "llm_score": 0.88,
      "stylometric_score": 0.71,
      "status": "classified"
    }
  ]
}
```

---

# Detection Signals

## Signal 1: Groq LLM Classification

The first signal uses a Groq-hosted large language model to evaluate whether the submitted text appears AI-generated or human-written.

This signal captures:

* semantic coherence
* generic AI-style phrasing
* overly polished structure
* unnatural transitions
* formulaic writing patterns

The signal returns a score from `0.0` to `1.0`.

* `0.0` means strongly human-written
* `0.5` means uncertain
* `1.0` means strongly AI-generated

Example output:

```json
{
  "label": "likely_ai",
  "score": 0.82,
  "reasoning": "The writing appears polished, generic, and uses formulaic transitions."
}
```

### Why I chose this signal

An LLM can evaluate the overall style, tone, structure, and semantic flow of a passage. This makes it useful for detecting patterns that simple statistics might miss.

### Blind spot

This signal may misclassify formal human writing, academic writing, edited writing, or writing from non-native English speakers as AI-generated.

## Signal 2: Stylometric Heuristics

The second signal uses pure Python measurements to analyze the structure of the writing.

Metrics used:

* sentence length variance
* vocabulary diversity
* punctuation density
* repetition rate

This signal returns a score from `0.0` to `1.0`, where higher means more AI-like.

Example output:

```json
{
  "score": 0.64,
  "metrics": {
    "sentence_length_variance": 3.2,
    "type_token_ratio": 0.48,
    "punctuation_density": 0.04,
    "repetition_rate": 0.11
  }
}
```

### Why I chose this signal

Stylometric analysis gives the system an independent structural signal. AI-generated text often has more uniform sentence patterns and smoother vocabulary distribution, while human writing is often more irregular.

### Blind spot

This signal can struggle with poetry, very short submissions, edited writing, and formal essays because those forms may naturally have unusual structure or repetition.


---

# Confidence Scoring

The final confidence score combines both detection signals using a weighted average.

Formula:

```text
Final Score = (0.65 × LLM Score) + (0.35 × Stylometric Score)
```

The LLM signal receives a higher weight because it evaluates the overall semantic meaning and writing style, while the stylometric signal serves as an independent structural check.

## Confidence Thresholds

| Score Range | Attribution  |
| ----------- | ------------ |
| 0.00 – 0.39 | Likely Human |
| 0.40 – 0.69 | Uncertain    |
| 0.70 – 1.00 | Likely AI    |

A confidence score around **0.60** means the system found some AI-like characteristics but not enough evidence to confidently classify the content. These cases are labeled as **Uncertain** to reduce false positives.

---

# Transparency Labels

## High Confidence AI

> "This content appears likely to be AI-generated based on multiple detection signals. This result is an estimate and may be appealed by the creator."

## High Confidence Human

> "This content appears likely to be human-written based on multiple detection signals. Detection systems are not perfect, and this result should be interpreted as a confidence-based estimate."

## Uncertain

> "Our system could not confidently determine whether this content was AI-generated or human-written. Readers should interpret this result with caution, and the creator may submit an appeal."

---

# Appeals Workflow

Any creator with a valid **content_id** may submit an appeal.

Each appeal must include:

* content_id
* creator_reasoning

When an appeal is received, the system:

1. Locates the original classification.
2. Updates the submission status to **under_review**.
3. Records the creator's reasoning.
4. Preserves the original classification.
5. Adds a new appeal event to the audit log.

A reviewer would see:

* content ID
* original classification
* confidence score
* individual detection scores
* creator reasoning
* current review status

---

# Rate Limiting

The submission endpoint will allow:

* **10 requests per minute**
* **100 requests per day**

These limits reflect realistic usage by individual creators while preventing automated abuse.

---

# Audit Log

Every classification stores:

* timestamp
* creator ID
* content ID
* attribution result
* confidence score
* LLM score
* stylometric score
* status

Every appeal additionally stores:

* creator reasoning
* appeal timestamp
* updated status

---

# Anticipated Edge Cases

### Poetry

Poetry often contains repetition and unconventional structure, which may resemble AI-generated text.

### Academic Writing

Formal academic writing may appear highly polished and could receive a higher AI score despite being written by a human.

### Very Short Text

Short submissions provide insufficient information for reliable stylometric analysis and should generally produce lower confidence.

### Non-native English Writers

Writing styles from non-native English speakers may differ from typical native patterns and could influence the model's confidence.

---

# False Positive Considerations

False positives are considered more harmful than false negatives because incorrectly labeling human-created work as AI-generated may reduce trust in creators.

To minimize this risk:

* Borderline scores become **Uncertain**.
* High AI confidence requires a score of at least **0.70**.
* Every decision can be appealed.
* Transparency labels clearly explain that results are estimates.

---

# AI Tool Plan

## Milestone 3

Generate:

* Flask application
* POST `/submit`
* GET `/log`
* Groq detection function

Verify:

* API accepts requests
* Responses include content ID and confidence
* Audit log records submissions

## Milestone 4

Generate:

* Stylometric analysis
* Confidence scoring logic

Verify:

* AI and human samples receive noticeably different scores.
* Borderline examples produce **Uncertain** results.

## Milestone 5

Generate:

* Transparency label logic
* POST `/appeal`
* Flask-Limiter integration
* Complete audit logging

Verify:

* All three labels can be reached.
* Appeals update status to **under_review**.
* Rate limiting returns HTTP 429 after the configured limit.
* Audit log records classifications and appeals correctly.
