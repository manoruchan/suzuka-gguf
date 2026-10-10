from pathlib import Path

from suzuka_gguf.components.path_resolver import PathResolver
from suzuka_gguf.components.utils import normalize_model_filename


def get_cached_repositories(cache_dir: Path) -> list[tuple[str, Path]]:
    if not cache_dir.is_dir():
        return []

    repos = []

    for path in cache_dir.iterdir():
        if path.is_dir():
            repo = PathResolver.repo_from_dir(path)

            if repo:
                repos.append((repo, path))

    return sorted(repos)


def find_cached_file(cache_dir: Path, filename: str) -> Path:
    filename = normalize_model_filename(filename)

    matches = []

    for _, repo_dir in get_cached_repositories(cache_dir):
        info = latest_snapshot(repo_dir)

        if not info:
            continue

        _, snapshot = info

        for file in snapshot_files(snapshot):
            if file.name == filename:
                matches.append(file)

    if not matches:
        raise FileNotFoundError(f"file is not cached: {filename}")

    if len(matches) > 1:
        raise RuntimeError(
            f"multiple cached files found for {filename}; "
            "use --repo <user>/<model>"
        )

    return matches[0]


def latest_snapshot(repo_dir: Path) -> tuple[str, Path] | None:
    refs = repo_dir / "refs"
    main = refs / "main"

    if main.is_file():
        commit = main.read_text(encoding="utf-8").strip()
        snapshot = repo_dir / "snapshots" / commit

        if snapshot.is_dir():
            return commit, snapshot

    snapshots = repo_dir / "snapshots"

    if not snapshots.is_dir():
        return None

    dirs = [p for p in snapshots.iterdir() if p.is_dir()]

    if not dirs:
        return None

    snapshot = max(dirs, key=lambda p: p.stat().st_mtime)
    return snapshot.name, snapshot


def snapshot_files(snapshot: Path) -> list[Path]:
    return sorted(
        (p for p in snapshot.rglob("*") if p.is_file()),
        key=lambda p: str(p.relative_to(snapshot)),
    )


def validate_gguf_filename(filename: str) -> Path:
    path = Path(filename)

    if (
        not filename
        or "\x00" in filename
        or path.is_absolute()
        or ".." in path.parts
        or not path.name.endswith(".gguf")
    ):
        raise ValueError(f"invalid GGUF file path: {filename!r}")

    return path


def remove_cached_gguf(repo_dir: Path, filename: str) -> bool:
    """Remove a GGUF file from every snapshot and collect unused blobs."""
    relative_path = validate_gguf_filename(filename)
    snapshots_dir = repo_dir / "snapshots"

    if repo_dir.is_symlink() or snapshots_dir.is_symlink():
        raise ValueError(
            f"refusing to remove a GGUF through a symbolic-link directory: {repo_dir}"
        )

    if not snapshots_dir.is_dir():
        return False

    snapshots = [
        path
        for path in snapshots_dir.iterdir()
        if path.is_dir() and not path.is_symlink()
    ]
    matches = []

    for snapshot in snapshots:
        parent = snapshot

        for part in relative_path.parts[:-1]:
            parent = parent / part
            if parent.is_symlink():
                raise ValueError(
                    "GGUF path cannot traverse a symbolic-link directory: "
                    f"{filename!r}"
                )

        candidate = snapshot / relative_path
        if candidate.is_symlink() or candidate.is_file():
            matches.append(candidate)

    if not matches:
        return False

    blobs_dir = repo_dir / "blobs"
    blob_targets = set()

    if not blobs_dir.is_symlink():
        blobs_root = blobs_dir.resolve(strict=False)

        for path in matches:
            if not path.is_symlink():
                continue

            try:
                target = path.resolve(strict=False)
            except (OSError, RuntimeError):
                continue

            if target.is_relative_to(blobs_root):
                blob_targets.add(target)

    for path in matches:
        path.unlink()

    for blob in blob_targets:
        if blob.is_file() and not _snapshot_references_blob(snapshots, blob):
            blob.unlink()

    return True


def _snapshot_references_blob(snapshots: list[Path], blob: Path) -> bool:
    for snapshot in snapshots:
        for path in snapshot.rglob("*"):
            if not path.is_symlink():
                continue

            try:
                if path.resolve(strict=False) == blob:
                    return True
            except (OSError, RuntimeError):
                continue

    return False


def cached_model_file(
    cache_dir: Path,
    repo: str,
    filename: str | None,
) -> Path:
    path = PathResolver.repo_dir(repo, cache_dir)

    if not path.is_dir():
        raise FileNotFoundError(f"model is not cached: {repo}")

    info = latest_snapshot(path)

    if not info:
        raise FileNotFoundError(f"no snapshot found for: {repo}")

    _, snapshot = info

    if filename:
        candidate = snapshot / filename

        if candidate.is_file():
            return candidate

        raise FileNotFoundError(f"file is not cached: {repo}/{filename}")

    files = snapshot_files(snapshot)

    ggufs = [
        p
        for p in files
        if p.name.endswith(".gguf") and "mmproj" not in p.name
    ]

    if len(ggufs) == 1:
        return ggufs[0]

    if not ggufs:
        raise FileNotFoundError(f"no GGUF model file found in: {repo}")

    raise RuntimeError(
        f"multiple GGUF files found in {repo}; "
        "specify the file explicitly"
    )
