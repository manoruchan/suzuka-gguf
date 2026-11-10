#!/usr/bin/env bash

_suzuka_commands=(
    call
    info
    list
    path
    pull
    remove
)


# Directory that holds this file (bin/), used when init.sh did not export
# SUZUKA_GGUF_DIR (e.g. completion.bash sourced on its own).
_suzuka_own_dir() {
    cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd
}


_suzuka_dir() {
    if [[ -n "${SUZUKA_GGUF_DIR:-}" ]]; then
        printf '%s\n' "$SUZUKA_GGUF_DIR"
        return
    fi

    local command_path
    command_path="$(command -v suzuka-gguf 2>/dev/null || true)"

    if [[ -n "$command_path" ]]; then
        cd -- "$(dirname -- "$command_path")/.." 2>/dev/null && pwd
        return
    fi

    _suzuka_own_dir
}


_suzuka_cache_args() {
    local i

    for ((i = 1; i < ${#COMP_WORDS[@]}; i++)); do
        case "${COMP_WORDS[i]}" in
            --cache)
                if ((i + 1 < ${#COMP_WORDS[@]})); then
                    printf '%s\n' "--cache" "${COMP_WORDS[i + 1]}"
                fi
                return
                ;;
            --cache=*)
                printf '%s\n' "--cache" "${COMP_WORDS[i]#--cache=}"
                return
                ;;
        esac
    done
}


# Ask the Python helper for candidates.  $1 is the kind, $2 an optional repo.
_suzuka_candidates() {
    local kind="$1"
    local repo="${2:-}"
    local dir
    local cache_args=()
    local completion_args=("$kind")

    dir="$(_suzuka_dir)"
    [[ -n "$dir" && -f "$dir/suzuka_gguf/completion.py" ]] || return 0

    while IFS= read -r arg; do
        [[ -n "$arg" ]] && cache_args+=("$arg")
    done < <(_suzuka_cache_args)

    if [[ -n "$repo" ]]; then
        completion_args+=(--repo "$repo")
    fi

    PYTHONPATH="$dir" \
        python3 -m suzuka_gguf.completion \
        "${completion_args[@]}" "${cache_args[@]}" 2>/dev/null
}


# Index of the subcommand word, skipping global options and their values.
_suzuka_command_index() {
    local i=1

    while ((i < COMP_CWORD)); do
        case "${COMP_WORDS[i]}" in
            --cache)
                i=$((i + 2))
                ;;
            --cache=*)
                i=$((i + 1))
                ;;
            -*)
                i=$((i + 1))
                ;;
            *)
                printf '%s\n' "$i"
                return 0
                ;;
        esac
    done

    return 1
}


# Value of --repo if it already appears on the line.
_suzuka_repo_value() {
    local i

    for ((i = 1; i < ${#COMP_WORDS[@]}; i++)); do
        case "${COMP_WORDS[i]}" in
            --repo)
                [[ -n "${COMP_WORDS[i + 1]:-}" ]] && printf '%s\n' "${COMP_WORDS[i + 1]}"
                return 0
                ;;
            --repo=*)
                printf '%s\n' "${COMP_WORDS[i]#--repo=}"
                return 0
                ;;
        esac
    done

    return 1
}


# Repository passed positionally, e.g. `remove <repo> --file`.
_suzuka_positional_repo() {
    local index="$1"
    local repo="${COMP_WORDS[index + 1]:-}"

    if [[ -n "$repo" && "$repo" != -* && $((index + 1)) -lt $COMP_CWORD ]]; then
        printf '%s\n' "$repo"
    fi
}


_suzuka_flags() {
    case "$1" in
        call)   printf '%s\n' --host --port ;;
        info)   printf '%s\n' ;;
        list)   printf '%s\n' --minimal ;;
        path)   printf '%s\n' --repo ;;
        pull)   printf '%s\n' --file --no-mmproj ;;
        remove) printf '%s\n' --file -y --yes ;;
        *)      ;;
    esac

    printf '%s\n' --cache
}


