# This module is responsible for storing and retrieving
# every classification and appeal made by our system.

import json      # Allows us to work with JSON files
import os        # Lets us check if a file exists

# Name of the file that will store our audit log
LOG_FILE = "audit_log.json"


def load_log():
    """
    Loads the current audit log.

    If the log file doesn't exist yet,
    return an empty list instead of crashing.
    """

    # Check whether the log file already exists
    if not os.path.exists(LOG_FILE):
        return []

    # Open the JSON file in read mode
    with open(LOG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_log(entries):
    """
    Saves the entire audit log back to disk.

    Parameter:
        entries (list): Every log entry we want to save.
    """

    # "w" means overwrite the file with the newest version
    with open(LOG_FILE, "w", encoding="utf-8") as file:

        # indent=2 makes the JSON much easier to read
        json.dump(entries, file, indent=2)


def write_log(entry):
    """
    Adds ONE new event to the audit log.

    Example:
        A new submission
        A new appeal
    """

    # Load existing entries
    entries = load_log()

    # Add the newest entry
    entries.append(entry)

    # Save everything back to the file
    save_log(entries)


def get_recent_logs(limit=20):
    """
    Returns only the newest log entries.

    By default, we return the last 20.
    """

    entries = load_log()

    # Python slicing:
    # [-20:] means "last 20 items"
    return entries[-limit:]