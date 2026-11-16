from contextlib import contextmanager
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import sqlite3
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DB = ROOT / "appointments.db"
PROVIDERS = ("Dr. Morgan", "Dr. Patel", "Dr. Lee")
SERVICES = ("Consultation", "Follow-up", "Health check")
SLOTS = tuple(f"{hour:02d}:{minute:02d}" for hour in range(9, 17) for minute in (0, 30))


@contextmanager
def database():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize():
    with database() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY, patient TEXT NOT NULL,
                provider TEXT NOT NULL, service TEXT NOT NULL,
                day TEXT NOT NULL, slot TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Scheduled'
                    CHECK(status IN ('Scheduled', 'Cancelled'))
            );
            CREATE UNIQUE INDEX IF NOT EXISTS active_slot
            ON appointments(provider, day, slot) WHERE status = 'Scheduled';
        """)


def fields(data):
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object.")
    patient, provider, service, day, slot = (
        data.get(key) for key in ("patient", "provider", "service", "day", "slot")
    )
    if not isinstance(patient, str) or not 1 <= len(patient.strip()) <= 100:
        raise ValueError("Enter a patient name of 1 to 100 characters.")
    if provider not in PROVIDERS or service not in SERVICES or slot not in SLOTS:
        raise ValueError("Select a valid provider, visit type and time.")
    if not isinstance(day, str):
        raise ValueError("Select a valid date.")
    try:
        parsed = date.fromisoformat(day)
    except ValueError:
        raise ValueError("Select a valid date.") from None
    if parsed.isoformat() != day or parsed < date.today():
        raise ValueError("Choose today or a future date.")
    return patient.strip(), provider, service, day, slot


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload, mime="application/json"):
        body = json.dumps(payload).encode() if mime == "application/json" else payload
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            self.reply(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif path == "/api/appointments":
            with database() as db:
                rows = db.execute("SELECT * FROM appointments ORDER BY day, slot, id")
                self.reply(200, [dict(row) for row in rows])
        elif path == "/api/options":
            self.reply(200, dict(providers=PROVIDERS, services=SERVICES,
                                 slots=SLOTS, today=date.today().isoformat()))
        else:
            self.reply(404, {"error": "Page not found."})

    def do_POST(self):
        self.change("create")

    def do_PUT(self):
        self.change("edit")

    def do_DELETE(self):
        self.change("cancel")

    def change(self, operation):
        path = urlsplit(self.path).path.split("/")
        if path[:3] != ["", "api", "appointments"]:
            return self.reply(404, {"error": "Page not found."})
        try:
            if operation == "create":
                if len(path) != 3:
                    raise ValueError("Invalid appointment URL.")
            else:
                if len(path) != 4 or not path[3].isascii() or not path[3].isdigit():
                    raise ValueError("Invalid appointment ID.")
                appointment_id = int(path[3])
                if not 0 < appointment_id < 2**63:
                    raise ValueError("Invalid appointment ID.")
            if operation != "cancel":
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 8192:
                    raise ValueError("Invalid request size.")
                try:
                    values = fields(json.loads(self.rfile.read(length)))
                except (UnicodeError, json.JSONDecodeError):
                    raise ValueError("Invalid JSON.") from None
            with database() as db:
                if operation == "create":
                    result = db.execute(
                        "INSERT INTO appointments(patient,provider,service,day,slot) VALUES (?,?,?,?,?)",
                        values,
                    )
                    appointment_id = result.lastrowid
                elif operation == "edit":
                    result = db.execute(
                        "UPDATE appointments SET patient=?,provider=?,service=?,day=?,slot=? "
                        "WHERE id=? AND status='Scheduled'", (*values, appointment_id),
                    )
                else:
                    result = db.execute(
                        "UPDATE appointments SET status='Cancelled' WHERE id=? AND status='Scheduled'",
                        (appointment_id,),
                    )
                if not result.rowcount:
                    return self.reply(404, {"error": "Scheduled appointment not found."})
            self.reply(201 if operation == "create" else 200, {"id": appointment_id})
        except ValueError as error:
            self.reply(400, {"error": str(error)})
        except sqlite3.IntegrityError:
            self.reply(409, {"error": "That provider already has an appointment at this time."})


if __name__ == "__main__":
    initialize()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Appointment Manager: http://127.0.0.1:8000", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

