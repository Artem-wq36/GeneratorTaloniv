import shutil
import tkinter as tk
import customtkinter as ctk

from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

from settings import LOGOS_DIR, load_settings, save_settings
from history import get_next_number, load_history, save_ticket
from pdf_generator import generate_pdf


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GeneratorApp:

    BG = "#111827"
    CARD = "#1F2937"
    INPUT = "#111827"
    BORDER = "#374151"
    TEXT = "#F9FAFB"
    MUTED = "#9CA3AF"
    BLUE = "#2563EB"
    BLUE_HOVER = "#1D4ED8"
    GREEN = "#22C55E"

    def __init__(self, root):
        self.root = root
        self.root.title("GeneratorTaloniv")
        self.root.geometry("900x760")
        self.root.minsize(760, 680)
        self.root.configure(fg_color=self.BG)

        self.settings = load_settings()

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

        date_time_frame = ctk.CTkFrame(
            fields_frame,
            fg_color="transparent"
        )
        date_time_frame.pack(fill="x", pady=(0, 12))
        date_time_frame.grid_columnconfigure((0, 1), weight=1)

        date_frame = ctk.CTkFrame(
            date_time_frame,
            fg_color="transparent"
        )
        date_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 10)
        )

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
        time_frame.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(10, 0)
        )

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
            fg_color=self.INPUT,
            border_color=self.BORDER,
            text_color=self.TEXT,
            placeholder_text_color=self.MUTED,
            corner_radius=9
        )
        self.time_entry.pack(fill="x")

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
            text="📋  Переглянути історію",
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
            text="⚙  Налаштування підприємства",
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
                "Будь ласка, заповніть усі поля."
            )
            return

        try:
            datetime.strptime(loading_date, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror(
                "Помилка дати",
                "Введіть дату у форматі ДД.ММ.РРРР."
            )
            return

        try:
            datetime.strptime(loading_time, "%H:%M")
        except ValueError:
            messagebox.showerror(
                "Помилка часу",
                "Введіть час у форматі ГГ:ХХ, наприклад 09:30."
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
            initialdir=last_folder
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
                f"Не вдалося запам'ятати папку:\n{error}"
            )

        number = get_next_number()

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

        output_path = pdf_folder / f"talon_{number:06d}.pdf"
        qr_path = qr_folder / f"qr_{number:06d}.png"

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
                f"Не вдалося створити талон:\n{error}"
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
                f"записати його в історію.\n\n{error}"
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
            f"QR-код:\n{qr_path}"
        )

    def show_history(self):
        history = load_history()

        window = ctk.CTkToplevel(self.root)
        window.title("Історія талонів")
        window.geometry("800x600")
        window.minsize(600, 400)
        window.configure(fg_color=self.BG)

        ctk.CTkLabel(
            window,
            text="Історія талонів",
            font=("Arial", 23, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=25, pady=(25, 15))

        text = ctk.CTkTextbox(
            window,
            font=("Arial", 13),
            fg_color=self.CARD,
            text_color=self.TEXT,
            border_width=1,
            border_color=self.BORDER,
            corner_radius=12,
            wrap="word"
        )
        text.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        if not history:
            text.insert("end", "Історія талонів поки порожня.")

        else:
            for ticket in reversed(history):
                number = ticket.get("number", "")

                if isinstance(number, int):
                    number_text = f"{number:06d}"
                else:
                    number_text = str(number)

                text.insert(
                    "end",
                    f"ТАЛОН № {number_text}\n"
                )

                text.insert(
                    "end",
                    f"Автомобіль: {ticket.get('vehicle', '')}\n"
                    f"Водій: {ticket.get('driver', '')}\n"
                    f"Менеджер: {ticket.get('manager', '')}\n"
                    f"Дата завантаження: {ticket.get('loading_date', '')}\n"
                    f"Час завантаження: {ticket.get('loading_time', '')}\n"
                    f"Створено: {ticket.get('creation_time', '')}\n"
                    f"PDF: {ticket.get('pdf_path', '')}\n"
                    f"QR-код: {ticket.get('qr_path', '')}\n"
                    f"{'-' * 65}\n\n"
                )

        text.configure(state="disabled")

    def show_settings(self):
        window = ctk.CTkToplevel(self.root)
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

        current_logo = self.settings.get("logo_file", "")
        logo_var = tk.StringVar(
            value=Path(current_logo).name if current_logo else ""
        )

        ctk.CTkLabel(
            content,
            text="Логотип підприємства",
            font=("Arial", 13, "bold"),
            text_color=self.TEXT
        ).pack(anchor="w", padx=15, pady=(18, 5))

        logo_label = ctk.CTkLabel(
            content,
            text=logo_var.get() or "Не вибрано",
            text_color=self.MUTED
        )
        logo_label.pack(anchor="w", padx=15, pady=(0, 8))

        selected_logo = {"path": None}
        clear_logo = {"value": False}

        def choose_logo():
            path = filedialog.askopenfilename(
                parent=window,
                title="Вибрати логотип",
                filetypes=[("Зображення", "*.png *.jpg *.jpeg")]
            )

            if path:
                selected_logo["path"] = path
                clear_logo["value"] = False
                logo_var.set(Path(path).name)
                logo_label.configure(text=Path(path).name)

        def remove_logo():
            selected_logo["path"] = None
            clear_logo["value"] = True
            logo_var.set("")
            logo_label.configure(text="Не вибрано")

        logo_buttons = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        logo_buttons.pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkButton(
            logo_buttons,
            text="Вибрати",
            width=110,
            height=35,
            command=choose_logo
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            logo_buttons,
            text="Прибрати",
            width=110,
            height=35,
            fg_color="#374151",
            hover_color="#4B5563",
            command=remove_logo
        ).pack(side="left")

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

            if clear_logo["value"]:
                new_settings["logo_file"] = ""

            elif selected_logo["path"]:
                source = Path(selected_logo["path"])
                extension = source.suffix.lower()

                if extension not in [".png", ".jpg", ".jpeg"]:
                    messagebox.showerror(
                        "Непідтримуваний формат",
                        "Виберіть PNG, JPG або JPEG.",
                        parent=window
                    )
                    return

                destination = LOGOS_DIR / f"company_logo{extension}"

                try:
                    LOGOS_DIR.mkdir(parents=True, exist_ok=True)

                    if source.resolve() != destination.resolve():
                        shutil.copy2(source, destination)

                    new_settings["logo_file"] = str(destination)

                except OSError as error:
                    messagebox.showerror(
                        "Помилка логотипа",
                        str(error),
                        parent=window
                    )
                    return

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
