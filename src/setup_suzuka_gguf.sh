#!/usr/bin/env bash

set -euo pipefail

LLAMA_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

PYTHON_FILE="$LLAMA_DIR/suzuka-gguf.py"
BASHRC="$HOME/.bashrc"

cp "$LLAMA_DIR/src/suzuka-gguf.src" "$PYTHON_FILE" # overwrites the file if already exists
chmod +x "$PYTHON_FILE"

mkdir -p "$LLAMA_DIR/models"
mkdir -p "$LLAMA_DIR/.bin"

ln -sfn "$PYTHON_FILE" "$LLAMA_DIR/.bin/suzuka-gguf"

if ! grep -Fqx "# suzuka-gguf" "$BASHRC"; then
    {
        echo
        echo "# suzuka-gguf"
        echo "source \"$LLAMA_DIR/src/path_setup.sh\""
    } >> "$BASHRC"
else
    echo "Warning: existing suzuka-gguf configuration found in $BASHRC." >&2
    echo "         Please check the suzuka-gguf source path manually if this repository was moved." >&2
fi

echo "Configured suzuka-gguf:"
echo "  Repository: $LLAMA_DIR"
echo "  Cache:      $LLAMA_DIR/models"
echo
echo "Run:"
echo "  source ~/.bashrc"
