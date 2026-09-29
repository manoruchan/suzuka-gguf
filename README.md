# suzuka-gguf

A small GGUF manager for llama.cpp.

`suzuka-gguf` downloads GGUF models from Hugging Face, keeps them in a local cache, and helps you inspect and resolve cached models.

## Requirements

* Linux
* Bash
* Python 3
* [Hugging Face](https://huggingface.co/)
* llama.cpp `0.3.0`

The CLI interface of llama.cpp is subject to change. `suzuka-gguf` currently targets the llama.cpp `0.3.0` interface.

## Compatibility

Tested only against `llama.cpp@0.3.0` built with Spack.

Other install methods or versions are not guaranteed to work — the llama.cpp CLI interface changes between versions.

## Installation

Clone the repository:

```bash
git clone https://github.com/manoruchan/suzuka-gguf.git
cd suzuka-gguf
```

Run the setup script:

```bash
bash setup_suzuka_gguf.sh
source ~/.bashrc
```

The setup registers `init_suzuka_gguf.sh` in `.bashrc`. When sourced, `init_suzuka_gguf.sh`:

* adds `bin/` to `$PATH`
* creates the default model cache if necessary

`models/` is a runtime-generated directory and is ignored by Git.

## Cache

By default, models are stored in:

```text
<repository>/models/
```

For example:

```text
/home/suzuka/suzuka-gguf/models/
```

The cache follows the Hugging Face hub cache layout:

```text
models/
└── models--<user>--<model>/
    ├── refs/
    └── snapshots/
        └── <revision>/
            └── <files>
```

An existing cache can be used explicitly with `--cache`:

```bash
suzuka-gguf --cache /home/suzuka/.cache/huggingface/hub list
```

For `pull`, `LLAMA_CACHE` is set only for the `llama-cli` subprocess used for the download; it does not affect the calling shell.

## Commands

```text
suzuka-gguf list
suzuka-gguf list --minimal
suzuka-gguf list <user>/<model>

suzuka-gguf info <user>/<model>

suzuka-gguf path <file>
suzuka-gguf path <file> --repo <user>/<model>

suzuka-gguf pull <user>/<model>[:<quantize>]

suzuka-gguf remove <user>/<model>

suzuka-gguf call "your prompt"
```

## Listing Cached Models

The default `list` command shows cached GGUF model files across all repositories:

```bash
suzuka-gguf list
```

Example:

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

To list cached repositories without file details, use `--minimal`:

```bash
suzuka-gguf list --minimal
```

Example:

```text
Cache: /home/suzuka/suzuka-gguf/models
LiquidAI/LFM2-24B-A2B-GGUF
LiquidAI/LFM2.5-8B-A1B-GGUF
ggml-org/gemma-4-E4B-it-GGUF
unsloth/Qwen3.6-35B-A3B-MTP-GGUF
unsloth/gemma-4-26B-A4B-it-GGUF
```

A specific repository can be inspected with:

```bash
suzuka-gguf list ggml-org/gemma-4-E4B-it-GGUF
```

Example:

```text
   4.3 GiB  gemma-4-E4B-it-Q4_0.gguf
 533.9 MiB  mmproj-gemma-4-E4B-it-Q8_0.gguf
```

## Repository Information

```bash
suzuka-gguf info LiquidAI/LFM2-24B-A2B-GGUF
```

Example:

```text
Repository : LiquidAI/LFM2-24B-A2B-GGUF
Cache path : /home/suzuka/suzuka-gguf/models/models--LiquidAI--LFM2-24B-A2B-GGUF
Size       : 13.4 GiB
Revision   : 6247d03b87c27c05a258feb5acdfb4d5efbf0bd8
Snapshot   : /home/suzuka/suzuka-gguf/models/models--LiquidAI--LFM2-24B-A2B-GGUF/snapshots/6247d03b87c27c05a258feb5acdfb4d5efbf0bd8
```

Shows metadata for a cached repository.

## Resolving Model Paths

`path` resolves a cached model file to its actual path.

When the filename is unique across the cache, the repository does not need to be specified:

```bash
suzuka-gguf path Ternary-Bonsai-2-27B-PTQ1_0.gguf
```

Output:

```text
/home/suzuka/suzuka-gguf/models/models--prism-ml--Ternary-Bonsai-2-27B-gguf/snapshots/6ed5e12bf84b7a63069882c91dd9e9218647d17b/Ternary-Bonsai-2-27B-PTQ1_0.gguf
```

If the same filename exists in multiple repositories, specify the repository explicitly:

```bash
suzuka-gguf path Ternary-Bonsai-2-27B-PTQ1_0.gguf \
    --repo prism-ml/Ternary-Bonsai-2-27B-gguf
```

The returned path can be passed directly to any llama.cpp build:

```bash
llama-cli \
    -m "$(suzuka-gguf path gemma-4-E4B-it-Q4_0.gguf)" \
    -p "こんにちは！"
```

`suzuka-gguf` does not need a build with support for a given model — it only resolves the file path. For example, a Ternary-quantized model that requires a llama.cpp fork can be resolved the same way and handed to that fork directly:

```bash
~/prism-llama.cpp/build/bin/llama-cli \
    -m "$(suzuka-gguf path Ternary-Bonsai-2-27B-PTQ1_0.gguf)" \
    -p "こんにちは！"
```

## Pulling Models

Download a GGUF repository from Hugging Face:

```bash
suzuka-gguf pull prism-ml/Ternary-Bonsai-2-27B-gguf
```

Or download a specific quantization:

```bash
suzuka-gguf pull prism-ml/Ternary-Bonsai-2-27B-gguf:TQ1_0
```

The download is performed through `llama-cli`, with its `LLAMA_CACHE` directed to `suzuka-gguf`'s cache.

If multimodal projector files are not needed:

```bash
suzuka-gguf pull <user>/<model> --no-mmproj
```

## Removing Models

```bash
suzuka-gguf remove unsloth/gemma-4-26B-A4B-it-GGUF
```

**Warning:** `remove` deletes the entire cached repository, including all downloaded GGUF files. It does not currently support removing an individual file, and the operation cannot be undone.

## Calling the Model

```bash
suzuka-gguf call "Explain what a GGUF file is."
```

Sends the prompt to a running local `llama-server` OpenAI-compatible API and streams the response.

## Typical Workflow

`suzuka-gguf` is primarily intended to manage a local GGUF cache and resolve models for whichever llama.cpp build you want to use.

```bash
# 1. Find a GGUF on Hugging Face

# 2. Pull it
suzuka-gguf pull <user>/<model>:<quantize>

# 3. Inspect the cache
suzuka-gguf list

# 4. Resolve the model path
suzuka-gguf path <file>

# 5. Run it with your own llama.cpp build
llama-cli -m "$(suzuka-gguf path <file>)"
```

## Design

`suzuka-gguf` is primarily a cache manager and model resolver.

```text
                     Hugging Face
                          │
                          ▼
                      llama-cli
                          │
                          ▼
                    suzuka-gguf
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
           cache        inspect      resolve
             │            │            │
             │           list         path
             │                         │
             │                         │
             │                         │
             └────────────┬────────────┘
                          ▼
                   any llama.cpp build
```

`suzuka-gguf` manages GGUF models and provides a bridge between the model ecosystem on Hugging Face and the llama.cpp build you actually want to use.
