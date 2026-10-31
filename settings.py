
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

LOGOS_DIR = APP_DATA_DIR / "logos"
PDF_DIR = APP_DATA_DIR / "PDF"
QR_DIR = APP_DATA_DIR / "QR-коди"


DEFAULT_SETTINGS = {
    "company_name": "Назва підприємства",
    "company_address": "Адреса підприємства",
    "location": "49.7695890, 28.7308250 (Глухівці)",
    "footer_text": "Пред'явіть цей талон відповідальному працівнику.",
    "logo_file": ""
}


def migrate_file(source, destination):
    if source.exists() and not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def migrate_old_data():
    migrate_file(BASE_DIR / "settings.json", SETTINGS_FILE)
    migrate_file(BASE_DIR / "history.json", HISTORY_FILE)
    migrate_file(BASE_DIR / "ticket_counter.txt", COUNTER_FILE)

    old_logos = BASE_DIR / "logos"

    if old_logos.exists():
        LOGOS_DIR.mkdir(parents=True, exist_ok=True)

        for file in old_logos.iterdir():
            destination = LOGOS_DIR / file.name

            if file.is_file() and not destination.exists():
                shutil.copy2(file, destination)


def ensure_storage():
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    LOGOS_DIR.mkdir(parents=True, exist_ok=True)
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

        result = DEFAULT_SETTINGS.copy()
        result.update(settings)

        logo_file = result.get("logo_file", "")

        if logo_file:
            old_logo_path = Path(logo_file)

            if not old_logo_path.is_absolute():
                old_logo_path = BASE_DIR / old_logo_path

            if old_logo_path.exists():
                destination = LOGOS_DIR / old_logo_path.name

                if old_logo_path.resolve() != destination.resolve():
                    if not destination.exists():
                        shutil.copy2(old_logo_path, destination)

                result["logo_file"] = str(destination)

        return result

    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    ensure_storage()

    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)
