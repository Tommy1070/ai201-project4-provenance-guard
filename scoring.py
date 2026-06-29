def combine_scores(llm_score, stylometric_score):
    """
    Combines the Groq LLM score and the stylometric score.

    Higher score = more AI-like.
    """

    final_score = (0.65 * llm_score) + (0.35 * stylometric_score)

    return round(final_score, 2)


def get_attribution(confidence):
    """
    Converts the final score into one of three categories.
    """

    if confidence >= 0.70:
        return "likely_ai"

    if confidence <= 0.39:
        return "likely_human"

    return "uncertain"