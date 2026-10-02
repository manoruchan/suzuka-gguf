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


def cli_filename(filename: str) -> str:
    if filename.endswith(".gguf"):
        return filename[:-5]
    return filename


def normalize_model_filename(filename: str) -> str:
    if not filename.endswith(".gguf"):
        return filename + ".gguf"
    return filename
