import html
import os
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

from local_data import create_backup, restore_backup


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "opdmanagement.settings")
BUNDLE_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
APP_DATA = Path(
    os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
) / "OPDPro"
DATABASE_PATH = APP_DATA / "db.sqlite3"
MEDIA_ROOT = APP_DATA / "media"
BACKUP_ROOT = APP_DATA / "backups"
WEBVIEW_DATA = APP_DATA / "webview"
for data_directory in (APP_DATA, MEDIA_ROOT, BACKUP_ROOT, WEBVIEW_DATA):
    data_directory.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("OPD_DATABASE_PATH", str(DATABASE_PATH))
os.environ.setdefault("OPD_MEDIA_ROOT", str(MEDIA_ROOT))
os.environ.setdefault("OPD_LOCAL_DESKTOP", "True")
os.environ.setdefault("DJANGO_DEBUG", "False")
os.environ.setdefault("ALLOWED_HOSTS", "127.0.0.1,localhost")

APP_URL = "http://127.0.0.1:8765/"
server_state = {"server": None, "thread": None}
server_lock = threading.Lock()
application_state = {"ready": False, "has_admin": False, "error": None}
application_lock = threading.Lock()


class QuietRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        return


def start_server():
    with server_lock:
        if server_state["server"] is not None:
            return

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
        server_state["server"] = server
        server_state["thread"] = thread


def stop_server():
    with server_lock:
        server = server_state["server"]
        thread = server_state["thread"]
        if server is None:
            return
        server_state["server"] = None
        server_state["thread"] = None

    server.shutdown()
    server.server_close()
    if thread:
        thread.join(timeout=5)


def initialize_application(window):
    try:
        import django
        from django.apps import apps
        from django.core.management import call_command
        from django.core.management.utils import get_random_secret_key

        secret_file = APP_DATA / "secret_key"
        try:
            secret_key = secret_file.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            secret_key = get_random_secret_key()
            secret_file.write_text(secret_key, encoding="utf-8")
        if not secret_key:
            raise RuntimeError(f"The secret key file is empty: {secret_file}")
        os.environ["SECRET_KEY"] = secret_key

        django.setup()
        call_command("migrate", interactive=False, verbosity=0)

        DrugMaster = apps.get_model("prescriptions", "DrugMaster")
        if not DrugMaster.objects.exists():
            drug_fixture = BUNDLE_ROOT / "prescriptions" / "fixtures" / "drug_master.json"
            if not drug_fixture.is_file():
                raise FileNotFoundError(f"The bundled medicine catalogue was not found: {drug_fixture}")
            call_command("loaddata", str(drug_fixture), verbosity=0)

        CustomUser = apps.get_model("usermanagement", "CustomUser")
        with application_lock:
            application_state["has_admin"] = CustomUser.objects.filter(is_superuser=True).exists()
            application_state["ready"] = True
        start_server()
        window.load_url(APP_URL)
    except Exception as error:
        with application_lock:
            application_state["error"] = str(error)
        window.load_html(
            "<!doctype html><html lang='en'><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>OPDPro could not start</title>"
            "<style>body{margin:0;background:#f5f8f6;color:#20342a;"
            "font:16px 'Segoe UI',sans-serif}.panel{max-width:620px;margin:12vh auto;"
            "padding:32px;background:white;border:1px solid #e1e9e3;border-radius:16px}"
            "h1{color:#155b3b}code{overflow-wrap:anywhere}</style>"
            "<main class='panel'><h1>OPDPro could not start</h1>"
            "<p>The clinic service did not finish starting. Close OPDPro and contact your "
            "administrator with this error:</p><code>"
            f"{html.escape(str(error))}</code></main></html>"
        )


