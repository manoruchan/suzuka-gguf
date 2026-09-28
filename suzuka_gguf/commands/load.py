from __future__ import annotations

import argparse
import sys

from suzuka_gguf.components import runtime
from suzuka_gguf.components.cache import Cache
from suzuka_gguf.components.path_resolver import PathResolver


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "load",
        help="load a cached model",
    )
    parser.add_argument("file")
    parser.add_argument("--repo", help="<user>/<model>")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--threads", type=int)
    parser.add_argument("--reasoning")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    cache_dir = args.cache or PathResolver.DEFAULT_CACHE_PATH

    if args.repo is not None:
        model_path = Cache.cached_model_file(
            cache_dir,
            args.repo,
            args.file,
        )
    else:
        model_path = Cache.find_cached_file(
            cache_dir,
            args.file,
        )

    repo_path = PathResolver.repository_from_model_path(model_path)
    repo = PathResolver.repo_from_dir(repo_path)

    if repo is None:
        raise RuntimeError(
            f"cannot determine repository from model path: {model_path}"
        )

    target = f"{repo}/{model_path.name}"

    current = runtime.request("status")

    if current is not None:
        current_target = current["model_target"]

        if current_target == target:
            print(f"Already loaded: {target}")
            print(
                f"API: http://{current['host']}:{current['port']}"
            )
            return 0

        print(
            f"Another model is already loaded: {current_target}",
            file=sys.stderr,
        )
        print(
            "Run `suzuka-gguf unload` first.",
            file=sys.stderr,
        )
        return 1

    print(f"Loading: {target}")
    print(f"Model  : {model_path}")
    print(f"API    : http://{args.host}:{args.port}")

    runtime.request(
        "load",
        model_repo=repo,
        model_target=target,
        model_path=str(model_path),
        host=args.host,
        port=args.port,
        threads=args.threads,
        reasoning=args.reasoning,
        timeout=args.timeout,
    )

    print(f"Loaded: {target}")

    return 0
