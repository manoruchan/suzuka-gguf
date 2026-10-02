from __future__ import annotations

import argparse
import os
import subprocess

from suzuka_gguf.components.path_resolver import PathResolver


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
        help="explicit Hugging Face model file",
    )
    parser.add_argument(
        "--no-mmproj",
        action="store_true",
        help="do not download mmproj automatically",
    )
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    command = ["llama-cli"]

    if ":" in args.target and args.file:
        raise SystemExit(
            "error: --file cannot be used with a quantization target "
            "(<user>/<model>:<quantize>)"
        )

    if args.file:
        command += [
            "--hf-repo",
            args.target,
            "--hf-file",
            args.file,
        ]
    elif ":" in args.target:
        command += ["-hf", args.target]
    else:
        command += ["--hf-repo", args.target]

    if args.no_mmproj:
        command.append("--no-mmproj")

    print("+", " ".join(command))
    print("Note: llama-cli downloads and then exits.")

    env = os.environ.copy()
    env["LLAMA_CACHE"] = str(
        args.cache or PathResolver.DEFAULT_CACHE_PATH
    )

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        env=env,
    )

    process.communicate(b"/exit\n")

    return process.returncode
