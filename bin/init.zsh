#!/usr/bin/env zsh

# zsh glue for suzuka-gguf.  `bin/setup.sh` adds one line to ~/.zshrc:
#
#     source "<repository>/bin/init.zsh"
#
# It only puts bin/ on $PATH and points the cache at <repository>/models;
# the commands themselves are shell independent.

if [[ -z ${ZSH_VERSION:-} ]]; then
    echo "suzuka-gguf: init.zsh must be sourced from zsh." >&2
    return 1 2>/dev/null || exit 1
fi

_suzuka_self="${(%):-%x}"
SUZUKA_GGUF_DIR="${_suzuka_self:A:h:h}"
unset _suzuka_self

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

echo "suzuka-gguf command enabled for this shell."
echo "  Command: $SUZUKA_GGUF_COMMAND_DIR/suzuka-gguf"
echo "  Cache:   $SUZUKA_GGUF_CACHE"