# Match a newline-separated candidate list against the current word.
_suzuka_reply() {
    local cur="$1"
    local candidates="$2"
    local candidate

    COMPREPLY=()

    while IFS= read -r candidate; do
        [[ -z "$candidate" ]] && continue
        [[ ${candidate:0:${#cur}} == "$cur" ]] || continue
        COMPREPLY+=("$candidate")
    done <<< "$candidates"
}


# Same, for `--opt=value` forms: strip the prefix from the word being typed.
_suzuka_reply_prefixed() {
    local prefix="$1"
    local cur="$2"
    local candidates="$3"
    local candidate

    COMPREPLY=()

    while IFS= read -r candidate; do
        [[ -z "$candidate" ]] && continue
        [[ ${candidate:0:${#cur}} == "$cur" ]] || continue
        COMPREPLY+=("$prefix$candidate")
    done <<< "$candidates"

    case "$prefix" in
        --cache=*)
            compopt -o nospace 2>/dev/null || true
            ;;
    esac
}


_suzuka_reply_dirs() {
    local cur="$1"
    local dir
    local count=0

    COMPREPLY=()

    while IFS= read -r dir; do
        [[ -z "$dir" ]] && continue
        COMPREPLY+=("$dir/")
        count=$((count + 1))
    done < <(compgen -d -- "$cur" 2>/dev/null)

    if ((count > 0)); then
        compopt -o nospace 2>/dev/null || true
    fi
}


_suzuka_cached_files() {
    local command="$1"
    local index="$2"
    local repo

    case "$command" in
        pull)
            # --file here names a file inside the Hugging Face repository;
            # the local cache has nothing useful to offer.
            return 0
            ;;
    esac

    repo="$(_suzuka_repo_value || _suzuka_positional_repo "$index")"
    _suzuka_candidates gguf-files "$repo"
}


_suzuka_completion() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    local index command

    COMPREPLY=()

    # sllama-server <model>
    if [[ "${COMP_WORDS[0]}" == "sllama-server" ]]; then
        if ((COMP_CWORD == 1)); then
            _suzuka_reply "$cur" "$(_suzuka_candidates models)"
        fi
        return 0
    fi

    # global --cache value
    if [[ "$prev" == "--cache" ]]; then
        _suzuka_reply_dirs "$cur"
        return 0
    fi
    if [[ "$cur" == --cache=* ]]; then
        _suzuka_reply_prefixed "--cache=" "${cur#--cache=}" \
            "$(compgen -d -- "${cur#--cache=}" 2>/dev/null | sed 's:$:/:')"
        return 0
    fi

    index="$(_suzuka_command_index || true)"

    # command name
    if [[ -z "$index" ]]; then
        if [[ "$cur" == -* ]]; then
            _suzuka_reply "$cur" "--cache"
        else
            _suzuka_reply "$cur" "$(printf '%s\n' "${_suzuka_commands[@]}")"
        fi
        return 0
    fi

    command="${COMP_WORDS[index]}"

    # option values
    case "$prev" in
        --repo)
            _suzuka_reply "$cur" "$(_suzuka_candidates repos)"
            return 0
            ;;
        --file)
            _suzuka_reply "$cur" "$(_suzuka_cached_files "$command" "$index")"
            return 0
            ;;
    esac

    if [[ "$cur" == --repo=* ]]; then
        _suzuka_reply_prefixed "--repo=" "${cur#--repo=}" \
            "$(_suzuka_candidates repos)"
        return 0
    fi

    if [[ "$cur" == --file=* ]]; then
        _suzuka_reply_prefixed "--file=" "${cur#--file=}" \
            "$(_suzuka_cached_files "$command" "$index")"
        return 0
    fi

    # flags
    if [[ "$cur" == -* ]]; then
        _suzuka_reply "$cur" "$(_suzuka_flags "$command")"
        return 0
    fi

    # positional arguments
    if ((COMP_CWORD == index + 1)); then
        case "$command" in
            path)
                _suzuka_reply "$cur" "$(_suzuka_candidates models)"
                ;;
            info|remove|list)
                _suzuka_reply "$cur" "$(_suzuka_candidates repos)"
                ;;
        esac
    fi

    return 0
}


complete -F _suzuka_completion suzuka-gguf sllama-server
