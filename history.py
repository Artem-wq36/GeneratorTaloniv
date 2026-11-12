
import json
from pathlib import Path
from send2trash import send2trash

from settings import (
    HISTORY_FILE,
    COUNTER_FILE,
    ensure_storage
)


def get_next_number():
    ensure_storage()

    try:
        last_number = int(
            COUNTER_FILE.read_text(encoding="utf-8").strip()
        )
    except (ValueError, OSError):
        last_number = 0

    history = load_history()
    history_numbers = []

    for ticket in history:
        try:
            number = int(ticket.get("number", 0))

            if number > 0:
                history_numbers.append(number)

        except (ValueError, TypeError):
            continue

    if history_numbers:
        last_number = max(last_number, max(history_numbers))

    next_number = last_number + 1

    COUNTER_FILE.write_text(
        str(next_number),
        encoding="utf-8"
    )

    return next_number


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


def delete_tickets_to_trash(selected_indices):
    ensure_storage()

    history = load_history()

    selected_indices = sorted(
        set(selected_indices),
        reverse=True
    )

    removed_tickets = []
    failed_tickets = []

    for index in selected_indices:
        if not isinstance(index, int):
            continue

        if not 0 <= index < len(history):
            continue

        ticket = history[index]

        try:
            for key in ("pdf_path", "qr_path"):
                file_path = ticket.get(key)

                if not file_path:
                    continue

                file_path = Path(file_path)

                if file_path.exists() and file_path.is_file():
                    send2trash(str(file_path))

            removed_tickets.append((index, ticket))

        except (OSError, PermissionError, ValueError) as error:
            failed_tickets.append({
                "number": ticket.get("number", "Невідомо"),
                "error": str(error)
            })

    removed_indices = {
        index for index, ticket in removed_tickets
    }

    new_history = [
        ticket
        for index, ticket in enumerate(history)
        if index not in removed_indices
    ]

    temp_file = HISTORY_FILE.with_name(
        HISTORY_FILE.name + ".tmp"
    )

    try:
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(
                new_history,
                file,
                ensure_ascii=False,
                indent=4
            )

        temp_file.replace(HISTORY_FILE)

    except (OSError, TypeError, ValueError):
        temp_file.unlink(missing_ok=True)
        raise

    return (
        [ticket for index, ticket in removed_tickets],
        failed_tickets
    )