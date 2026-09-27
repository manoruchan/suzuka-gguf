from __future__ import annotations

import argparse

from suzuka_gguf.components.cache import Cache
from suzuka_gguf.components.path_resolver import PathResolver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "list",
        help="list cached repositories"
    )
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    cache_dir = args.cache or PathResolver.DEFAULT_CACHE_PATH

    print(f"Cache: {cache_dir}")

    repos = Cache.get_cached_repositories(cache_dir)

    if not repos:
        print("No cached repositories.")
        return 0

    for repo, _ in repos:
        print(repo)

    return 0
