from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "call",
        help="call a running llama-server",
    )
    parser.add_argument("prompt")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="llama-server host",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="llama-server port",
    )
    parser.set_defaults(func=execute)


def execute(args: argparse.Namespace) -> int:
    url = (
        f"http://{args.host}:{args.port}"
        "/v1/chat/completions"
    )

    body = {
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
            timeout=300,
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
        )
        return 1

    except urllib.error.URLError as exc:
        print(
            f"API connection error: {exc}",
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

    print(f"\n[{', '.join(metrics)}]")

    return 0
