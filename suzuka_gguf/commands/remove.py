from __future__ import annotations

import argparse
import shutil
import sys

from suzuka_gguf.components.path_resolver import PathResolver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "remove",
        help="remove a cached repository"
    )
    parser.add_argument("repo")
    parser.add_argument("-y", "--yes", action="store_true")
    parser.set_defaults(func=execute)

def execute(args: argparse.Namespace) -> int:
    cache_dir = args.cache or PathResolver.DEFAULT_CACHE_PATH
    repo_dir = PathResolver.repo_dir(args.repo, cache_dir)

    if not repo_dir.is_dir():
        print(f"Not cached: {args.repo}", file=sys.stderr)
        return 1

    if not args.yes:
        answer = input(f"Remove cached repository {args.repo}? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Cancelled.")
            return 0

    shutil.rmtree(repo_dir)
    print(f"Removed: {args.repo}")

    return 0
