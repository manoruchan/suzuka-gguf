#!/usr/bin/env bash

set -euo pipefail

SUZUKA_GGUF_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BASHRC="$HOME/.bashrc"

mkdir -p "$SUZUKA_GGUF_DIR/models"
mkdir -p "$SUZUKA_GGUF_DIR/log"

chmod +x ~/suzuka-gguf-alpha/bin/suzuka-gguf

if ! grep -Fqx "# suzuka-gguf" "$BASHRC"; then
    {
        echo
        echo "# suzuka-gguf"
        echo "source \"$SUZUKA_GGUF_DIR/shell_setup.sh\""
    } >> "$BASHRC"
else
    echo "Warning: existing suzuka-gguf configuration found in $BASHRC." >&2
    echo "         Please check the suzuka-gguf source path manually if this repository was moved." >&2
fi

echo "Configured suzuka-gguf:"
echo "  Repository: $SUZUKA_GGUF_DIR"
echo "  Cache:      $SUZUKA_GGUF_DIR/models"
echo "  Log:        $SUZUKA_GGUF_DIR/log"
echo
echo "Run:"
echo "  source ~/.bashrc"
