from __future__ import annotations

import argparse
import sys

from suzuka_gguf.components.cache import Cache
from suzuka_gguf.components.path_resolver import PathResolver
from suzuka_gguf.components.utils import human_size, directory_size


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "info",
        help="show repository information",
    )
    parser.add_argument("repo", help="<user>/<model>")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    cache_dir = args.cache or PathResolver.DEFAULT_CACHE_PATH
    repo_dir = PathResolver.repo_dir(args.repo, cache_dir)

    if not repo_dir.exists():
        print(f"Not cached: {args.repo}", file=sys.stderr)
        return 1

    info = Cache.latest_snapshot(repo_dir)

    print(f"Repository : {args.repo}")
    print(f"Cache path : {repo_dir}")
    print(f"Size       : {human_size(directory_size(repo_dir))}")

    if not info:
        print("Revision   : -")
        return 0

    revision, snapshot = info
    print(f"Revision   : {revision}")
    print(f"Snapshot   : {snapshot}")

    return 0
