from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

from suzuka_gguf.components import runtime


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "call",
        help="call the currently loaded model",
    )
    parser.add_argument("prompt")
    parser.add_argument("--reasoning-effort")
    parser.add_argument("--timeout", type=float, default=300)
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    state = runtime.request("status")

    if state is None:
        print(
            "llama-server is not running. "
            "Run `suzuka-gguf load <file>` first.",
            file=sys.stderr,
        )
        return 1

    url = (
        f"http://{state['host']}:{state['port']}"
        "/v1/chat/completions"
    )

    body = {
        "model": state["model_repo"],
        "messages": [
            {
                "role": "user",
                "content": args.prompt,
            }
        ],
        "stream": True,
        "stream_options": {
            "include_usage": True,
        },
    }

    if args.reasoning_effort is not None:
        body["reasoning_effort"] = args.reasoning_effort

    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    usage = {}
    timings = {}
    start_time = time.monotonic()

    try:
        with urllib.request.urlopen(
            request,
            timeout=args.timeout,
        ) as response:
            for line in response:
                line = line.decode("utf-8").strip()

                if not line.startswith("data: "):
                    continue

                data = line[6:]

                if data == "[DONE]":
                    break

                chunk = json.loads(data)

                if chunk.get("usage"):
                    usage = chunk["usage"]

                if chunk.get("timings"):
                    timings = chunk["timings"]

                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                content = delta.get("content", "")

                if content:
                    print(content, end="", flush=True)

    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(
            f"API error ({exc.code}): {detail}",
            file=sys.stderr,
        )
        return 1

    except urllib.error.URLError as exc:
        print(
            f"API connection error: {exc}",
            file=sys.stderr,
        )
        return 1

    elapsed = time.monotonic() - start_time

    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    predicted_per_second = timings.get("predicted_per_second")

    print()

    metrics = []

    if prompt_tokens is not None:
        metrics.append(f"prompt={prompt_tokens} tokens")

    if completion_tokens is not None:
        metrics.append(f"completion={completion_tokens} tokens")

    metrics.append(f"total={elapsed:.2f} s")

    if predicted_per_second is not None:
        metrics.append(
            f"{predicted_per_second:.2f} tok/s"
        )

    print(
        f"\n[{', '.join(metrics)}]",
        file=sys.stderr,
    )

    return 0
