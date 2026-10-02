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
