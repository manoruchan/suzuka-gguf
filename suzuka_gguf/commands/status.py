from __future__ import annotations

import argparse

from suzuka_gguf.components import runtime


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "status",
        help="show server status",
    )
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    current = runtime.request("status")

    if current is None:
        print("No suzuka-gguf model is loaded.")
        return 0

    print(f"Model  : {current['model_target']}")
    print(f"Path   : {current['model_path']}")
    print(
        f"API    : http://{current['host']}:{current['port']}"
    )
    print(f"PID    : {current['pid']}")

    return 0
