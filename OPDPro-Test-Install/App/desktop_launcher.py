import os
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

from local_data import create_backup, restore_backup


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "opdmanagement.settings")
APP_DATA = Path(
    os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
) / "OPDPro"
APP_DATA.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = APP_DATA / "db.sqlite3"
MEDIA_ROOT = APP_DATA / "media"
BACKUP_ROOT = APP_DATA / "backups"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("OPD_DATABASE_PATH", str(DATABASE_PATH))
os.environ.setdefault("OPD_MEDIA_ROOT", str(MEDIA_ROOT))
os.environ.setdefault("OPD_LOCAL_DESKTOP", "True")
os.environ.setdefault("DJANGO_DEBUG", "False")
os.environ.setdefault("ALLOWED_HOSTS", "127.0.0.1,localhost")


class QuietRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        return


def main():
    root = tk.Tk()
    root.title("OPDPro Clinic")
    root.geometry("570x470")
    root.minsize(520, 430)
    root.configure(background="#f5f8f6")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background="#f5f8f6")
    style.configure("TLabel", background="#f5f8f6", foreground="#24372d", font=("Segoe UI", 10))
    style.configure("Title.TLabel", foreground="#155b3b", font=("Segoe UI", 23, "bold"))
    style.configure("Hint.TLabel", foreground="#5e7066", font=("Segoe UI", 9))
    style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
    style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 9))

    server_holder = {"server": None, "thread": None}
    initialized = {"ready": False}
    operation = {"active": False}
    url = "http://127.0.0.1:8765/"

    ttk.Label(root, text="OPDPro", style="Title.TLabel").pack(pady=(24, 2))
    ttk.Label(root, text="Your clinic, organised.", style="Hint.TLabel").pack()
    status = ttk.Label(root, text="Preparing your clinic database…", wraplength=480)
    status.pack(pady=(18, 12))

    setup_button = ttk.Button(root, text="Create clinic administrator", style="Accent.TButton", state="disabled")
    setup_button.pack(pady=5)

    actions = ttk.Frame(root)
    actions.pack(pady=8)
    open_button = ttk.Button(actions, text="Open OPDPro", state="disabled")
    backup_button = ttk.Button(actions, text="Create backup", state="disabled")
    restore_button = ttk.Button(actions, text="Restore backup", state="disabled")
    open_button.grid(row=0, column=0, padx=4, pady=4)
    backup_button.grid(row=0, column=1, padx=4, pady=4)
    restore_button.grid(row=0, column=2, padx=4, pady=4)

    data_button = ttk.Button(root, text="Open clinic data folder", state="disabled")
    data_button.pack(pady=(4, 8))
    ttk.Label(
        root,
        text="Clinic records stay on this computer. Backups contain patient data; save them only to a secure location.",
        style="Hint.TLabel",
        wraplength=465,
        justify="center",
    ).pack(padx=28, pady=(4, 12))

    def show_error(title, error):
        status.configure(text="OPDPro could not complete that action. See the details below.")
        messagebox.showerror(title, str(error), parent=root)

    def open_clinic():
        webbrowser.open_new(url)

    def start_server():
        if server_holder["server"] is not None:
            return
        try:
            from django.contrib.staticfiles.handlers import StaticFilesHandler
            from django.core.wsgi import get_wsgi_application

            application = StaticFilesHandler(get_wsgi_application())
            server = make_server(
                "127.0.0.1",
                8765,
                application,
                server_class=WSGIServer,
                handler_class=QuietRequestHandler,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            server_holder["server"] = server
            server_holder["thread"] = thread
            open_button.configure(state="normal")
            backup_button.configure(state="normal")
            restore_button.configure(state="normal")
            data_button.configure(state="normal")
            setup_button.configure(state="disabled")
            status.configure(text="Your clinic is ready. OPDPro opens in your browser.")
            open_clinic()
        except Exception as error:
            show_error("The local clinic server could not start", error)

    def stop_server():
        server = server_holder["server"]
        if server is None:
            return
        server.shutdown()
        server.server_close()
        thread = server_holder["thread"]
        if thread:
            thread.join(timeout=5)
        server_holder["server"] = None
        server_holder["thread"] = None

    def create_administrator():
        if not initialized["ready"]:
            return
        dialog = tk.Toplevel(root)
        dialog.title("Set up your clinic")
        dialog.resizable(False, False)
        dialog.transient(root)
        dialog.grab_set()
        frame = ttk.Frame(dialog, padding=22)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Create your clinic administrator", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 5)
        )
        ttk.Label(
            frame,
            text="Use this account to sign in and add other clinic staff.",
            style="Hint.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))

        fields = {}
        labels = (("First name", "first_name"), ("Last name", "last_name"), ("Email", "email"), ("Password", "password"), ("Confirm password", "confirm"))
        for row, (label, key) in enumerate(labels, start=2):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 16))
            entry = ttk.Entry(frame, width=34, show="*" if key in {"password", "confirm"} else "")
            entry.grid(row=row, column=1, sticky="ew", pady=5)
            fields[key] = entry
        frame.columnconfigure(1, weight=1)

        def save_administrator():
            first_name = fields["first_name"].get().strip()
            last_name = fields["last_name"].get().strip()
            email = fields["email"].get().strip()
            password = fields["password"].get()
            if not all((first_name, last_name, email, password)):
                messagebox.showwarning("Complete all fields", "Enter your name, email and password.", parent=dialog)
                return
            if password != fields["confirm"].get():
                messagebox.showwarning("Passwords do not match", "Enter the same password in both fields.", parent=dialog)
                return
            if len(password) < 12:
                messagebox.showwarning("Choose a stronger password", "Use at least 12 characters.", parent=dialog)
                return
            try:
                from django.contrib.auth.password_validation import validate_password
                from django.core.exceptions import ValidationError
                from usermanagement.models import CustomUser

                if CustomUser.objects.filter(email__iexact=email).exists():
                    messagebox.showwarning("Email already exists", "Use another email address or contact your administrator.", parent=dialog)
                    return
                account = CustomUser(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    staff_role="admin",
                )
                try:
                    account.full_clean(exclude=("password",))
                except ValidationError as error:
                    messagebox.showwarning(
                        "Check the account details",
                        "\n".join(error.messages),
                        parent=dialog,
                    )
                    return
                try:
                    validate_password(password, user=account)
                except ValidationError as error:
                    messagebox.showwarning(
                        "Choose a stronger password",
                        "\n".join(error.messages),
                        parent=dialog,
                    )
                    return
                CustomUser.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    staff_role="admin",
                )
            except Exception as error:
                show_error("Administrator account could not be created", error)
                return
            dialog.destroy()
            start_server()

        ttk.Button(frame, text="Create administrator", style="Accent.TButton", command=save_administrator).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=(16, 0)
        )
        fields["first_name"].focus_set()

    def initialize_application():
        try:
            import django
            from django.apps import apps
            from django.core.management import call_command
            from django.core.management.utils import get_random_secret_key

            secret_file = APP_DATA / "secret_key"
            if not os.environ.get("SECRET_KEY"):
                try:
                    secret_key = secret_file.read_text(encoding="utf-8").strip()
                except FileNotFoundError:
                    secret_key = get_random_secret_key()
                    secret_file.write_text(secret_key, encoding="utf-8")
                if not secret_key:
                    raise RuntimeError(f"The secret key file is empty: {secret_file}")
                os.environ["SECRET_KEY"] = secret_key

            os.environ.setdefault("DJANGO_DEBUG", "False")
            os.environ.setdefault("ALLOWED_HOSTS", "127.0.0.1,localhost")
            os.environ.setdefault("OPD_LOCAL_DESKTOP", "True")
            django.setup()
            call_command("migrate", interactive=False, verbosity=0)

            DrugMaster = apps.get_model("prescriptions", "DrugMaster")
            if not DrugMaster.objects.exists():
                call_command("loaddata", "prescriptions/fixtures/drug_master.json", verbosity=0)

            CustomUser = apps.get_model("usermanagement", "CustomUser")
            has_admin = CustomUser.objects.filter(is_superuser=True).exists()
            initialized["ready"] = True
            root.after(0, lambda: on_initialized(has_admin))
        except Exception as error:
            root.after(0, lambda error=error: show_error("OPDPro could not start", error))

    def on_initialized(has_admin):
        if has_admin:
            start_server()
        else:
            status.configure(text="One-time setup: create the clinic administrator account.")
            setup_button.configure(state="normal", command=create_administrator)

    def choose_backup_folder():
        return filedialog.askdirectory(
            title="Choose a secure backup location",
            initialdir=str(Path.home() / "Documents"),
            parent=root,
        )

    def create_backup_now():
        folder = choose_backup_folder()
        if not folder:
            return
        from datetime import datetime

        destination = Path(folder) / f"OPDPro-backup-{datetime.now():%Y%m%d-%H%M%S}.zip"
        operation["active"] = True
        backup_button.configure(state="disabled")
        status.configure(text="Creating a consistent database and reports backup…")

        def work():
            try:
                from django.conf import settings

                create_backup(settings.DATABASES["default"]["NAME"], settings.MEDIA_ROOT, destination)
                root.after(0, lambda: on_backup_complete(destination))
            except Exception as error:
                root.after(0, lambda error=error: on_backup_failed(error))

        threading.Thread(target=work, daemon=True).start()

    def on_backup_complete(destination):
        operation["active"] = False
        backup_button.configure(state="normal")
        status.configure(text=f"Backup saved to: {destination}")
        messagebox.showinfo("Backup complete", f"Clinic data was backed up to:\n{destination}", parent=root)

    def on_backup_failed(error):
        operation["active"] = False
        backup_button.configure(state="normal")
        show_error("Backup could not be created", error)

    def restore_backup_now():
        archive_path = filedialog.askopenfilename(
            title="Select an OPDPro backup",
            filetypes=(("OPDPro backup", "*.zip"), ("All files", "*.*")),
            parent=root,
        )
        if not archive_path:
            return
        confirmed = messagebox.askyesno(
            "Replace clinic data?",
            "Restoring replaces the current database and uploaded reports with the selected backup. "
            "A safety backup of the current data will be created first. Continue?",
            icon="warning",
            parent=root,
        )
        if not confirmed:
            return
        backup_folder = choose_backup_folder()
        if not backup_folder:
            return

        from datetime import datetime

        safety_backup = Path(backup_folder) / f"OPDPro-before-restore-{datetime.now():%Y%m%d-%H%M%S}.zip"
        operation["active"] = True
        backup_button.configure(state="disabled")
        restore_button.configure(state="disabled")
        status.configure(text="Creating a safety backup before restore…")

        def work():
            try:
                from django.conf import settings
                from django.core.management import call_command

                create_backup(settings.DATABASES["default"]["NAME"], settings.MEDIA_ROOT, safety_backup)
                stop_server()
                restore_backup(archive_path, settings.DATABASES["default"]["NAME"], settings.MEDIA_ROOT)
                call_command("migrate", interactive=False, verbosity=0)
                root.after(0, lambda: on_restore_complete())
            except Exception as error:
                root.after(0, lambda error=error: on_restore_failed(error))

        threading.Thread(target=work, daemon=True).start()

    def on_restore_complete():
        operation["active"] = False
        start_server()
        backup_button.configure(state="normal")
        restore_button.configure(state="normal")
        messagebox.showinfo("Restore complete", "The clinic data was restored successfully.", parent=root)

    def on_restore_failed(error):
        operation["active"] = False
        try:
            from django.core.management import call_command

            call_command("migrate", interactive=False, verbosity=0)
            root.after(0, start_server)
        except Exception as startup_error:
            error = RuntimeError(f"{error}\n\nThe local server could not restart: {startup_error}")
        backup_button.configure(state="normal")
        restore_button.configure(state="normal")
        show_error("Restore could not be completed", error)

    def open_data_folder():
        try:
            if sys.platform == "win32":
                os.startfile(APP_DATA)
            else:
                webbrowser.open(APP_DATA.as_uri())
        except Exception as error:
            show_error("Clinic data folder could not be opened", error)

    def close_app():
        if operation["active"]:
            messagebox.showinfo(
                "Please wait",
                "Wait for the backup or restore operation to finish before closing OPDPro.",
                parent=root,
            )
            return
        try:
            stop_server()
        except Exception as error:
            show_error("Server could not be stopped cleanly", error)
            return
        root.destroy()

    open_button.configure(command=open_clinic)
    backup_button.configure(command=create_backup_now)
    restore_button.configure(command=restore_backup_now)
    data_button.configure(command=open_data_folder)
    root.protocol("WM_DELETE_WINDOW", close_app)
    threading.Thread(target=initialize_application, daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    main()
