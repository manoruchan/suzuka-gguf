from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from suzuka_gguf.components.cache import (
    remove_cached_gguf,
    validate_gguf_filename,
)
from suzuka_gguf.components.cache_lock import repository_lock
from suzuka_gguf.components.path_resolver import PathResolver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "remove",
        help="remove a cached repository or GGUF file",
    )
    parser.add_argument("repo")
    parser.add_argument(
        "--file",
        metavar="FILE",
        help="remove one cached GGUF file instead of the whole repository",
    )
    parser.add_argument("-y", "--yes", action="store_true")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    cache_dir = (
        Path(args.cache)
        if args.cache
        else PathResolver.DEFAULT_CACHE_PATH
    )
    repo_dir = PathResolver.repo_dir(args.repo, cache_dir)

    if args.file is not None:
        validate_gguf_filename(args.file)

    if not repo_dir.is_dir():
        print(f"Not cached: {args.repo}", file=sys.stderr)
        return 1

    target = f"{args.repo}/{args.file}" if args.file else args.repo

    if not args.yes:
        if args.file:
            prompt = f"Remove cached GGUF {target}? [y/N] "
        else:
            prompt = f"Remove cached repository {args.repo}? [y/N] "

        answer = input(prompt).strip().lower()
        if answer not in {"y", "yes"}:
            print("Cancelled.")
            return 0

    with repository_lock(cache_dir, args.repo):
        if not repo_dir.is_dir():
            print(f"Not cached: {args.repo}", file=sys.stderr)
            return 1

        if args.file:
            if not remove_cached_gguf(repo_dir, args.file):
                print(f"Not cached: {target}", file=sys.stderr)
                return 1
            print(f"Removed: {target}")
        else:
            shutil.rmtree(repo_dir)
            print(f"Removed: {args.repo}")

    return 0
