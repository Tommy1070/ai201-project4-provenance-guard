def generate_label(attribution):
    """
    Returns the reader-facing transparency label.
    """

    if attribution == "likely_ai":
        return "This content appears likely to be AI-generated based on multiple detection signals. This result is an estimate and may be appealed by the creator."

    if attribution == "likely_human":
        return "This content appears likely to be human-written based on multiple detection signals. Detection systems are not perfect, and this result should be interpreted as a confidence-based estimate."

    return "Our system could not confidently determine whether this content was AI-generated or human-written. Readers should interpret this result with caution, and the creator may submit an appeal."