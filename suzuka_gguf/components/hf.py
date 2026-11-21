from __future__ import annotations

import json
import urllib.error
import urllib.request

from suzuka_gguf.components.utils import model_filename_candidates


REPOSITORY_API = "https://huggingface.co/api/models/{repo}/tree/main"
LISTING_LIMIT = 1000
LISTING_TIMEOUT = 30.0


def repository_files(
    repo: str,
    timeout: float = LISTING_TIMEOUT,
) -> list[str]:
    """Return the paths of the files in the main branch of a repository.

    The whole tree is listed, so files in a subdirectory keep their relative
    path. Raises RuntimeError when the list cannot be read, which leaves the
    decision to fall back to the caller.
    """
    url = (
        f"{REPOSITORY_API.format(repo=repo)}"
        f"?recursive=true&limit={LISTING_LIMIT}"
    )

    paths = []

    while url:
        request = urllib.request.Request(
            url,
            headers={"Accept": "application/json"},
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=timeout,
            ) as response:
                entries = json.load(response)
                url = _next_page(response.headers.get("Link", ""))
        except urllib.error.HTTPError as exc:
            hint = (
                " (the repository may be missing or private)"
                if exc.code in (401, 403, 404)
                else ""
            )
            raise RuntimeError(
                f"cannot list the files of {repo}: HTTP {exc.code}{hint}"
            ) from exc
        except (urllib.error.URLError, OSError) as exc:
            raise RuntimeError(
                f"cannot reach huggingface.co for {repo}: {exc}"
            ) from exc
        except ValueError as exc:
            raise RuntimeError(
                f"cannot read the file list of {repo}: {exc}"
            ) from exc

        if not isinstance(entries, list):
            raise RuntimeError(f"unexpected file list for {repo}")

        paths.extend(
            entry["path"]
            for entry in entries
            if entry.get("type") == "file" and entry.get("path")
        )

    return sorted(paths)


def _next_page(link_header: str) -> str | None:
    for part in link_header.split(","):
        target, _, parameters = part.partition(";")

        if 'rel="next"' in parameters:
            return target.strip().strip("<>")

    return None


def match_repository_file(files: list[str], filename: str) -> str:
    """Resolve a name given by the user against the files of a repository.

    The name wins as soon as it is a file in the repository, so a file that
    is not named "*.gguf" is never renamed: "model-Q4_K_M.gguf_file" is a
    name, not an abbreviation. The extension is only completed when the name
    itself matches nothing, and every completed name has to exist in the
    repository, so a name is never invented.
    """
    candidates = model_filename_candidates(filename)
    available = set(files)

    direct = [candidate for candidate in candidates if candidate in available]

    if len(direct) == 1:
        return direct[0]

    if direct:
        raise RuntimeError(_ambiguous_message(direct))

    if "/" not in filename:
        matches = [
            path
            for path in files
            if path.rsplit("/", 1)[-1] in candidates
        ]

        if len(matches) == 1:
            return matches[0]

        if matches:
            raise RuntimeError(_ambiguous_message(matches))

    raise RuntimeError(_not_found_message(files, filename))


def _ambiguous_message(matches: list[str]) -> str:
    return "ambiguous file name; use one of: " + ", ".join(sorted(matches))


def _not_found_message(files: list[str], filename: str) -> str:
    message = f"file not found in the repository: {filename!r}"

    if not files:
        return message + " (the repository has no files)"

    directory, _, _ = filename.rpartition("/")

    nearby = [
        path
        for path in files
        if directory and path.startswith(directory + "/")
    ]

    visible = [
        path
        for path in (nearby or files)
        if not path.rsplit("/", 1)[-1].startswith(".")
    ]
    shown = visible[:10]

    message += "\n  available files:\n" + "\n".join(
        f"    {path}" for path in shown
    )

    if len(visible) > len(shown):
        message += f"\n    ... and {len(visible) - len(shown)} more"

    return message
