# suzuka-gguf

A small GGUF manager for llama.cpp.

Download GGUF models from Hugging Face, keep them in a local cache, and resolve them to file paths for whichever llama.cpp build you want to use.

**Shell autocompletion is included.**

## Features

* **Tab completion** — cached model files complete for `path` and `sllama-server`, cached repositories for `info` and `remove`
* **Minimally invasive** — one line in `.bashrc` that adds `bin/` to `$PATH`; no shims, no global state
* **Build-agnostic** — only resolves paths, so it works with any llama.cpp build or fork
* **Built-in help** — `suzuka-gguf --help` (and `suzuka-gguf <command> --help`)

## Quick Start

```bash
# Pull a model
suzuka-gguf pull prism-ml/Ternary-Bonsai-2-27B-gguf:TQ1_0

# See what's cached
suzuka-gguf list

# Resolve and run with your own llama.cpp build (press <Tab> after "path")
llama-cli -m "$(suzuka-gguf path Ternary-Bonsai-2-27B-PTQ1_0)"
```

## Requirements

* Linux
* Bash
* Python 3
* Network access to [Hugging Face](https://huggingface.co/)
* llama.cpp `0.3.0` (built with Spack)

> [!NOTE]
> Tested only against `llama.cpp@0.3.0` built with Spack. The llama.cpp CLI changes between versions, so other versions or install methods are not guaranteed to work.

## Installation

```bash
git clone https://github.com/manoruchan/suzuka-gguf.git
cd suzuka-gguf
bash bin/setup.sh
source ~/.bashrc
```

The setup registers `bin/init.sh` in `.bashrc`. When sourced, it adds `bin/` to `$PATH`, enables completion, and creates the default model cache if necessary.

## Commands

Run `suzuka-gguf --help` for the full list of commands and options.

| Command | Description |
| --- | --- |
| `suzuka-gguf list [<user>/<model>] [--minimal]` | List cached GGUF files (`--minimal`: repository names only) |
| `suzuka-gguf info <user>/<model>` | Show metadata of a cached repository |
| `suzuka-gguf path <file> [--repo <user>/<model>]` | Resolve a cached file to its real path |
| `suzuka-gguf pull <user>/<model>[:<quantize>] [--file <file>] [--no-mmproj]` | Download a model |
| `suzuka-gguf remove <user>/<model> [-y]` | Delete a cached repository |
| `suzuka-gguf call "prompt" [--host <host>] [--port <port>]` | Send a prompt to a running `llama-server` |
| `sllama-server <model> [options...]` | Start `llama-server` with a cached model |

## Usage

### Pull

```bash
# Repository only (a single .gguf is selected by the Hugging Face resolver)
suzuka-gguf pull prism-ml/Ternary-Bonsai-2-27B-gguf

# Specific quantization
suzuka-gguf pull prism-ml/Ternary-Bonsai-2-27B-gguf:TQ1_0

# Specific file
suzuka-gguf pull prism-ml/Ternary-Bonsai-2-27B-gguf --file Ternary-Bonsai-2-27B-PTQ1_0.gguf

# Skip multimodal projector files
suzuka-gguf pull <user>/<model> --no-mmproj
```

`pull` is a thin wrapper around `llama-cli`. If you specify only a repository, the Hugging Face resolver picks a single `.gguf` to download; use `:<quantize>` or `--file` to choose explicitly.

`LLAMA_CACHE` is set only for the `llama-cli` subprocess, so your shell is unaffected.

### List

```bash
suzuka-gguf list
suzuka-gguf list --minimal
suzuka-gguf list ggml-org/gemma-4-E4B-it-GGUF
```

<details>
<summary>Example output</summary>

`suzuka-gguf list`

```text
Cache: /home/suzuka/suzuka-gguf/models

LiquidAI/LFM2-24B-A2B-GGUF  (6247d03b87c2)
    13.4 GiB  LFM2-24B-A2B-Q4_K_M.gguf

LiquidAI/LFM2.5-8B-A1B-GGUF  (49c148317070)
     4.8 GiB  LFM2.5-8B-A1B-Q4_K_M.gguf
     8.4 GiB  LFM2.5-8B-A1B-Q8_0.gguf

ggml-org/gemma-4-E4B-it-GGUF  (b8093469224f)
     4.3 GiB  gemma-4-E4B-it-Q4_0.gguf

unsloth/Qwen3.6-35B-A3B-MTP-GGUF  (5bc3e238d916)
    21.1 GiB  Qwen3.6-35B-A3B-UD-Q4_K_M.gguf

unsloth/gemma-4-26B-A4B-it-GGUF  (c099eb48e663)
    15.8 GiB  gemma-4-26B-A4B-it-UD-Q4_K_M.gguf
```

`suzuka-gguf list --minimal`

```text
Cache: /home/suzuka/suzuka-gguf/models
LiquidAI/LFM2-24B-A2B-GGUF
LiquidAI/LFM2.5-8B-A1B-GGUF
ggml-org/gemma-4-E4B-it-GGUF
unsloth/Qwen3.6-35B-A3B-MTP-GGUF
unsloth/gemma-4-26B-A4B-it-GGUF
```

`suzuka-gguf list ggml-org/gemma-4-E4B-it-GGUF`

```text
   4.3 GiB  gemma-4-E4B-it-Q4_0.gguf
 533.9 MiB  mmproj-gemma-4-E4B-it-Q8_0.gguf
```

</details>

### Info

```bash
suzuka-gguf info LiquidAI/LFM2-24B-A2B-GGUF
```

<details>
<summary>Example output</summary>

```text
Repository : LiquidAI/LFM2-24B-A2B-GGUF
Cache path : /home/suzuka/suzuka-gguf/models/models--LiquidAI--LFM2-24B-A2B-GGUF
Size       : 13.4 GiB
Revision   : 6247d03b87c27c05a258feb5acdfb4d5efbf0bd8
Snapshot   : /home/suzuka/suzuka-gguf/models/models--LiquidAI--LFM2-24B-A2B-GGUF/snapshots/6247d03b87c27c05a258feb5acdfb4d5efbf0bd8
```

</details>

### Resolve a model path

`path` resolves a cached file to its actual path. If the filename is unique across the cache, `--repo` is not needed.

```bash
suzuka-gguf path Ternary-Bonsai-2-27B-PTQ1_0
```

If the same filename exists in multiple repositories, specify the repository:

```bash
suzuka-gguf path Ternary-Bonsai-2-27B-PTQ1_0 --repo prism-ml/Ternary-Bonsai-2-27B-gguf
```

The result can be passed to any llama.cpp build, including forks:

```bash
llama-cli -m "$(suzuka-gguf path gemma-4-E4B-it-Q4_0)"

# e.g. a fork that supports Ternary quantization
~/prism-llama.cpp/build/bin/llama-cli -m "$(suzuka-gguf path Ternary-Bonsai-2-27B-PTQ1_0)"
```

`suzuka-gguf` only resolves file paths, so it doesn't need a build that supports the model.

### Remove

```bash
suzuka-gguf remove unsloth/gemma-4-26B-A4B-it-GGUF

# Skip the confirmation prompt
suzuka-gguf remove unsloth/gemma-4-26B-A4B-it-GGUF -y
```

> [!WARNING]
> `remove` deletes the **entire cached repository**, including all downloaded GGUF files. Removing a single file is not supported, and this cannot be undone.

### Run llama-server

`sllama-server` resolves a cached model through `suzuka-gguf` and passes the path to `llama-server`. Extra arguments are forwarded as-is.

```bash
sllama-server Qwen3-Coder-30B-A3B-Instruct-IQ4_XS --threads 8 --ctx-size 32768
```

### Call

```bash
suzuka-gguf call "Explain what a GGUF file is."

# Non-default server
suzuka-gguf call "Hello" --host 192.168.1.10 --port 8081
```

Sends the prompt to a running `llama-server` (OpenAI-compatible API) and streams the response. Defaults to `127.0.0.1:8080`.

## Cache

Models are stored in `<repository>/models/` by default (e.g. `/home/suzuka/suzuka-gguf/models/`). This directory is generated at runtime and ignored by Git.

To use an existing Hugging Face cache instead, pass `--cache`:

```bash
suzuka-gguf --cache /home/suzuka/.cache/huggingface/hub list
```

<details>
<summary>Cache layout</summary>

The cache follows the Hugging Face hub layout:

```text
models/
└── models--<user>--<model>/
    ├── refs/
    └── snapshots/
        └── <revision>/
            └── <files>
```

</details>

## Design

`suzuka-gguf` is a cache manager and model resolver. It bridges the Hugging Face model ecosystem and the llama.cpp build you actually want to use.

```text
Hugging Face → llama-cli → suzuka-gguf ─┬─ cache
                                        ├─ inspect (list / info)
                                        └─ resolve (path) → any llama.cpp build
```
