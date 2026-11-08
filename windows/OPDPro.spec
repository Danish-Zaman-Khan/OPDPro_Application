from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

ROOT = Path(SPECPATH).resolve().parent
DATA_DIRS = [
    (ROOT / "templates", "templates"),
    (ROOT / "static", "static"),
    (ROOT / "prescriptions" / "fixtures", "prescriptions/fixtures"),
]
datas = [(str(source), target) for source, target in DATA_DIRS if source.exists()]
for package in ("django", "rest_framework", "rest_framework_simplejwt", "corsheaders", "widget_tweaks", "webview"):
    datas.extend(collect_data_files(package))

for package in ("Django", "djangorestframework", "djangorestframework-simplejwt", "django-cors-headers", "django-widget-tweaks", "python-dotenv", "Pillow", "pywebview"):
    datas.extend(copy_metadata(package))

APP_MODULES = (
    "opdmanagement",
    "appointment",
    "billing",
    "doctors",
    "patients",
    "prescriptions",
    "reports",
    "settings",
    "user_notifications",
    "usermanagement",
)
hiddenimports = list(collect_submodules("django"))
for module in (*APP_MODULES, "rest_framework", "rest_framework_simplejwt", "corsheaders", "widget_tweaks", "PIL", "webview"):
    hiddenimports.extend(collect_submodules(module))

analysis = Analysis(
    [str(ROOT / "desktop_launcher.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "IPython"],
    noarchive=False,
    optimize=1,
)
python_archive = PYZ(analysis.pure)
executable = EXE(
    python_archive,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="OPDPro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
