#!/usr/bin/env bash

_suzuka_gguf_completion() {
    local cur="${COMP_WORDS[COMP_CWORD]}"

    if (( COMP_CWORD != 1 )); then
        return 0
    fi

    local commands=(
        call
        info
        list
        path
        pull
        remove
    )

    COMPREPLY=(
        $(compgen -W "${commands[*]}" -- "$cur")
    )
}

complete -F _suzuka_gguf_completion suzuka-gguf
