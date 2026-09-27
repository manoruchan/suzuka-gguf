from __future__ import annotations

import json
import os
import socket


def _socket_name() -> str:
    token = os.environ.get("SUZUKA_GGUF_RUNTIME")

    if not token:
        raise RuntimeError(
            "suzuka-gguf runtime is not running; "
            "source path_setup.sh first"
        )

    return f"\0suzuka-gguf-{token}"


def request(command: str, **kwargs) -> dict | None:
    payload = {
        "command": command,
        **kwargs,
    }

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(_socket_name())

        sock.sendall(
            (json.dumps(payload) + "\n").encode("utf-8")
        )

        data = b""

        while b"\n" not in data:
            chunk = sock.recv(4096)

            if not chunk:
                raise RuntimeError("suzuka-gguf runtime disconnected")

            data += chunk

    response = json.loads(data.decode("utf-8"))

    if not response["ok"]:
        raise RuntimeError(response["error"])

    return response["result"]
