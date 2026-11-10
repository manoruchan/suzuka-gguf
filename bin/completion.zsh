#compdef suzuka-gguf

# zsh completion for suzuka-gguf, sourced from bin/init.zsh.
#
# Candidate lists come from suzuka_gguf/completion.py, the same helper the
# bash completion uses, so both shells offer the same names.

_suzuka_commands=(call info list path pull remove)


_suzuka_gguf_dir() {
    if [[ -n ${SUZUKA_GGUF_DIR:-} ]]; then
        print -r -- "$SUZUKA_GGUF_DIR"
        return 0
    fi

    print -r -- "${${(%):-%x}:h:h}"
}


# Cache options already present on the command line, as an array in reply.
_suzuka_cache_args() {
    local i

    reply=()

    for (( i = 2; i < CURRENT; i++ )); do
        case ${words[i]} in
            --cache)
                reply=( --cache "${words[i+1]}" )
                ;;
            --cache=*)
                reply=( --cache "${words[i]#--cache=}" )
                ;;
        esac
    done
}


# Fill reply with candidates.  $1 kind, $2 optional repository.
_suzuka_candidates() {
    local kind=$1
    local repo=${2:-}
    local dir
    local -a args cache_args

    dir=$(_suzuka_gguf_dir)
    [[ -n $dir && -f $dir/suzuka_gguf/completion.py ]] || return 1

    _suzuka_cache_args
    cache_args=( "${reply[@]}" )

    args=( "$kind" )
    [[ -n $repo ]] && args+=( --repo "$repo" )

    reply=(
        ${(f)"$(PYTHONPATH=$dir python3 -m suzuka_gguf.completion "${args[@]}" "${cache_args[@]}" 2>/dev/null)"}
    )
    reply=( ${reply:#} )
}


_suzuka_flags() {
    case $1 in
        call)   print -l -- --host --port ;;
        list)   print -l -- --minimal ;;
        path)   print -l -- --repo ;;
        pull)   print -l -- --file --no-mmproj ;;
        remove) print -l -- --file -y --yes ;;
    esac
}


# Candidates for --file.  `pull --file` names a file inside the Hugging Face
# repository, so the local cache has nothing to offer.
_suzuka_file_candidates() {
    local cmd=$1
    local repo=$2

    [[ $cmd == pull ]] && return 1

    _suzuka_candidates gguf-files "$repo"
}


_suzuka_offer_files() {
    if (( ${#reply} )); then
        _describe -t files 'cached GGUF' reply
    else
        _message 'no cached GGUF'
    fi
}


_suzuka_gguf() {
    emulate -L zsh
    setopt extendedglob

    local cur=${words[CURRENT]}
    local prev=${words[CURRENT-1]}
    local cmd index i repo
    local -a positional flags

    # --cache is global and takes a directory
    if [[ $prev == --cache ]]; then
        _directories
        return 0
    fi

    if [[ $cur == --cache=* ]]; then
        compset -P '--cache='
        _directories
        return 0
    fi

    # subcommand position
    index=

    for (( i = 2; i < CURRENT; i++ )); do
        case ${words[i]} in
            --cache)
                (( i++ ))
                ;;
            --cache=*|-*)
                ;;
            *)
                index=$i
                break
                ;;
        esac
    done

    if [[ -z $index ]]; then
        if [[ $cur == -* ]]; then
            compadd -- --cache
        else
            _describe -t commands 'suzuka-gguf command' _suzuka_commands
        fi
        return 0
    fi

    cmd=${words[index]}

    # repository already named on the line (--repo, or the positional of
    # info / remove / list)
    repo=

    for (( i = 2; i < ${#words[@]}; i++ )); do
        case ${words[i]} in
            --repo)
                repo=${words[i+1]}
                ;;
            --repo=*)
                repo=${words[i]#--repo=}
                ;;
        esac
    done

    if [[ -z $repo ]]; then
        case $cmd in
            info|remove|list)
                if [[ -n ${words[index + 1]:-} && ${words[index+1]} != -* ]]; then
                    repo=${words[index+1]}
                fi
                ;;
        esac
    fi

    # option values
    case $prev in
        --repo)
            _suzuka_candidates repos
            _describe -t repositories 'cached repository' reply
            return 0
            ;;
        --file)
            _suzuka_file_candidates "$cmd" "$repo" && _suzuka_offer_files
            return 0
            ;;
    esac

    case $cur in
        --repo=*)
            compset -P '--repo='
            _suzuka_candidates repos
            _describe -t repositories 'cached repository' reply
            return 0
            ;;
        --file=*)
            compset -P '--file='
            _suzuka_file_candidates "$cmd" "$repo" && _suzuka_offer_files
            return 0
            ;;
        -*)
            flags=( ${(f)"$(_suzuka_flags "$cmd")"} )
            (( ${#flags} )) && compadd -- "${flags[@]}"
            return 0
            ;;
    esac

    # first positional argument
    positional=()

    for (( i = index + 1; i < CURRENT; i++ )); do
        case ${words[i]} in
            --cache|--repo|--file|--host|--port)
                (( i++ ))
                ;;
            --*=*|-*)
                ;;
            *)
                positional+=( "${words[i]}" )
                ;;
        esac
    done

    (( ${#positional} )) && return 0

    case $cmd in
        path)
            if [[ -n $repo ]]; then
                _suzuka_candidates gguf-files "$repo"
            else
                _suzuka_candidates models
            fi
            _suzuka_offer_files
            ;;
        info|remove|list)
            _suzuka_candidates repos
            _describe -t repositories 'cached repository' reply
            ;;
    esac

    return 0
}


if (( $+functions[compdef] )); then
    compdef _suzuka_gguf suzuka-gguf
else
    print -u2 "suzuka-gguf: zsh completion needs compinit; run 'autoload -Uz compinit && compinit' and source bin/init.zsh again."
fi
