from __future__ import annotations

import argparse
import json
import secrets
import signal
import socket

from suzuka_gguf.components.server import Server


def socket_name(token: str) -> str:
    return f"\0suzuka-gguf-{token}"


class ServerRuntime:
    def __init__(self, token: str):
        self.token = token
        self.server = Server(
            log_path=self._log_path(),
        )
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(socket_name(token))
        self.socket.listen(8)
        self.running = True

        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGHUP, self._handle_signal)


    def _log_path(self):
        from suzuka_gguf.components.path_resolver import PathResolver

        return PathResolver.DEFAULT_CACHE_PATH.parent / "log" / "server.log"

    def _handle_signal(self, signum, frame):
        self.running = False
        self.server.unload()

    def run(self) -> None:
        print(f"READY {self.token}", flush=True)

        try:
            while self.running:
                self.socket.settimeout(0.5)

                try:
                    connection, _ = self.socket.accept()
                except TimeoutError:
                    continue

                with connection:
                    self.handle(connection)
        finally:
            self.server.unload()
            self.socket.close()

    def handle(self, connection: socket.socket) -> None:
        data = b""

        while b"\n" not in data:
            chunk = connection.recv(4096)

            if not chunk:
                return

            data += chunk

        request = json.loads(data.decode("utf-8"))

        try:
            result = self.dispatch(request)
            response = {
                "ok": True,
                "result": result,
            }
        except Exception as exc:
            response = {
                "ok": False,
                "error": str(exc),
            }

        connection.sendall(
            (json.dumps(response) + "\n").encode("utf-8")
        )

    def dispatch(self, request: dict) -> dict | None:
        command = request["command"]

        if command == "load":
            self.server.load(
                model_repo=request["model_repo"],
                model_target=request["model_target"],
                model_path=request["model_path"],
                host=request["host"],
                port=request["port"],
                threads=request.get("threads"),
                reasoning=request.get("reasoning"),
                timeout=request.get("timeout", 60.0),
            )
            return self.server.status()

        if command == "unload":
            self.server.unload(
                timeout=request.get("timeout", 10.0),
            )
            return None

        if command == "status":
            return self.server.status()

        raise ValueError(f"unknown server command: {command}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("token")
    args = parser.parse_args()

    runtime = ServerRuntime(args.token)
    runtime.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
