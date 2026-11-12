import sys
import zipfile
import tkinter as tk
import customtkinter as ctk

from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
from send2trash import send2trash

from settings import (
    SETTINGS_FILE,
    HISTORY_FILE,
    COUNTER_FILE,
    DEFAULT_SETTINGS,
    load_settings,
    save_settings
)

from history import (
    get_next_number,
    load_history,
    save_ticket
)

from pdf_generator import generate_pdf


ctk.set_default_color_theme("blue")

APP_VERSION = "1.2.0"


def resource_path(relative_path):
    
    # Повертає шлях до ресурсу для звичайного запуску та EXE.
    
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path


def set_window_icon(window):
    
    # Встановлює іконку програми для вікна.
    
    try:
        window.iconbitmap(str(resource_path("app_icon.ico")))
    except (OSError, tk.TclError):
        pass


class GeneratorApp:

    BG = ("#F3F4F6", "#111827")
    CARD = ("#FFFFFF", "#1F2937")
    INPUT = ("#F9FAFB", "#111827")
    BORDER = ("#D1D5DB", "#374151")
    TEXT = ("#111827", "#F9FAFB")
    MUTED = ("#6B7280", "#9CA3AF")
    BLUE = ("#2563EB", "#2563EB")
    BLUE_HOVER = ("#1D4ED8", "#1D4ED8")
    GREEN = ("#16A34A", "#22C55E")

    def __init__(self, root):
        self.root = root

        self.settings = load_settings()

        self.appearance_mode = self.settings.get(
            "appearance_mode",
            "dark"
        )

        ctk.set_appearance_mode(self.appearance_mode)

        self.root.title("GeneratorTaloniv")
        self.root.geometry("900x910")
        self.root.minsize(760, 830)
        self.root.configure(fg_color=self.BG)

        set_window_icon(self.root)

        self.create_interface()

    def create_interface(self):
        main = ctk.CTkFrame(
            self.root,
            fg_color=self.BG,
            corner_radius=0
        )
        main.pack(fill="both", expand=True, padx=35, pady=25)

        header = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )
        header.pack(fill="x", pady=(0, 25))

        title_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="GeneratorTaloniv",
            font=("Arial", 28, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="Генератор електронних талонів",
            font=("Arial", 13),
            text_color=self.MUTED
        ).pack(anchor="w", pady=(3, 0))

        header_buttons = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )
        header_buttons.pack(side="right")

        ctk.CTkButton(
            header_buttons,
            text="ⓘ  Про програму",
            height=35,
            width=130,
            font=("Arial", 12, "bold"),
            fg_color=self.CARD,
            hover_color=self.BORDER,
            border_width=1,
            border_color=self.BORDER,
            text_color=self.TEXT,
            corner_radius=9,
            command=self.show_about
        ).pack(side="right", padx=(10, 0))

        self.theme_var = tk.BooleanVar(
            value=self.appearance_mode == "light"
        )

        self.theme_switch = ctk.CTkSwitch(
            header_buttons,
            text="Світла тема",
            variable=self.theme_var,
            onvalue=True,
            offvalue=False,
            command=self.toggle_theme,
            font=("Arial", 12),
            text_color=self.TEXT,
            progress_color=self.BLUE,
            button_color=self.CARD,
            button_hover_color=self.BORDER
        )
        self.theme_switch.pack(side="right")

        form_card = ctk.CTkFrame(
            main,
            fg_color=self.CARD,
            corner_radius=16,
            border_width=1,
            border_color=self.BORDER
        )
        form_card.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            form_card,
            text="Створення нового талона",
            font=("Arial", 19, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=25, pady=(22, 18))

        fields_frame = ctk.CTkFrame(
            form_card,
            fg_color="transparent"
        )
        fields_frame.pack(fill="x", padx=25, pady=(0, 22))

        date_time_frame = ctk.CTkFrame(
            fields_frame,
            fg_color="transparent"
        )
        date_time_frame.pack(fill="x", pady=(0, 12))

        date_frame = ctk.CTkFrame(
            date_time_frame,
            fg_color="transparent"
        )
        date_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            date_frame,
            text="Дата завантаження",
            font=("Arial", 13, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", pady=(0, 7))

        self.date_entry = ctk.CTkEntry(
            date_frame,
            height=42,
            placeholder_text="ДД.ММ.РРРР",
            font=("Arial", 13, "bold"),
            fg_color=self.INPUT,
            border_color=self.BORDER,
            text_color=self.TEXT,
            placeholder_text_color=self.MUTED,
            corner_radius=9
        )
        self.date_entry.pack(fill="x")

        time_frame = ctk.CTkFrame(
            date_time_frame,
            fg_color="transparent"
        )
        time_frame.pack(fill="x")

        ctk.CTkLabel(
            time_frame,
            text="Час завантаження",
            font=("Arial", 13, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", pady=(0, 7))

        self.time_entry = ctk.CTkEntry(
            time_frame,
            height=42,
            placeholder_text="ГГ:ХХ",
            font=("Arial", 13, "bold"),
            fg_color=self.INPUT,
            border_color=self.BORDER,
            text_color=self.TEXT,
            placeholder_text_color=self.MUTED,
            corner_radius=9
        )
        self.time_entry.pack(fill="x")

        self.vehicle_entry = self.add_field(
            fields_frame,
            "Номер транспортного засобу",
            "Введіть номер транспортного засобу"
        )

        self.driver_entry = self.add_field(
            fields_frame,
            "Ім'я водія",
            "Введіть ім'я водія"
        )

        self.manager_entry = self.add_field(
            fields_frame,
            "Контакт менеджера",
            "Введіть контакт менеджера"
        )

        ctk.CTkButton(
            form_card,
            text="Створити талон  →",
            height=48,
            font=("Arial", 15, "bold"),
            fg_color=self.BLUE,
            hover_color=self.BLUE_HOVER,
            corner_radius=10,
            command=self.create_ticket
        ).pack(fill="x", padx=25, pady=(0, 25))

        actions_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )
        actions_frame.pack(fill="x")

        actions_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            actions_frame,
            text="Переглянути історію",
            height=48,
            font=("Arial", 14, "bold"),
            fg_color=self.CARD,
            hover_color=self.BORDER,
            border_width=1,
            border_color=self.BORDER,
            corner_radius=10,
            command=self.show_history
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 7)
        )

        ctk.CTkButton(
            actions_frame,
            text="Налаштування підприємства",
            height=48,
            font=("Arial", 14, "bold"),
            fg_color=self.CARD,
            hover_color=self.BORDER,
            border_width=1,
            border_color=self.BORDER,
            corner_radius=10,
            command=self.show_settings
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(7, 0)
        )

        ctk.CTkButton(
            actions_frame,
            text="Резервне копіювання",
            height=48,
            font=("Arial", 14, "bold"),
            fg_color=self.CARD,
            hover_color=self.BORDER,
            border_width=1,
            border_color=self.BORDER,
            corner_radius=10,
            command=self.create_backup
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(12, 0)
        )

        status_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )
        status_frame.pack(side="bottom", fill="x", pady=(25, 0))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="●  Програма готова до роботи",
            font=("Arial", 12),
            text_color=self.GREEN
        )
        self.status_label.pack(anchor="center")

    def toggle_theme(self):
        new_mode = "light" if self.theme_var.get() else "dark"

        self.settings["appearance_mode"] = new_mode

        try:
            save_settings(self.settings)

        except (OSError, TypeError, ValueError) as error:
            messagebox.showwarning(
                "Помилка збереження теми",
                "Не вдалося зберегти вибрану тему.\n\n"
                f"{error}",
                parent=self.root
            )

        self.appearance_mode = new_mode
        ctk.set_appearance_mode(new_mode)

    def show_about(self):
        window = ctk.CTkToplevel(self.root)
        set_window_icon(window)

        window.title("Про програму")
        window.geometry("540x520")
        window.resizable(False, False)
        window.configure(fg_color=self.BG)
        window.transient(self.root)
        window.grab_set()

        ctk.CTkLabel(
            window,
            text="GeneratorTaloniv",
            font=("Arial", 29, "bold"),
            text_color=self.TEXT
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            window,
            text="Генератор електронних талонів",
            font=("Arial", 14),
            text_color=self.MUTED
        ).pack(pady=(0, 12))

        ctk.CTkLabel(
            window,
            text=f"Версія {APP_VERSION}",
            font=("Arial", 16, "bold"),
            text_color=self.BLUE
        ).pack(pady=(0, 22))

        info_frame = ctk.CTkFrame(
            window,
            fg_color=self.CARD,
            corner_radius=12,
            border_width=1,
            border_color=self.BORDER
        )
        info_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 20)
        )

        info_text = (
            "ПРО ПРОГРАМУ\n\n"
            "GeneratorTaloniv — програма для створення "
            "електронних талонів на завантаження.\n\n"
            "МОЖЛИВОСТІ ПРОГРАМИ\n\n"
            "• Створення PDF-талонів із QR-кодами.\n"
            "• Автоматична нумерація талонів.\n"
            "• Збереження історії створених талонів.\n"
            "• Налаштування інформації підприємства.\n"
            "• Резервне копіювання даних.\n"
            "• Повернення стандартних параметрів.\n"
            "• Підтримка світлої та темної теми.\n"
            "• Видалення непотрібних талонів із переміщенням файлів до Кошика Windows.\n"
            "• Автоматичне приховування з історії талонів, файли яких відсутні.\n\n"
            "Програма зберігає робочі дані локально."
        )

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Arial", 13),
            text_color=self.TEXT,
            justify="left",
            anchor="w",
            wraplength=440
        ).pack(
            fill="both",
            expand=True,
            padx=22,
            pady=18
        )

        ctk.CTkLabel(
            window,
            text="GeneratorTaloniv • 2026",
            font=("Arial", 11),
            text_color=self.MUTED
        ).pack(pady=(0, 12))

        ctk.CTkButton(
            window,
            text="Закрити",
            height=40,
            width=130,
            fg_color=self.BLUE,
            hover_color=self.BLUE_HOVER,
            corner_radius=9,
            command=window.destroy
        ).pack(pady=(0, 20))

    def create_backup(self):
        selected_folder = filedialog.askdirectory(
            title="Виберіть папку для резервної копії",
            initialdir=str(Path.home())
        )

        if not selected_folder:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        backup_path = (
            Path(selected_folder)
            / f"GeneratorTaloniv_Backup_{timestamp}.zip"
        )

        try:
            with zipfile.ZipFile(
                backup_path,
                "w",
                zipfile.ZIP_DEFLATED
            ) as archive:

                files = [
                    SETTINGS_FILE,
                    HISTORY_FILE,
                    COUNTER_FILE
                ]

                for file_path in files:
                    if file_path.exists():
                        archive.write(
                            file_path,
                            arcname=file_path.name
                        )

        except (OSError, zipfile.BadZipFile) as error:
            messagebox.showerror(
                "Помилка резервного копіювання",
                f"Не вдалося створити резервну копію:\n{error}",
                parent=self.root
            )
            return

        messagebox.showinfo(
            "Резервну копію створено",
            "Резервну копію GeneratorTaloniv успішно створено!\n\n"
            f"Місце збереження:\n{backup_path}",
            parent=self.root
        )

    def add_field(self, parent, label_text, placeholder):
        field_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )
        field_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=("Arial", 13, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", pady=(0, 7))

        entry = ctk.CTkEntry(
            field_frame,
            height=42,
            placeholder_text=placeholder,
            fg_color=self.INPUT,
            border_color=self.BORDER,
            text_color=self.TEXT,
            placeholder_text_color=self.MUTED,
            corner_radius=9
        )
        entry.pack(fill="x")

        return entry

    def create_ticket(self):
        vehicle = self.vehicle_entry.get().strip()
        driver = self.driver_entry.get().strip()
        manager = self.manager_entry.get().strip()
        loading_date = self.date_entry.get().strip()
        loading_time = self.time_entry.get().strip()

        if not all([
            vehicle,
            driver,
            manager,
            loading_date,
            loading_time
        ]):
            messagebox.showwarning(
                "Не всі поля заповнені",
                "Будь ласка, заповніть усі поля.",
                parent=self.root
            )
            return

        try:
            datetime.strptime(loading_date, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror(
                "Помилка дати",
                "Введіть дату у форматі ДД.ММ.РРРР.",
                parent=self.root
            )
            return

        try:
            datetime.strptime(loading_time, "%H:%M")
        except ValueError:
            messagebox.showerror(
                "Помилка часу",
                "Введіть час у форматі ГГ:ХХ.",
                parent=self.root
            )
            return

        last_folder = self.settings.get(
            "last_save_folder",
            str(Path.home())
        )

        if not Path(last_folder).is_dir():
            last_folder = str(Path.home())

        selected_folder = filedialog.askdirectory(
            title="Виберіть папку для збереження талона",
            initialdir=last_folder,
            parent=self.root
        )

        if not selected_folder:
            return

        selected_folder = Path(selected_folder)
        self.settings["last_save_folder"] = str(selected_folder)

        try:
            save_settings(self.settings)
        except Exception as error:
            messagebox.showwarning(
                "Попередження",
                f"Не вдалося запам'ятати папку:\n{error}",
                parent=self.root
            )

        try:
            number = get_next_number()

        except OSError as error:
            messagebox.showerror(
                "Помилка нумерації",
                f"Не вдалося отримати новий номер талона:\n{error}",
                parent=self.root
            )
            return

        creation_time = datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        )

        data = {
            "vehicle": vehicle,
            "driver": driver,
            "manager": manager,
            "loading_date": loading_date,
            "loading_time": loading_time,
            "creation_time": creation_time
        }

        pdf_folder = selected_folder / "PDF"
        qr_folder = selected_folder / "QR-коди"

        output_path = pdf_folder / f"talon_{number:08d}.pdf"
        qr_path = qr_folder / f"qr_{number:08d}.png"

        try:
            pdf_folder.mkdir(parents=True, exist_ok=True)
            qr_folder.mkdir(parents=True, exist_ok=True)

            generate_pdf(
                data,
                self.settings,
                number,
                output_path,
                qr_path
            )

        except Exception as error:
            messagebox.showerror(
                "Помилка створення PDF",
                f"Не вдалося створити талон:\n{error}",
                parent=self.root
            )
            return

        ticket = {
            "number": number,
            "vehicle": vehicle,
            "driver": driver,
            "manager": manager,
            "loading_date": loading_date,
            "loading_time": loading_time,
            "creation_time": creation_time,
            "company_name": self.settings["company_name"],
            "pdf_path": str(output_path),
            "qr_path": str(qr_path)
        }

        try:
            save_ticket(ticket)

        except Exception as error:
            messagebox.showwarning(
                "Талон створено, але історію не збережено",
                "PDF-файл успішно створено, але не вдалося "
                f"записати його в історію.\n\n{error}",
                parent=self.root
            )
            return

        self.status_label.configure(
            text=f"●  Талон № {number:06d} успішно створено",
            text_color=self.GREEN
        )

        messagebox.showinfo(
            "Успішно",
            f"Талон № {number:06d} створено!\n\n"
            f"PDF:\n{output_path}\n\n"
            f"QR-код:\n{qr_path}",
            parent=self.root
        )

    def show_history(self):
        history = load_history()

        window = ctk.CTkToplevel(self.root)
        set_window_icon(window)

        window.title("Історія талонів")
        window.geometry("850x650")
        window.minsize(650, 450)
        window.configure(fg_color=self.BG)
        window.transient(self.root)

        ctk.CTkLabel(
            window,
            text="Історія талонів",
            font=("Arial", 23, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=25, pady=(25, 15))

        list_frame = ctk.CTkScrollableFrame(
            window,
            fg_color=self.CARD,
            corner_radius=12,
            border_width=1,
            border_color=self.BORDER
        )
        list_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        selected_items = []

        visible_history = []

        for index, ticket in enumerate(history):
            pdf_path = ticket.get("pdf_path")
            qr_path = ticket.get("qr_path")

            if not pdf_path or not qr_path:
                continue

            if Path(pdf_path).is_file() and Path(qr_path).is_file():
                visible_history.append((index, ticket))

        if not visible_history:
            ctk.CTkLabel(
                list_frame,
                text="Історія талонів поки порожня.",
                font=("Arial", 14),
                text_color=self.MUTED
            ).pack(pady=30)

        else:
            for index, ticket in reversed(visible_history):
                number = ticket.get("number", "")

                if isinstance(number, int):
                    number_text = f"{number:06d}"
                else:
                    number_text = str(number)

                item_frame = ctk.CTkFrame(
                    list_frame,
                    fg_color=self.INPUT,
                    corner_radius=10,
                    border_width=1,
                    border_color=self.BORDER
                )
                item_frame.pack(fill="x", padx=8, pady=6)

                selected = tk.BooleanVar(value=False)
                selected_items.append((index, selected))

                checkbox = ctk.CTkCheckBox(
                    item_frame,
                    text="",
                    variable=selected,
                    width=24,
                    checkbox_width=22,
                    checkbox_height=22,
                    fg_color=self.BLUE,
                    hover_color=self.BLUE_HOVER
                )
                checkbox.pack(side="left", padx=(14, 8), pady=14)

                details = (
                    f"ТАЛОН № {number_text}\n"
                    f"Автомобіль: {ticket.get('vehicle', '')}\n"
                    f"Водій: {ticket.get('driver', '')}\n"
                    f"Менеджер: {ticket.get('manager', '')}\n"
                    f"Дата завантаження: {ticket.get('loading_date', '')}\n"
                    f"Час завантаження: {ticket.get('loading_time', '')}\n"
                    f"Створено: {ticket.get('creation_time', '')}"
                )

                ctk.CTkLabel(
                    item_frame,
                    text=details,
                    font=("Arial", 12),
                    text_color=self.TEXT,
                    justify="left",
                    anchor="w"
                ).pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=(4, 12),
                    pady=12
                )

        bottom_frame = ctk.CTkFrame(
            window,
            fg_color="transparent"
        )
        bottom_frame.pack(fill="x", padx=25, pady=(0, 20))

        def delete_selected():
            selected_indices = [
                index
                for index, variable in selected_items
                if variable.get()
            ]

            if not selected_indices:
                messagebox.showwarning(
                    "Нічого не вибрано",
                    "Виберіть записи, які потрібно видалити.",
                    parent=window
                )
                return

            confirm = messagebox.askyesno(
                "Підтвердження видалення",
                "Перемістити вибрані PDF-файли та QR-коди "
                "до Кошика Windows?\n\n",
                parent=window
            )

            if not confirm:
                return

            removed_count = 0
            failed_tickets = []

            # Обробляємо кожен талон окремо.
            for index in selected_indices:
                ticket = history[index]
                moved_files = []

                try:
                    for key in ("pdf_path", "qr_path"):
                        file_path = Path(ticket[key])

                        if not file_path.is_file():
                            raise FileNotFoundError(
                                f"Файл не знайдено: {file_path}"
                            )

                        send2trash(str(file_path))
                        moved_files.append(str(file_path))

                    removed_count += 1

                except Exception as error:
                    failed_tickets.append({
                        "number": ticket.get("number", "?"),
                        "error": str(error),
                        "moved_files": moved_files
                    })

            window.destroy()

            if failed_tickets:
                failed_text = "\n\n".join(
                    (
                        f"Талон № {item['number']}: {item['error']}"
                        + (
                            "\nДо Кошика вже переміщено: "
                            + ", ".join(item["moved_files"])
                            if item["moved_files"]
                            else ""
                        )
                    )
                    for item in failed_tickets
                )

                messagebox.showwarning(
                    "Часткове видалення",
                    f"Успішно переміщено талонів: {removed_count}.\n"
                    f"Проблемних талонів: {len(failed_tickets)}.\n\n"
                    f"{failed_text}",
                    parent=self.root
                )

            else:
                messagebox.showinfo(
                    "Видалення завершено",
                    f"Успішно переміщено талонів до Кошика: "
                    f"{removed_count}.\n\n"
                    "Записи збережені в історії. Після відновлення "
                    "PDF і QR-коду вони знову з'являться у списку.",
                    parent=self.root
                )

            self.show_history()

        ctk.CTkButton(
            bottom_frame,
            text="Видалити вибрані записи",
            height=42,
            font=("Arial", 13, "bold"),
            fg_color="#DC2626",
            hover_color="#B91C1C",
            corner_radius=10,
            command=delete_selected
        ).pack(side="left")

        ctk.CTkButton(
            bottom_frame,
            text="Закрити",
            height=42,
            font=("Arial", 13, "bold"),
            fg_color=self.BORDER,
            hover_color=self.MUTED,
            text_color=self.TEXT,
            corner_radius=10,
            command=window.destroy
        ).pack(side="right")

    def show_settings(self):
        window = ctk.CTkToplevel(self.root)
        set_window_icon(window)

        window.title("Налаштування підприємства")
        window.geometry("700x650")
        window.minsize(580, 500)
        window.configure(fg_color=self.BG)
        window.transient(self.root)
        window.grab_set()

        ctk.CTkLabel(
            window,
            text="Налаштування підприємства",
            font=("Arial", 22, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=25, pady=(22, 15))

        frame = ctk.CTkFrame(
            window,
            fg_color=self.CARD,
            corner_radius=14,
            border_width=1,
            border_color=self.BORDER
        )
        frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        content = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            corner_radius=0
        )
        content.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        fields = [
            ("company_name", "Назва підприємства"),
            ("company_address", "Адреса підприємства"),
            ("location", "Місце завантаження / координати"),
            ("footer_text", "Текст унизу талона")
        ]

        entries = {}

        for key, label_text in fields:
            ctk.CTkLabel(
                content,
                text=label_text,
                font=("Arial", 13, "bold"),
                text_color=self.TEXT
            ).pack(anchor="w", padx=15, pady=(12, 5))

            entry = ctk.CTkEntry(
                content,
                height=40,
                fg_color=self.INPUT,
                border_color=self.BORDER,
                text_color=self.TEXT,
                corner_radius=8
            )
            entry.pack(fill="x", padx=15)
            entry.insert(0, self.settings.get(key, ""))
            entries[key] = entry

        def save_changes():
            new_settings = self.settings.copy()

            for key, entry in entries.items():
                value = entry.get().strip()

                if not value:
                    messagebox.showwarning(
                        "Порожнє поле",
                        "Усі текстові поля налаштувань мають бути заповнені.",
                        parent=window
                    )
                    return

                new_settings[key] = value

            try:
                save_settings(new_settings)
                self.settings = new_settings

            except (OSError, TypeError, ValueError) as error:
                messagebox.showerror(
                    "Помилка збереження",
                    str(error),
                    parent=window
                )
                return

            messagebox.showinfo(
                "Збережено",
                "Налаштування підприємства оновлено.",
                parent=window
            )
            window.destroy()

        def restore_defaults():
            confirm = messagebox.askyesno(
                "Відновлення стандартних налаштувань",
                "Відновити стандартні налаштування?\n\n"
                "Інформація підприємства буде скинута "
                "до стандартних значень.",
                parent=window
            )

            if not confirm:
                return

            for key, entry in entries.items():
                entry.delete(0, "end")
                entry.insert(
                    0,
                    (
                        "https://www.google.com/maps?q=49.769589,28.730825"
                        if key == "location"
                        else DEFAULT_SETTINGS[key]
                    )
                )

            save_changes()

        ctk.CTkButton(
            frame,
            text="Відновлення стандартних налаштувань",
            height=42,
            font=("Arial", 13, "bold"),
            fg_color=self.BORDER,
            hover_color=self.MUTED,
            text_color=self.TEXT,
            corner_radius=10,
            command=restore_defaults
        ).pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkButton(
            frame,
            text="Зберегти налаштування",
            height=46,
            font=("Arial", 14, "bold"),
            fg_color=self.BLUE,
            hover_color=self.BLUE_HOVER,
            corner_radius=10,
            command=save_changes
        ).pack(fill="x", padx=20, pady=15)


def run_app():
    root = ctk.CTk()
    GeneratorApp(root)
    root.mainloop()