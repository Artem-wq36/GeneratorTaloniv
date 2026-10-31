import json

from settings import (
    HISTORY_FILE,
    COUNTER_FILE,
    ensure_storage
)


def get_next_number():
    ensure_storage()

    try:
        number = int(COUNTER_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        number = 0

    return number + 1


def load_history():
    ensure_storage()

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def save_ticket(ticket):
    ensure_storage()

    history = load_history()
    history.append(ticket)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=4)

    COUNTER_FILE.write_text(
        str(ticket["number"]),
        encoding="utf-8"
    )
