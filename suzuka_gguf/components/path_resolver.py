from typing import Final
from pathlib import Path


class PathResolver:
    PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
    DEFAULT_CACHE_PATH: Final[Path] = PROJECT_ROOT / "models"

    def default_cache_path() -> Path:
        return PathResolver.DEFAULT_CACHE_PATH

    @staticmethod
    def repo_dir(repo: str, path: Path | None = None) -> Path:
        resolved_path = (
            path
            if path is not None
            else PathResolver.DEFAULT_CACHE_PATH
        )

        if "/" not in repo or repo.startswith("/") or ".." in Path(repo).parts:
            raise ValueError(f"invalid repository name: {repo!r}")

        org, model = repo.split("/", 1)
        return resolved_path / f"models--{org}--{model}"

    @staticmethod
    def repo_from_dir(path: Path) -> str | None:
        name = path.name

        if not name.startswith("models--"):
            return None

        rest = name[len("models--"):]

        if "--" not in rest:
            return None

        org, model = rest.split("--", 1)
        return f"{org}/{model}"

    @staticmethod
    def repository_from_model_path(model_path: Path) -> Path:
        """
        Return the Hugging Face repository directory containing model_path.

        Expected layout:

            <cache>/models--org--model/snapshots/<revision>/<file>
        """
        try:
            return model_path.parents[2]
        except IndexError:
            raise RuntimeError(
                f"cannot determine repository from model path: {model_path}"
            )
