#!/usr/bin/env bash

set -euo pipefail

SUZUKA_GGUF_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"

SHELL_NAME="${SHELL:-}"
SHELL_NAME="${SHELL_NAME##*/}"

case "$SHELL_NAME" in
    zsh)
        RC="$HOME/.zshrc"
        INIT="$SUZUKA_GGUF_DIR/bin/init.zsh"
        ;;
    bash | "")
        RC="$HOME/.bashrc"
        INIT="$SUZUKA_GGUF_DIR/bin/init.sh"
        ;;
    *)
        echo "Warning: unrecognized shell '$SHELL_NAME', assuming bash." >&2
        RC="$HOME/.bashrc"
        INIT="$SUZUKA_GGUF_DIR/bin/init.sh"
        ;;
esac

mkdir -p "$SUZUKA_GGUF_DIR/models"

chmod +x "$SUZUKA_GGUF_DIR/bin/suzuka-gguf"
chmod +x "$SUZUKA_GGUF_DIR/bin/init.zsh"

if ! grep -Fqx "# suzuka-gguf" "$RC" 2>/dev/null; then
    {
        echo
        echo "# suzuka-gguf"
        echo "source \"$INIT\""
    } >> "$RC"
else
    echo "Warning: existing suzuka-gguf configuration found in $RC." >&2
    echo "         Remove it and re-run this script if this repository was moved." >&2
fi

echo "Configured suzuka-gguf:"
echo "  Repository: $SUZUKA_GGUF_DIR"
echo "  Cache:      $SUZUKA_GGUF_DIR/models"
echo "  Shell:      ${SHELL_NAME:-bash}"
echo "  Init:       $INIT"

echo

echo "Run:"
echo "  source $RC"
