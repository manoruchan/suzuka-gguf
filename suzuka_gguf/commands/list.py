from __future__ import annotations

import argparse
from pathlib import Path

from suzuka_gguf.components.cache import Cache
from suzuka_gguf.components.path_resolver import PathResolver
from suzuka_gguf.components.utils import human_size


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "list",
        help="list cached GGUF files",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        help="<user>/<model>",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="list repository names only",
    )
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    cache_dir = args.cache or PathResolver.DEFAULT_CACHE_PATH

    if args.minimal:
        return show_repositories(cache_dir)

    if args.repo is not None:
        return show_repository(cache_dir, args.repo)

    return show_cached_files(cache_dir)


def show_repository(cache_dir: Path, repo: str) -> int:
    repo_dir = PathResolver.repo_dir(repo, cache_dir)

    if not repo_dir.is_dir():
        print(f"Not cached: {repo}")
        return 1

    info = Cache.latest_snapshot(repo_dir)

    if not info:
        print("No snapshot found.")
        return 1

    _, snapshot = info
    files = Cache.snapshot_files(snapshot)

    if not files:
        print("No files found.")
        return 0

    for file in files:
        try:
            size = human_size(file.stat().st_size)
        except OSError:
            size = "-"

        print(f"{size:>10}  {file.relative_to(snapshot)}")

    return 0


def show_cached_files(cache_dir: Path) -> int:
    print(f"Cache: {cache_dir}")
    print()

    repos = Cache.get_cached_repositories(cache_dir)

    if not repos:
        print("No cached repositories.")
        return 0

    for repo, repo_dir in repos:
        info = Cache.latest_snapshot(repo_dir)

        if not info:
            print(repo)
            print("  No snapshot found.")
            print()
            continue

        revision, snapshot = info
        print(f"{repo}  ({revision[:12]})")

        model_files = [
            file
            for file in Cache.snapshot_files(snapshot)
            if file.name.endswith(".gguf") and "mmproj" not in file.name
        ]

        if not model_files:
            print("  No GGUF model files found.")
            print()
            continue

        for file in model_files:
            print(
                f"  {human_size(file.stat().st_size):>10}"
                f"  {file.relative_to(snapshot)}"
            )

        print()

    return 0


def show_repositories(cache_dir: Path) -> int:
    print(f"Cache: {cache_dir}")

    repos = Cache.get_cached_repositories(cache_dir)

    if not repos:
        print("No cached repositories.")
        return 0

    for repo, _ in repos:
        print(repo)

    return 0
