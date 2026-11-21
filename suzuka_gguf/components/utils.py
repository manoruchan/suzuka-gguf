from pathlib import Path


def human_size(n: int) -> str:
    value = float(n)

    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{n} B"


def directory_size(path: Path) -> int:
    total = 0

    if not path.exists():
        return 0

    for p in path.rglob("*"):
        try:
            if p.is_file() and not p.is_symlink():
                total += p.stat().st_size
        except OSError:
            pass

    return total


GGUF_SUFFIXES = (".gguf", ".gguf_file")


def cli_filename(filename: str) -> str:
    if filename.endswith(".gguf"):
        return filename[:-5]
    return filename


def is_gguf_filename(filename: str) -> bool:
    return filename.endswith(GGUF_SUFFIXES)


def normalize_model_filename(filename: str) -> str:
    """Return filename with a .gguf suffix when it carries no GGUF suffix.

    A name that is already a file name — "model-Q4_K_M.gguf" as well as the
    tagged form "model-Q4_K_M.gguf_file" — is returned unchanged, so a name
    that comes from a repository is never renamed.
    """
    name = Path(filename).name

    if not name or is_gguf_filename(name.lower()):
        return filename

    return filename + ".gguf"


def model_filename_candidates(filename: str) -> list[str]:
    """Return the names to try for a name given by the user, in order.

    A name that already carries a GGUF suffix is used as it is. A bare name
    also tries the suffixes repositories publish, and a candidate is only
    used once the corresponding file exists, so a name is never invented.
    """
    if is_gguf_filename(filename):
        return [filename]

    return [filename, filename + ".gguf", filename + ".gguf_file"]
