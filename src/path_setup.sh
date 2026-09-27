#!/usr/bin/env bash

# usage: source ./path_setup.sh

SUZUKA_GGUF_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SUZUKA_GGUF_COMMAND_DIR="$SUZUKA_GGUF_DIR/.bin"
SUZUKA_GGUF_CACHE="$SUZUKA_GGUF_DIR/models"

mkdir -p "$SUZUKA_GGUF_COMMAND_DIR"
mkdir -p "$SUZUKA_GGUF_CACHE"

ln -sfn "$SUZUKA_GGUF_DIR/suzuka-llama.py" "$SUZUKA_GGUF_COMMAND_DIR/suzuka-llama"

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
