#!/usr/bin/env bash

if [ -z "${BASH_VERSION:-}" ]; then
    echo "suzuka-gguf: bash is required, but this shell is not bash." >&2
    echo "             Start bash and source it from ~/.bashrc." >&2
    return 1 2>/dev/null || exit 1
fi

SUZUKA_GGUF_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
SUZUKA_GGUF_COMMAND_DIR="$SUZUKA_GGUF_DIR/bin"
SUZUKA_GGUF_CACHE="$SUZUKA_GGUF_DIR/models"

mkdir -p "$SUZUKA_GGUF_CACHE"

case ":$PATH:" in
    *":$SUZUKA_GGUF_COMMAND_DIR:"*)
        ;;
    *)
        export PATH="$SUZUKA_GGUF_COMMAND_DIR:$PATH"
        ;;
esac

source "$SUZUKA_GGUF_COMMAND_DIR/completion.bash"

echo "suzuka-gguf command enabled for this shell."
echo "  Command: $SUZUKA_GGUF_COMMAND_DIR/suzuka-gguf"
echo "  Cache:   $SUZUKA_GGUF_CACHE"
