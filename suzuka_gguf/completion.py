from __future__ import annotations

import argparse
from pathlib import Path

from suzuka_gguf.components.cache import (
    get_cached_repositories,
    latest_snapshot,
    snapshot_files,
)
from suzuka_gguf.components.path_resolver import PathResolver
from suzuka_gguf.components.utils import cli_filename


def model_files(cache_dir: Path) -> list[str]:
    files: set[str] = set()

    for _, repo_dir in get_cached_repositories(cache_dir):
        info = latest_snapshot(repo_dir)
        if not info:
            continue

        _, snapshot = info

        for file in snapshot_files(snapshot):
            if file.name.endswith(".gguf") and "mmproj" not in file.name:
                files.add(cli_filename(file.name))

    return sorted(files)


def gguf_files(cache_dir: Path, repo: str | None = None) -> list[str]:
    files: set[str] = set()

    if repo is None:
        repo_dirs = [
            repo_dir
            for _, repo_dir in get_cached_repositories(cache_dir)
        ]
    else:
        repo_dir = PathResolver.repo_dir(repo, cache_dir)
        repo_dirs = [repo_dir] if repo_dir.is_dir() else []

    for repo_dir in repo_dirs:
        snapshots = repo_dir / "snapshots"

        if not snapshots.is_dir():
            continue

        for snapshot in snapshots.iterdir():
            if not snapshot.is_dir() or snapshot.is_symlink():
                continue

            for file in snapshot_files(snapshot):
                if file.name.endswith(".gguf"):
                    files.add(str(file.relative_to(snapshot)))

    return sorted(files)


def repositories(cache_dir: Path) -> list[str]:
    return [
        repo
        for repo, _ in get_cached_repositories(cache_dir)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("models", "repos", "gguf-files"))
    parser.add_argument("--cache")
    parser.add_argument("--repo")
    args = parser.parse_args()

    cache_dir = Path(
        args.cache
        if args.cache is not None
        else PathResolver.DEFAULT_CACHE_PATH
    )

    if args.kind == "models":
        values = model_files(cache_dir)
    elif args.kind == "repos":
        values = repositories(cache_dir)
    else:
        values = gguf_files(cache_dir, args.repo)

    for value in values:
        print(value)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
