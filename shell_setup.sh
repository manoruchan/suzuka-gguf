#!/usr/bin/env bash

# usage: source ./shell_setup.sh

SUZUKA_GGUF_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SUZUKA_GGUF_COMMAND_DIR="$SUZUKA_GGUF_DIR/bin"
SUZUKA_GGUF_CACHE="$SUZUKA_GGUF_DIR/models"

mkdir -p "$SUZUKA_GGUF_CACHE"
mkdir -p "$SUZUKA_GGUF_DIR/log"

case ":$PATH:" in
    *":$SUZUKA_GGUF_COMMAND_DIR:"*)
        ;;
    *)
        export PATH="$SUZUKA_GGUF_COMMAND_DIR:$PATH"
        ;;
esac


# Start one runtime for this shell.
if [[ -z "${SUZUKA_GGUF_RUNTIME:-}" ]]; then
    SUZUKA_GGUF_RUNTIME="$(python3 -c 'import secrets; print(secrets.token_hex(16))')"

    coproc SUZUKA_GGUF_RUNTIME_PROCESS {
        PYTHONPATH="$SUZUKA_GGUF_DIR" \
            python3 -m suzuka_gguf.components.server_runtime \
            "$SUZUKA_GGUF_RUNTIME"
    }

    IFS= read -r runtime_ready <&"${SUZUKA_GGUF_RUNTIME_PROCESS[0]}"

    if [[ "$runtime_ready" != "READY $SUZUKA_GGUF_RUNTIME" ]]; then
        echo "Failed to start suzuka-gguf runtime." >&2
        return 1
    fi

    export SUZUKA_GGUF_RUNTIME
    export SUZUKA_GGUF_RUNTIME_PID="$SUZUKA_GGUF_RUNTIME_PROCESS_PID"

    trap '
        if [[ -n "${SUZUKA_GGUF_RUNTIME_PID:-}" ]]; then
            kill "$SUZUKA_GGUF_RUNTIME_PID" 2>/dev/null || true
            wait "$SUZUKA_GGUF_RUNTIME_PID" 2>/dev/null || true
        fi
    ' EXIT
fi

echo "suzuka-gguf command enabled for this shell."
echo "  Command: $SUZUKA_GGUF_COMMAND_DIR/suzuka-gguf"
echo "  Cache:   $SUZUKA_GGUF_CACHE"
