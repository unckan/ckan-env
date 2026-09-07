"""Safe, read-only access to explicitly configured server log files."""

from __future__ import annotations

import glob
import os
from pathlib import Path

from ckan.plugins import toolkit


DEFAULT_LOG_PATTERNS = "/var/log/supervisor/*.log"
MAX_LINES = 2000
MAX_BYTES = 512 * 1024


def configured_sources() -> dict[str, Path]:
    """Return existing regular files from the configured allowlist.

    Globs are expanded once per request. The source id is the absolute path, but
    it can only be selected if it appears in this allowlist.
    """
    value = toolkit.config.get(
        "ckanext.unckan.server_terminal.log_paths", DEFAULT_LOG_PATTERNS
    )
    patterns = [item.strip() for item in value.replace("\n", ",").split(",")]
    paths: dict[str, Path] = {}
    for pattern in filter(None, patterns):
        for match in sorted(glob.glob(os.path.expandvars(pattern))):
            path = Path(match).resolve()
            if path.is_file():
                paths[str(path)] = path
    return paths


def read_tail(path: Path, line_count: int = 500) -> str:
    """Read a bounded tail without loading a potentially huge log into RAM."""
    try:
        line_count = int(line_count)
    except (TypeError, ValueError):
        line_count = 500
    line_count = max(1, min(line_count, MAX_LINES))
    with path.open("rb") as stream:
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(max(0, size - MAX_BYTES))
        data = stream.read(MAX_BYTES)
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    return "\n".join(lines[-line_count:])


def select_source(source_id: str | None = None) -> tuple[str, Path]:
    sources = configured_sources()
    if not sources:
        raise FileNotFoundError("No hay archivos de log disponibles")
    if source_id:
        path = sources.get(source_id)
        if path is None:
            raise ValueError("La fuente de log solicitada no está permitida")
        return source_id, path
    return next(iter(sources.items()))
