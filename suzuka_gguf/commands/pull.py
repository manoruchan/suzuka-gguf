from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from suzuka_gguf.components.cache_lock import repository_lock
from suzuka_gguf.components.hf import (
    match_repository_file,
    repository_files,
)
from suzuka_gguf.components.path_resolver import PathResolver
from suzuka_gguf.components.utils import normalize_model_filename


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "pull",
        help="download a model from Hugging Face",
    )
    parser.add_argument(
        "target",
        help="<user>/<model> or <user>/<model>:<quantize>",
    )
    parser.add_argument(
        "--file",
        metavar="FILE",
        help=(
            "file in the repository; used as given, "
            "extension completed when it matches no file"
        ),
    )
    parser.add_argument(
        "--no-mmproj",
        action="store_true",
        help="do not download mmproj automatically",
    )
    parser.set_defaults(func=execute)


def resolve_file(repo: str, filename: str) -> str:
    try:
        files = repository_files(repo)
    except RuntimeError as exc:
        print(
            f"Note: {exc}; using {filename!r} as given.",
            file=sys.stderr,
        )
        return normalize_model_filename(filename)

    return match_repository_file(files, filename)


def execute(args: argparse.Namespace) -> int:
    command = ["llama-cli"]

    if ":" in args.target and args.file:
        raise SystemExit(
            "error: --file cannot be used with a quantization target "
            "(<user>/<model>:<quantize>)"
        )

    repo = args.target.split(":", 1)[0]

    if args.file:
        args.file = resolve_file(repo, args.file)
        command += [
            "--hf-repo",
            repo,
            "--hf-file",
            args.file,
        ]
    elif ":" in args.target:
        command += ["-hf", args.target]
    else:
        command += ["--hf-repo", args.target]

    if args.no_mmproj:
        command.append("--no-mmproj")

    cache_dir = (
        Path(args.cache)
        if args.cache
        else PathResolver.DEFAULT_CACHE_PATH
    )
    PathResolver.repo_dir(repo, cache_dir)

    print("+", " ".join(command))
    print("Note: llama-cli downloads and then exits.")

    env = os.environ.copy()
    env["LLAMA_CACHE"] = str(cache_dir)

    with repository_lock(cache_dir, repo):
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            env=env,
        )

        process.communicate(b"/exit\n")

    return process.returncode
