# OPDPro

OPDPro is a local outpatient-practice management app for a **single clinic on one Windows computer**. The Windows desktop app displays the clinic and its setup, backup, and restore controls together in one native application window. It runs a local-only clinic server and stores the clinic database and uploaded reports in the signed-in user's local application data folder. It includes patient records, appointments, doctor/staff profiles, prescriptions, invoice and payment tracking, and lab-report upload/review.

The project is India-oriented: it uses the `Asia/Kolkata` timezone, Indian rupee amounts, Indian payment modes, optional GSTIN and registration details, and an Indian medicine catalogue. Doctors and dentists can use the general OPD workflow and enter a specialization (for example, `Dentistry`) in their profile.

## Important scope and safety notice

- This is a single-clinic application, not a hosted multi-clinic service. Do not use one installation to store records for unrelated clinics.
- The clinical workflow is specialty-neutral. It does **not** currently provide a dental odontogram/tooth chart, dental treatment plans, or specialty-specific clinical forms.
- OPDPro handles sensitive personal and health information. Staff registration is controlled by the clinic administrator; the first-run desktop setup creates the initial administrator. The app has limited role-based access controls and is intended for one trusted local computer.
- This repository has not established legal/regulatory compliance or completed an independent security assessment. Review privacy, access, backup, clinical, and operational requirements before using real patient records.

## Start here

For clinic staff, use the Windows release: double-click `OPDPro-Setup.exe` and follow the installer when available; the ZIP also includes a script-based installer. Open OPDPro from its shortcut. Create the clinic administrator on first run, then sign in within the same application window. See [Local deployment and clinic setup](docs/LOCAL-DEPLOYMENT.md) for staff sign-in, secure backups and restore, data locations, uninstalling without deleting records, manual developer setup, and troubleshooting.

## Main areas

| Area | Included workflow |
|---|---|
| Staff | Doctor, receptionist, nurse, pharmacist, lab technician, and admin roles |
| Patients | Patient registration, profile, medical history, allergies, and visit history |
| Appointments | Booking, status tracking, doctor notes, and visit history |
| Prescriptions | Drug catalogue, dosage instructions, printable prescription, and dispense status |
| Billing | Invoices, configurable fees, partial payments, and payment modes |
| Reports | Upload and doctor review of lab and imaging reports |
| Clinic configuration | Clinic details, fees, invoice prefix, and footer |

This feature list describes the current code, not a clinical or regulatory certification. Review [the local deployment guide](docs/LOCAL-DEPLOYMENT.md) before entering real data.

## Repository map

- `opdmanagement/` — Django project configuration and root routes
- `usermanagement/`, `doctors/`, `patients/`, `appointment/` — staff, patient, and appointment workflows
- `prescriptions/`, `billing/`, `reports/`, `settings/` — prescription, finance, report, and clinic configuration workflows
- `local_data.py`, `desktop_launcher.py` — local Windows startup and clinic backup/restore
- `templates/`, `static/` — web interface assets
- `android/` — Android WebView wrapper project
- `windows/` — Windows release build and installation scripts

## Mobile and desktop wrappers

The Android project is an optional WebView client and requires a separately deployed HTTPS backend; it is not part of the one-computer Windows install. Developers build Windows releases on Windows with `windows/build_windows.ps1`. End users do not need Python or developer tools.