class DesktopApi:
    def __init__(self):
        self.window = None
        self._operation_lock = threading.Lock()

    def get_status(self):
        with application_lock:
            return {
                "ready": application_state["ready"],
                "has_admin": application_state["has_admin"],
                "error": application_state["error"],
            }

    def create_administrator(self, first_name, last_name, email, password, confirm_password):
        if not self.get_status()["ready"]:
            return {"ok": False, "error": "Wait for OPDPro to finish starting."}
        first_name = first_name.strip()
        last_name = last_name.strip()
        email = email.strip()
        if not all((first_name, last_name, email, password)):
            return {"ok": False, "error": "Enter your name, email and password."}
        if password != confirm_password:
            return {"ok": False, "error": "Enter the same password in both fields."}
        if len(password) < 12:
            return {"ok": False, "error": "Use a password with at least 12 characters."}

        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        from usermanagement.models import CustomUser

        if CustomUser.objects.filter(email__iexact=email).exists():
            return {"ok": False, "error": "That email address is already in use."}
        account = CustomUser(
            email=email,
            first_name=first_name,
            last_name=last_name,
            staff_role="admin",
        )
        try:
            account.full_clean(exclude=("password",))
            validate_password(password, user=account)
        except ValidationError as error:
            return {"ok": False, "error": " ".join(error.messages)}

        with application_lock:
            if CustomUser.objects.filter(is_superuser=True).exists():
                return {"ok": False, "error": "A clinic administrator has already been created."}
            CustomUser.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                staff_role="admin",
            )
            application_state["has_admin"] = True
        return {"ok": True}

    @staticmethod
    def _selected_path(selection):
        if not selection:
            return None
        return selection[0] if isinstance(selection, (list, tuple)) else selection

    def create_backup(self):
        import webview

        folder = self._selected_path(
            self.window.create_file_dialog(
                webview.FileDialog.FOLDER,
                directory=str(
                    (Path.home() / "Documents")
                    if (Path.home() / "Documents").is_dir()
                    else APP_DATA
                ),
            )
        )
        if not folder:
            return {"cancelled": True}
        if not self._operation_lock.acquire(blocking=False):
            raise RuntimeError("Wait for the current clinic data operation to finish.")
        try:
            from django.conf import settings

            destination = Path(folder) / f"OPDPro-backup-{datetime.now():%Y%m%d-%H%M%S-%f}.zip"
            create_backup(settings.DATABASES["default"]["NAME"], settings.MEDIA_ROOT, destination)
            return {"cancelled": False, "path": str(destination)}
        finally:
            self._operation_lock.release()

    def select_restore_backup(self):
        import webview

        selected = self._selected_path(
            self.window.create_file_dialog(
                webview.FileDialog.OPEN,
                directory=str(BACKUP_ROOT),
                allow_multiple=False,
                file_types=("OPDPro backup (*.zip)",),
            )
        )
        return {"cancelled": not selected, "path": str(selected) if selected else ""}

    def restore_backup(self, archive_path):
        if not self._operation_lock.acquire(blocking=False):
            raise RuntimeError("Wait for the current clinic data operation to finish.")
        try:
            from django.conf import settings
            from django.core.management import call_command
            from django.db import connections

            backup_path = Path(archive_path)
            if not backup_path.is_file():
                raise FileNotFoundError("The selected OPDPro backup could not be found.")
            safety_backup = BACKUP_ROOT / (
                f"OPDPro-before-restore-{datetime.now():%Y%m%d-%H%M%S-%f}.zip"
            )
            create_backup(
                settings.DATABASES["default"]["NAME"],
                settings.MEDIA_ROOT,
                safety_backup,
            )
            connections.close_all()
            stop_server()
            try:
                restore_backup(backup_path, settings.DATABASES["default"]["NAME"], settings.MEDIA_ROOT)
                call_command("migrate", interactive=False, verbosity=0)
                from usermanagement.models import CustomUser

                with application_lock:
                    application_state["has_admin"] = CustomUser.objects.filter(
                        is_superuser=True
                    ).exists()
            except Exception as error:
                try:
                    call_command("migrate", interactive=False, verbosity=0)
                    start_server()
                except Exception as startup_error:
                    raise RuntimeError(
                        f"{error}\n\nThe local clinic service could not restart: {startup_error}"
                    ) from error
                raise
            start_server()
            return {"safety_backup": str(safety_backup)}
        finally:
            self._operation_lock.release()

    @staticmethod
    def open_data_folder():
        if sys.platform == "win32":
            os.startfile(APP_DATA)
        else:
            webbrowser.open(APP_DATA.as_uri())


def show_startup_error(error):
    if sys.platform == "win32":
        import ctypes

        ctypes.windll.user32.MessageBoxW(
            None,
            f"OPDPro could not open its application window.\n\n{error}",
            "OPDPro could not start",
            0x10,
        )
    else:
        print(f"OPDPro could not start: {error}", file=sys.stderr)


def main():
    try:
        import webview

        api = DesktopApi()
        window = webview.create_window(
            "OPDPro Clinic",
            html=(
                "<!doctype html><html lang='en'><meta charset='utf-8'>"
                "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                "<title>OPDPro</title><style>body{margin:0;display:grid;min-height:100vh;"
                "place-items:center;background:#f5f8f6;color:#155b3b;"
                "font:16px 'Segoe UI',sans-serif}.loading{text-align:center}"
                ".mark{font-size:30px;font-weight:700}.hint{color:#687970}</style>"
                "<main class='loading'><div class='mark'>OPDPro</div>"
                "<p>Preparing your clinic workspace…</p>"
                "<p class='hint'>Your clinic records stay on this computer.</p></main></html>"
            ),
            js_api=api,
            width=1360,
            height=900,
            min_size=(1024, 700),
            confirm_close=True,
            background_color="#f5f8f6",
        )
        api.window = window
        webview.start(
            initialize_application,
            args=(window,),
            gui="edgechromium",
            private_mode=False,
            storage_path=str(WEBVIEW_DATA),
        )
    except Exception as error:
        show_startup_error(error)
    finally:
        stop_server()


if __name__ == "__main__":
    main()
