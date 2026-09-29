from __future__ import annotations

import argparse
from pathlib import Path

from suzuka_gguf.components.cache import Cache
from suzuka_gguf.components.path_resolver import PathResolver


def model_files(cache_dir: Path) -> list[str]:
    files: set[str] = set()

    for _, repo_dir in Cache.get_cached_repositories(cache_dir):
        info = Cache.latest_snapshot(repo_dir)
        if not info:
            continue

        _, snapshot = info

        for file in Cache.snapshot_files(snapshot):
            if file.name.endswith(".gguf") and "mmproj" not in file.name:
                files.add(file.name)

    return sorted(files)


def repositories(cache_dir: Path) -> list[str]:
    return [
        repo
        for repo, _ in Cache.get_cached_repositories(cache_dir)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("models", "repos"))
    parser.add_argument("--cache")
    args = parser.parse_args()

    cache_dir = Path(
        args.cache
        if args.cache is not None
        else PathResolver.DEFAULT_CACHE_PATH
    )

    if args.kind == "models":
        values = model_files(cache_dir)
    else:
        values = repositories(cache_dir)

    for value in values:
        print(value)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

