from __future__ import annotations

import sys
import argparse

from suzuka_gguf import commands


COMMAND_MODULES = [
    commands.list,
    commands.info,
    commands.path,
    commands.pull,
    commands.remove,
    commands.call
]

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="suzuka-gguf",
        description="A simple GGUF manager for llama.cpp.",
    )

    parser.add_argument("--cache", help="cache dir")

    subparsers = parser.add_subparsers(dest="command", required=True)

    for module in COMMAND_MODULES:
        module.register_parser(subparsers)

    args = parser.parse_args()

    try:
        return args.func(args)
    except (ValueError, FileNotFoundError, RuntimeError, TimeoutError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130
