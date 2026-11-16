# Clinic Desk

Clinic Desk is a local appointment manager for a fictional clinic. Staff can book, edit, reschedule and cancel visits, and filter the schedule by status. SQLite preserves records across restarts. An active provider can have only one appointment per slot. Cancellation keeps the record and frees the slot.

## Run locally

Install Python 3.10 or later. No third-party packages are required. Open a terminal in this directory and run:

    python app.py

On Windows, use `py app.py` if `python` is unavailable. Open http://127.0.0.1:8000 in your browser. The database is created automatically beside app.py. Press Ctrl+C to stop the server.

## Verify

Run `python smoke_test.py` (or `py smoke_test.py` on Windows). It uses a temporary SQLite database and exercises the request handlers without opening a network connection.

For a browser walkthrough, book a fictional patient at 09:00 today. Try booking a second patient with the same provider and slot and check that the app reports a conflict. Edit the first visit to 10:00 and refresh the page to verify it persists. Cancel it, select the Cancelled filter and confirm the record remains visible. Switch back to All appointments and book the freed 10:00 slot.

## Scope

This is a single-clinic, local assessment prototype. It uses three fixed fictional providers and fixed 30-minute slots, with date validation based on the host clock. There are no accounts, reminders, audit history, timezone conversion, or provider availability rules. Use fictional names only. The server is bound to localhost and is intended for a local demonstration.

See ASSESSMENT.md for testing details, AI disclosure, and the proposed next improvement.
