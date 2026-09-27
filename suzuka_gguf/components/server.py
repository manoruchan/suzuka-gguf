from __future__ import annotations

import subprocess
import time
from pathlib import Path


class Server:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.process: subprocess.Popen | None = None
        self.model_repo: str | None = None
        self.model_target: str | None = None
        self.model_path: Path | None = None
        self.host: str | None = None
        self.port: int | None = None
        self.command: list[str] | None = None
        self.log = None

    @property
    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def load(
        self,
        *,
        model_repo: str,
        model_target: str,
        model_path: Path,
        host: str,
        port: int,
        threads: int | None = None,
        reasoning: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        if self.is_running:
            raise RuntimeError(
                f"another model is already loaded: {self.model_target}"
            )

        command = [
            "llama-server",
            "--model",
            str(model_path),
            "--host",
            host,
            "--port",
            str(port),
        ]

        if threads is not None:
            command += ["--threads", str(threads)]

        if reasoning is not None:
            command += ["--reasoning", reasoning]

        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        log = self.log_path.open("w", encoding="utf-8")

        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
        )

        self.process = process
        self.model_repo = model_repo
        self.model_target = model_target
        self.model_path = model_path
        self.host = host
        self.port = port
        self.command = command
        self.log = log

        try:
            self._wait_for_server(host, port, process, timeout)
        except Exception:
            self.unload()
            raise

    def unload(self, timeout: float = 10.0) -> None:
        process = self.process

        if process is None:
            return

        if process.poll() is None:
            process.terminate()

            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        if self.log is not None:
            self.log.close()

        self.process = None
        self.model_repo = None
        self.model_target = None
        self.model_path = None
        self.host = None
        self.port = None
        self.command = None
        self.log = None

    def status(self) -> dict | None:
        if not self.is_running:
            return None

        return {
            "model_repo": self.model_repo,
            "model_target": self.model_target,
            "model_path": str(self.model_path) if self.model_path else None,
            "host": self.host,
            "port": self.port,
            "pid": self.process.pid if self.process else None,
        }

    def _wait_for_server(
        self,
        host: str,
        port: int,
        process: subprocess.Popen,
        timeout: float,
    ) -> None:
        import urllib.error
        import urllib.request

        deadline = time.monotonic() + timeout
        url = f"http://{host}:{port}/health"

        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(
                    "llama-server exited before becoming ready "
                    f"(code {process.returncode})"
                )

            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    if response.status == 200:
                        return
            except (urllib.error.URLError, TimeoutError, OSError):
                pass

            time.sleep(0.25)

        raise TimeoutError(
            f"llama-server did not become ready within {timeout:.0f}s"
        )
