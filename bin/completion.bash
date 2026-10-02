#!/usr/bin/env bash

_suzuka_commands=(
    call
    info
    list
    path
    pull
    remove
)


_suzuka_dir() {
    if [[ -n "${SUZUKA_GGUF_DIR:-}" ]]; then
        printf '%s\n' "$SUZUKA_GGUF_DIR"
        return
    fi

    local command_path
    command_path="$(command -v suzuka-gguf 2>/dev/null || true)"

    if [[ -n "$command_path" ]]; then
        cd -- "$(dirname -- "$command_path")/.." 2>/dev/null && pwd
    fi
}


_suzuka_cache_args() {
    local i

    for ((i = 1; i < ${#COMP_WORDS[@]}; i++)); do
        if [[ "${COMP_WORDS[i]}" == "--cache" && $((i + 1)) -lt ${#COMP_WORDS[@]} ]]; then
            printf '%s\n' "--cache" "${COMP_WORDS[i + 1]}"
            return
        fi
    done
}


_suzuka_candidates() {
    local kind="$1"
    local dir
    local cache_args=()

    dir="$(_suzuka_dir)"
    [[ -n "$dir" && -f "$dir/suzuka_gguf/completion.py" ]] || return 0

    while IFS= read -r arg; do
        cache_args+=("$arg")
    done < <(_suzuka_cache_args)

    PYTHONPATH="$dir" \
        python3 -m suzuka_gguf.completion \
        "$kind" "${cache_args[@]}" 2>/dev/null
}


_suzuka_completion() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local command="${COMP_WORDS[1]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    local candidates

    COMPREPLY=()

    # sllama-server <model>
    if [[ "${COMP_WORDS[0]}" == "sllama-server" ]]; then
        if (( COMP_CWORD == 1 )); then
            candidates="$(_suzuka_candidates models)"

            COMPREPLY=(
                $(compgen -W "$candidates" -- "$cur")
            )
            return 0
        fi

        return 0
    fi

    # command completion
    if (( COMP_CWORD == 1 )); then
        COMPREPLY=(
            $(compgen -W "${_suzuka_commands[*]}" -- "$cur")
        )
        return 0
    fi

    # --repo value completion
    if [[ "$prev" == "--repo" ]]; then
        candidates="$(_suzuka_candidates repos)"

        COMPREPLY=(
            $(compgen -W "$candidates" -- "$cur")
        )
        return 0
    fi

    case "$command" in
        path)
            if (( COMP_CWORD == 2 )); then
                candidates="$(_suzuka_candidates models)"

                COMPREPLY=(
                    $(compgen -W "$candidates" -- "$cur")
                )
                return 0
            fi
            ;;

        info|remove|list)
            if (( COMP_CWORD == 2 )); then
                candidates="$(_suzuka_candidates repos)"

                COMPREPLY=(
                    $(compgen -W "$candidates" -- "$cur")
                )
                return 0
            fi
            ;;
    esac
}


complete -F _suzuka_completion suzuka-gguf sllama-server
