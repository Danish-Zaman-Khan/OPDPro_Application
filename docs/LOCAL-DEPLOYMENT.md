# Local deployment and clinic setup

This guide covers the Windows desktop release for clinic staff and a source-based setup for developers. The desktop server listens only on the clinic computer (`127.0.0.1`). The installed app stores the database and uploaded reports in the signed-in Windows user's local application data folder.

> **Scope:** This is a local, single-clinic Windows deployment, not an internet-hosted or multi-computer service. Do not expose its local server to the internet or clinic network. Keep the computer access-controlled and make regular backups to a secure, separate location.

## Install OPDPro on Windows

The end user does not need to install Python or run terminal commands. Prefer the GUI installer when the release includes it; the ZIP-based installer is also available.

1. Obtain the OPDPro Windows release from your clinic administrator or software provider. Only install releases from a source you trust.
2. If the release contains `OPDPro-Setup.exe`, double-click it and follow the setup wizard. Otherwise, extract the complete ZIP and double-click `install_windows.bat`. Both options install per-user without administrator privileges, and create Start menu and desktop shortcuts.
3. Open OPDPro from its shortcut. The OPDPro launcher starts the local service but waits for you to select **Open OPDPro** before opening a browser. On first launch, create the clinic administrator using the on-screen setup form. Choose a unique password with at least 12 characters.
4. In the launcher, select **Open OPDPro**. Sign in with the administrator account and add staff accounts through **Admin tools**. Do not share accounts. Passwords are stored as Django password hashes; the application does not save the sign-in password in plain text.
5. On the sign-in page, **Keep me signed in on this computer for 14 days** is optional. Leave it unchecked on a shared Windows account. Sign out from the profile menu when finished; the signed-out confirmation page provides a clear way back to sign-in.

The app and its data are kept separately. Reinstalling or replacing the application does not remove clinic records. The database and uploaded files are stored under `%LOCALAPPDATA%\OPDPro`; use **Open clinic data folder** in the launcher to view that location. Do not delete it when updating or uninstalling the app.

In the launcher, **Create backup** saves a ZIP containing a consistent SQLite database snapshot and uploaded reports. Choose a secure, preferably encrypted removable drive or other clinic-controlled backup location. These archives are not themselves encrypted and contain sensitive patient information. Keep multiple dated backups and periodically test recovery with **Restore backup**. Restore replaces current records and reports; the launcher prompts for confirmation and creates a safety backup before replacement.

To update, close OPDPro, install the new trusted release over the existing application, then reopen it. The installer will update the app files and shortcuts without changing the clinic data folder. Make a backup before updating. To uninstall, use **Settings → Apps → Installed apps → OPDPro**. Uninstalling removes the app and shortcuts but deliberately preserves clinic records and backups under `%LOCALAPPDATA%\OPDPro`.

The Windows distributable is built on Windows using `windows/build_windows.ps1`. With Inno Setup 6 installed, the build produces both `windows/dist/OPDPro-Setup.exe` (recommended) and `windows/dist/OPDPro-Test-Install-Windows.zip`; without Inno Setup it produces the ZIP-based installer only. The build has to be produced and tested on Windows before sharing it; a source checkout or an old test ZIP is not a substitute for a freshly built release.

The project does not currently sign the Windows executable or installer with an Authenticode certificate, so Windows SmartScreen may show an unverified-publisher warning. Distribute only through a trusted channel; broad clinic distribution should use a properly code-signed release.

## 1. Before you begin

For source-based developer setup, you need:

- Python 3.11, 3.12, or 3.13 available from a terminal.
- A terminal account that can create files in the project directory.
- Internet access to install Python packages and load the Bootstrap styles and icons used by the web UI.
- A clinic-owned computer with OS login protection, disk encryption where available, automatic screen lock, current security updates, and a plan for encrypted backups.

Keep the project in a stable, private directory. Do not install it in a shared/public folder. The app stores its SQLite database at `db.sqlite3` and uploaded reports under `media/` by default.

## Developer setup: create and activate a virtual environment

Run commands from the repository root (the directory containing `manage.py` and `requirements.txt`).

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Replace `3.11` with `3.12` or `3.13` if that is the Python version installed on the computer.

If PowerShell blocks activation, use the Python executable directly for the remaining commands:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install packages and configure the local environment

With the virtual environment active:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a private `.env` file from the example:

```text
Copy .env.example to .env
```

On macOS/Linux, the copy command is `cp .env.example .env`. In PowerShell, use `Copy-Item .env.example .env`.

Generate a new Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Edit `.env` and paste the generated value after `SECRET_KEY=`. Do not reuse the example, commit `.env`, share it, or use a key copied from another installation. `.env` is ignored by Git.

The example enables `DJANGO_DEBUG=True` only for local, same-computer use and allows only `localhost` and `127.0.0.1`. Keep those values for this guide. Do not set `ALLOWED_HOSTS=*` or expose this development server to the clinic LAN.

### Create the database and initial administrator

```bash
python manage.py check
python manage.py migrate
python manage.py loaddata prescriptions/fixtures/drug_master.json
python manage.py createsuperuser
```

The medicine fixture is optional; it loads the included starter catalogue and can be skipped. Create a separate account for each person who will use the application. Do not share the administrator login.

