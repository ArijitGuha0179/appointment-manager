from concurrent.futures import ThreadPoolExecutor
from datetime import date
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json

import app


class RequestSocket:
    def __init__(self, request):
        self.request = BytesIO(request)
        self.response = BytesIO()

    def makefile(self, *args):
        return self.request

    def sendall(self, data):
        self.response.write(data)


def call(path, method="GET", data=None):
    body = json.dumps(data).encode() if data is not None else b""
    headers = f"{method} {path} HTTP/1.0\r\nContent-Length: {len(body)}\r\n\r\n"
    sock = RequestSocket(headers.encode() + body)
    app.Handler(sock, ("127.0.0.1", 0), None)
    headers, result = sock.response.getvalue().split(b"\r\n\r\n", 1)
    code = int(headers.split()[1])
    return code, json.loads(result) if b"application/json" in headers else result


def run():
    with TemporaryDirectory() as directory:
        app.DB = Path(directory) / "test.db"
        app.initialize()
        path = "/api/appointments"
        assert b"Book a visit" in call("/")[1]
        assert call(path) == (200, [])
        _, options = call("/api/options")
        visit = dict(patient="Demo Patient", provider=options["providers"][0],
                     service=options["services"][0], day=date.today().isoformat(), slot="09:00")
        assert call(path, "POST", dict(visit, day="2000-01-01"))[0] == 400
        assert call(path, "POST", dict(visit, patient="  "))[0] == 400
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: call(path, "POST", visit), range(2)))
        assert sorted(code for code, _ in results) == [201, 409]
        booked = next(result["id"] for code, result in results if code == 201)
        item = f"{path}/{booked}"
        assert call(item, "PUT", dict(visit, slot="10:00"))[0] == 200
        assert call(path)[1][0]["slot"] == "10:00"
        assert call(item, "DELETE")[0] == 200
        assert call(path)[1][0]["status"] == "Cancelled"
        assert call(item, "PUT", visit)[0] == 404
        assert call(path, "POST", dict(visit, slot="10:00"))[0] == 201
        app.initialize()
        assert len(call(path)[1]) == 2
        assert call(path + "/999", "DELETE")[0] == 404
        print("Appointment request-handler checks passed.")


if __name__ == "__main__":
    run()
