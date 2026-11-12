
import json
import os
import shutil
import sys
from pathlib import Path


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent


APP_DATA_DIR = (
    Path(os.environ["LOCALAPPDATA"]) / "GeneratorTaloniv"
    if os.environ.get("LOCALAPPDATA")
    else Path.home() / "AppData" / "Local" / "GeneratorTaloniv"
)


SETTINGS_FILE = APP_DATA_DIR / "settings.json"
HISTORY_FILE = APP_DATA_DIR / "history.json"
COUNTER_FILE = APP_DATA_DIR / "ticket_counter.txt"

PDF_DIR = APP_DATA_DIR / "PDF"
QR_DIR = APP_DATA_DIR / "QR-коди"


DEFAULT_SETTINGS = {
    "company_name": "Назва підприємства",
    "company_address": "Адреса підприємства",
    "location": "49.7695890, 28.7308250 (Глухівці)",
    "footer_text": "Пред'явіть цей талон відповідальному працівнику.",
    "appearance_mode": "dark"
}


def migrate_file(source, destination):
    if source.exists() and not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def migrate_old_data():
    migrate_file(BASE_DIR / "settings.json", SETTINGS_FILE)
    migrate_file(BASE_DIR / "history.json", HISTORY_FILE)
    migrate_file(BASE_DIR / "ticket_counter.txt", COUNTER_FILE)


def ensure_storage():
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    QR_DIR.mkdir(parents=True, exist_ok=True)

    migrate_old_data()

    if not SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(
                DEFAULT_SETTINGS,
                file,
                ensure_ascii=False,
                indent=4
            )

    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")

    if not COUNTER_FILE.exists():
        COUNTER_FILE.write_text("0", encoding="utf-8")


def load_settings():
    ensure_storage()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)

        if not isinstance(settings, dict):
            settings = {}

        result = DEFAULT_SETTINGS.copy()
        result.update(settings)

        # Видаляємо застаріле налаштування логотипа.
        result.pop("logo_file", None)

        if result.get("appearance_mode") not in ("dark", "light"):
            result["appearance_mode"] = "dark"

        return result

    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    ensure_storage()

    settings = settings.copy()
    settings.pop("logo_file", None)

    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            settings,
            file,
            ensure_ascii=False,
            indent=4
        )