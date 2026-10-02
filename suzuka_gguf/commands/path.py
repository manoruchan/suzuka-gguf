from __future__ import annotations

import argparse

from suzuka_gguf.components.cache import cached_model_file, find_cached_file
from suzuka_gguf.components.path_resolver import PathResolver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "path",
        help="resolve a cached model file path"
    )
    parser.add_argument("file")
    parser.add_argument("--repo", help="<user>/<model>")
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    cache_dir = args.cache or PathResolver.DEFAULT_CACHE_PATH

    if args.repo is not None:
        print(cached_model_file(cache_dir, args.repo, args.file))
    else:
        print(find_cached_file(cache_dir, args.file))
    return 0
