#!/usr/bin/env python3
"""
download_resources.py — Descarga archivos binarios de resources de CKAN.

Lee ``datasets.jsonl`` del directorio actual (producido por
``ckanapi dump datasets``), filtra los resources que son uploads reales
(URL con ``/resource/{id}/download/``), y los descarga a ``resources-tmp/``
usando la API key provista.

Es idempotente: si el archivo ya existe en ``resources-tmp/<id>`` con
tamaño > 0, no lo baja de nuevo.

Al terminar, escribe ``resources-manifest.txt`` con los IDs descargados,
para que el script bash que lo invoca sepa qué copiar al storage del
container.

Uso:
    ./download_resources.py <prod-api-key>
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sys
import urllib.error
import urllib.request


def is_upload(url: str) -> bool:
    """Solo los resources subidos a CKAN tienen /resource/{id}/download/."""
    return "/resource/" in url and "/download/" in url


def main(api_key: str) -> int:
    dump = pathlib.Path("datasets.jsonl")
    if not dump.exists():
        print(f"ERROR: no existe {dump} en {pathlib.Path.cwd()}", file=sys.stderr)
        return 1

    tmp = pathlib.Path("resources-tmp")
    tmp.mkdir(exist_ok=True)

    total = downloaded = skipped = failed = 0
    manifest: list[str] = []

    with dump.open() as f:
        for line in f:
            dataset = json.loads(line)
            for resource in dataset.get("resources", []):
                total += 1
                rid = resource.get("id")
                url = resource.get("url")

                if not rid or not url or not is_upload(url):
                    skipped += 1
                    continue

                dest = tmp / rid
                if dest.exists() and dest.stat().st_size > 0:
                    manifest.append(rid)
                    continue

                request = urllib.request.Request(
                    url, headers={"Authorization": api_key}
                )
                try:
                    with urllib.request.urlopen(request, timeout=120) as response, dest.open("wb") as out:
                        shutil.copyfileobj(response, out)
                    downloaded += 1
                    manifest.append(rid)
                except (urllib.error.URLError, OSError) as exc:
                    print(f"   [skip] {rid}: {exc}", file=sys.stderr)
                    failed += 1
                    if dest.exists():
                        dest.unlink()

    pathlib.Path("resources-manifest.txt").write_text("\n".join(manifest))
    print(
        f"   total={total}  descargados={downloaded}  "
        f"salteados={skipped}  fallos={failed}"
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: download_resources.py <prod-api-key>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
