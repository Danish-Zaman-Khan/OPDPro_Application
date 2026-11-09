# Runtime Validation Report

**Generated:** 2026-11-05 14:40 IST (retest)  
**Target:** OPDPro local Django application  
**Test data:** Disposable SQLite database and media directory under `/tmp`; the clinic database and records were not used.

## Summary

| Step | Status | Exit Code | Details |
|---|---|---:|---|
| Startup | PASS | 0 | `manage.py runserver 127.0.0.1:8765 --noreload`; login page returned HTTP 200 |
| Django tests | PASS | 0 | 7 tests passed, including CSS placement and authentication redirect regression checks |
| Backup/restore tests | PASS | 0 | 2 tests passed |
| Django checks | PASS | 0 | Standard and local-desktop configurations passed; no pending migrations |
| Browser smoke | PASS | 0 | Login, protected-route redirect, dashboard styling, clinic page navigation, and patient create/read-back verified |

**Overall: PASS for local application runtime validation.** Windows packaging and installer behavior are outside this macOS runtime check.

## Environment

- OS: macOS
- Python: 3.13.8
- Docker: unavailable; application uses SQLite, so Docker was not required
- Node.js: 22.17.1
- Playwright: 1.64.1; Chromium installed and browser session used

## Browser checks

- Signed in through the browser with a disposable administrator account.
- Registered fictional patients, confirmed success notices and patient list entries after reload, then opened the patient detail page.
- Confirmed the latest record persisted in the isolated SQLite database: `Retest Patient`, phone `9988776655`, date of birth `1988-08-08`.
- After signing out, a protected dashboard request redirected to the app login page at `/?next=/dashboard/` (HTTP 200); signing back in returned to the dashboard.
- Authenticated requests to dashboard, patients, appointments, today's queue, prescriptions, reports, billing, doctors/staff, and admin returned HTTP 200.
- Login page and shared clinic CSS returned HTTP 200.
- Dashboard-specific CSS was present in the document stylesheet, applied to the dashboard heading, and absent from visible page text.
- Prescription creation and invoice creation returned HTTP 200; their page-specific CSS rules loaded without exposing stylesheet text in the page body.

## Fixes applied

1. Wrapped the shared `extra_styles` block in a `<style>` element so dashboard, prescription, and invoice page styles render correctly.
2. Set Django's `LOGIN_URL` to the named OPDPro login route and added regression tests for the login redirect and dashboard CSS placement.

The Windows executable and installer have not been built or tested on this macOS host.
