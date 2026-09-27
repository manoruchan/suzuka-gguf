from __future__ import annotations

import argparse

from suzuka_gguf.components import runtime


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "unload",
        help="unload the current model",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    current = runtime.request("status")

    if current is None:
        print("No suzuka-gguf model is loaded.")
        return 0

    print(
        f"Stopping llama-server "
        f"(PID {current['pid']})..."
    )

    runtime.request(
        "unload",
        timeout=args.timeout,
    )

    print("Unloaded.")

    return 0
