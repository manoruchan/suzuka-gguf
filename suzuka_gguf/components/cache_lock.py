from __future__ import annotations

import fcntl
import hashlib
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def repository_lock(cache_dir: Path, repo: str) -> Iterator[None]:
    """Serialize suzuka-gguf operations that modify one repository."""
    lock_dir = cache_dir / ".suzuka-gguf-locks"
    lock_dir.mkdir(parents=True, exist_ok=True)

    lock_name = (
        hashlib.sha256(repo.encode("utf-8")).hexdigest() + ".lock"
    )
    lock_path = lock_dir / lock_name

    with lock_path.open("a", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
