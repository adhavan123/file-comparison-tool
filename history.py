import json
import os

HISTORY_FILE = "history.json"


def load_history():

    if not os.path.exists(HISTORY_FILE):

        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)

    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(record):

    history = load_history()

    history.append(record)

    with open(HISTORY_FILE, "w") as f:
        json.dump(
            history,
            f,
            indent=4
        )