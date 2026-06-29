from audit import load_log, save_log


def submit_appeal(content_id, creator_reasoning):
    entries = load_log()

    found = False

    for entry in entries:
        if entry.get("content_id") == content_id:
            entry["status"] = "under_review"
            found = True

    if not found:
        return None

    appeal_entry = {
        "event_type": "appeal",
        "content_id": content_id,
        "creator_reasoning": creator_reasoning,
        "status": "under_review"
    }

    entries.append(appeal_entry)
    save_log(entries)

    return appeal_entry