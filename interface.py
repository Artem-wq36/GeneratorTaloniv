
import shutil
import tkinter as tk

from datetime import datetime
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

from settings import (
    LOGOS_DIR,
    load_settings,
    save_settings
)

from history import (
    get_next_number,
    load_history,
    save_ticket
)

from pdf_generator import generate_pdf


class GeneratorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Генератор електронних талонів")
        self.root.geometry("600x520")
        self.root.minsize(520, 480)

        self.settings = load_settings()

        self.create_interface()

    def create_interface(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        title = ttk.Label(
            main_frame,
            text="ГЕНЕРАТОР ЕЛЕКТРОННИХ ТАЛОНІВ",
            font=("Arial", 15, "bold")
        )
        title.pack(pady=(0, 20))

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x")

        self.vehicle_entry = self.add_field(
            form_frame,
            "Номер транспортного засобу:",
            0
        )

        self.driver_entry = self.add_field(
            form_frame,
            "Ім'я водія:",
            1
        )

        self.manager_entry = self.add_field(
            form_frame,
            "Контакт менеджера:",
            2
        )

        self.date_entry = self.add_field(
            form_frame,
            "Дата завантаження (ДД.ММ.РРРР):",
            3
        )

        self.time_entry = self.add_field(
            form_frame,
            "Час завантаження (ГГ:ХХ):",
            4
        )

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=25)

        ttk.Button(
            buttons_frame,
            text="Згенерувати PDF",
            command=self.create_ticket
        ).pack(fill="x", pady=5)

        ttk.Button(
            buttons_frame,
            text="Переглянути історію",
            command=self.show_history
        ).pack(fill="x", pady=5)

        ttk.Button(
            buttons_frame,
            text="Налаштування підприємства",
            command=self.show_settings
        ).pack(fill="x", pady=5)

        self.status_label = ttk.Label(
            main_frame,
            text="Програма готова до роботи.",
            foreground="green"
        )
        self.status_label.pack(pady=10)

    def add_field(self, parent, label_text, row):
        ttk.Label(
            parent,
            text=label_text
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=7
        )

        entry = ttk.Entry(parent, width=35)
        entry.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(10, 0),
            pady=7
        )

        parent.columnconfigure(1, weight=1)

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

        self.status_label.config(
            text=f"Талон № {number:06d} успішно створено.",
            foreground="green"
        )

        messagebox.showinfo(
            "Успішно",
            f"Талон № {number:06d} створено!\n\n"
            f"PDF:\n{output_path}\n\n"
            f"QR-код:\n{qr_path}"
        )

    def show_history(self):
        history = load_history()

        window = tk.Toplevel(self.root)
        window.title("Історія талонів")
        window.geometry("750x500")

        frame = ttk.Frame(window, padding=10)
        frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            frame,
            wrap="word",
            font=("Arial", 10),
            yscrollcommand=scrollbar.set
        )

        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)

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
                    f"{'-' * 55}\n\n"
                )

        text.config(state="disabled")

    def show_settings(self):
        window = tk.Toplevel(self.root)
        window.title("Налаштування підприємства")
        window.geometry("550x390")
        window.resizable(False, False)

        frame = ttk.Frame(window, padding=20)
        frame.pack(fill="both", expand=True)

        entries = {}

        fields = [
            ("company_name", "Назва підприємства:"),
            ("company_address", "Адреса підприємства:"),
            ("location", "Місце завантаження / координати:"),
            ("footer_text", "Текст унизу талона:")
        ]

        for row, (key, label_text) in enumerate(fields):
            ttk.Label(
                frame,
                text=label_text
            ).grid(
                row=row,
                column=0,
                sticky="w",
                pady=8
            )

            entry = ttk.Entry(frame, width=42)
            entry.grid(
                row=row,
                column=1,
                sticky="ew",
                padx=(10, 0),
                pady=8
            )

            entry.insert(0, self.settings.get(key, ""))
            entries[key] = entry

        logo_var = tk.StringVar(
            value=Path(self.settings.get("logo_file", "")).name
            if self.settings.get("logo_file", "")
            else ""
        )

        ttk.Label(
            frame,
            text="Логотип:"
        ).grid(
            row=4,
            column=0,
            sticky="w",
            pady=8
        )

        logo_label = ttk.Label(
            frame,
            text=logo_var.get() or "Не вибрано",
            width=30
        )

        logo_label.grid(
            row=4,
            column=1,
            sticky="w",
            padx=(10, 0)
        )

        selected_logo = {"path": None}
        clear_logo = {"value": False}

        def choose_logo():
            path = filedialog.askopenfilename(
                title="Вибрати логотип",
                filetypes=[
                    ("Зображення", "*.png *.jpg *.jpeg")
                ]
            )

            if path:
                selected_logo["path"] = path
                clear_logo["value"] = False
                logo_var.set(Path(path).name)
                logo_label.config(text=Path(path).name)

        def remove_logo():
            selected_logo["path"] = None
            clear_logo["value"] = True
            logo_var.set("")
            logo_label.config(text="Не вибрано")

        logo_buttons = ttk.Frame(frame)
        logo_buttons.grid(
            row=5,
            column=1,
            sticky="w",
            padx=(10, 0)
        )

        ttk.Button(
            logo_buttons,
            text="Вибрати",
            command=choose_logo
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            logo_buttons,
            text="Прибрати",
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

            except OSError as error:
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

        ttk.Button(
            frame,
            text="Зберегти налаштування",
            command=save_changes
        ).grid(
            row=6,
            column=0,
            columnspan=2,
            pady=25
        )

        frame.columnconfigure(1, weight=1)


def run_app():
    root = tk.Tk()
    GeneratorApp(root)
    root.mainloop()