For clinic staff accounts, sign in with the administrator account and use **Admin tools** at `/admin/` to manage accounts and clinic configuration. Only accounts with Django staff access can use Admin tools; a role label alone does not grant access. Admin pages include a **Return to OPDPro clinic** link. Use the role that matches each person's duties. A doctor can enter their specialization and professional registration number from their profile page (`/profile/update/`) or from the doctor profile edit page. The specialization is free text and appears on the doctor profile and printed prescriptions.

The installed app does not offer public staff registration. The clinic administrator is responsible for adding and disabling staff accounts; role labels are not a substitute for a reviewed authorization policy.

### Start and open OPDPro

Start the app from the repository root:

```bash
python manage.py runserver 127.0.0.1:8000
```

Open <http://127.0.0.1:8000/> in a browser on the same computer. Keep the terminal open while using the app. Stop the server with `Ctrl+C` before shutting down or backing up the computer.

For later sessions, open a terminal, change to the project root, activate `.venv`, and run the same `runserver` command. The first run after code updates should include `python manage.py migrate` before starting the server.

### Configure a clinic and staff

1. In Django admin (`/admin/`), create or update the single clinic settings record with the clinic's name, address, contact details, registration number, optional GSTIN, invoice prefix, and appropriate fee values.
2. Create individual staff accounts and assign their clinic role. The current roles include doctor, receptionist, nurse, pharmacist, lab technician, and admin.
3. Set a doctor's specialization in their profile. This is free text: examples include `General Medicine`, `Paediatrics`, or `Dentistry`. Dentists use the doctor role.
4. Review the fee catalogue, invoice footer, and clinic details before printing any documents.
5. Test the workflow with fictional data before entering actual patient details.

The app uses the `Asia/Kolkata` timezone and rupee-denominated amounts. Clinic information and financial settings must be confirmed by the clinic administrator; the sample defaults are not professional, tax, or billing advice.

## Data locations and backups

In source/developer mode the default local data locations are:

- Database: `<project-root>/db.sqlite3`
- Uploaded report files: `<project-root>/media/`

The application supports optional `OPD_DATABASE_PATH` and `OPD_MEDIA_ROOT` environment overrides. If you change either, record the resulting locations in the clinic's operations notes and include them in every backup.

The installed Windows desktop app stores its database, uploaded files, and generated secret key under `%LOCALAPPDATA%\OPDPro`. Keep that directory private and include it in backups. Use the launcher backup/restore controls rather than copying the live SQLite database.

At a minimum:

- Restrict OS access to the project, database, and uploaded files.
- Use an encrypted backup destination controlled by the clinic; never put unencrypted patient records in public/shared cloud folders or personal messaging/email.
- Stop the Django process before copying the SQLite database and media directory, so the database is not copied while being written.
- Keep multiple dated backups and periodically perform a restore test to a separate, non-production location.
- Define who may access, export, retain, and delete patient records under the clinic's applicable policies and legal/professional obligations.

The installed app stores its Django secret key in the separate per-user `%LOCALAPPDATA%\OPDPro` folder. Django hashes account passwords; it does not store them as readable text. Uploaded reports are served only to signed-in users. The local-only app uses HTTP on loopback, so Windows account protection and device disk encryption remain important. This app does not provide an automated backup, disaster-recovery, encryption-at-rest, retention, or audit-log service. OS-level safeguards and tested backup procedures remain the clinic's responsibility.

## India-focused and specialty scope

The app includes Indian clinic-oriented fields and options such as `Asia/Kolkata`, rupee amounts, UPI/cash/card/NEFT/cheque payment modes, optional GSTIN, and an included Indian medicine starter list. These are configurable operational features, not validation of a clinic's tax or prescribing requirements.

Doctors and dentists share the existing general OPD workflow: patient details, appointments, doctor notes, prescriptions, billing, and report handling. The current app does not include dental tooth charts/odontograms, procedure-specific dental plans, specialty-specific templates, ABHA/ABDM integration, or multi-clinic account isolation. Do not represent those capabilities as supported.

## Troubleshooting

| Problem | Check |
|---|---|
| Startup says `Set SECRET_KEY...` | Confirm `.env` is in the repository root, not in `.venv` or another folder, and that `SECRET_KEY` has a generated value. |
| `No module named ...` | Activate the project's `.venv` and run `python -m pip install -r requirements.txt`. |
| Login page or admin reports a missing database table | Stop the server and run `python manage.py migrate`. |
| Browser cannot connect | Confirm the server terminal has no error and use `http://127.0.0.1:8000/` on the same computer. |
| Uploaded reports are missing | Check `OPD_MEDIA_ROOT` if set; otherwise check the project `media/` directory and confirm the account can read/write it. |
| Static styles or icons are missing | Check the computer's internet connection; the web UI currently loads Bootstrap styles and icons from a public CDN. |

## Developer verification and upgrades

Before normal use or after updating application code:

```bash
python manage.py check
python manage.py migrate
python manage.py test
```

Most app test modules are placeholders; the current tests cover doctor profile fields only, not end-to-end or clinical workflows. A passing test command is therefore not evidence of clinical workflow coverage. Back up the database and media before applying updates or migrations, and test upgrades against a restored copy first.

## Moving beyond one local computer

Do not make the local server reachable from other devices by changing its bind address to `0.0.0.0`. A multi-user network or internet deployment needs a separate production design and review, including a supported production WSGI/ASGI server, HTTPS termination, production static/media delivery, a concurrency-appropriate database, access-control testing, monitoring, backups and restoration, and an India-specific privacy/security assessment. Do not put live patient records into a network deployment until those controls have been independently reviewed.
