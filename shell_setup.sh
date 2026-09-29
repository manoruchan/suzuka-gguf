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

echo "suzuka-gguf command enabled for this shell."
echo "  Command: $SUZUKA_GGUF_COMMAND_DIR/suzuka-gguf"
echo "  Cache:   $SUZUKA_GGUF_CACHE"
