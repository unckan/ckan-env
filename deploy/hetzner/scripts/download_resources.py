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


def log(msg: str) -> None:
    print(msg, flush=True)


def main(api_key: str) -> int:
    dump = pathlib.Path("datasets.jsonl")
    if not dump.exists():
        log(f"ERROR: no existe {dump} en {pathlib.Path.cwd()}")
        return 1

    tmp = pathlib.Path("resources-tmp")
    tmp.mkdir(exist_ok=True)

    # Primera pasada: juntar todos los uploads (rid, url, dataset_name).
    # Así tenemos un total conocido para el contador.
    uploads: list[tuple[str, str, str]] = []
    non_upload_count = 0
    with dump.open() as f:
        for line in f:
            dataset = json.loads(line)
            dname = dataset.get("name", "?")
            for resource in dataset.get("resources", []):
                rid = resource.get("id")
                url = resource.get("url")
                if not rid or not url or not is_upload(url):
                    non_upload_count += 1
                    continue
                uploads.append((rid, url, dname))

    total = len(uploads)
    log(f"   {total} uploads a bajar ({non_upload_count} links externos se saltean)")

    downloaded = cached = failed = 0
    manifest: list[str] = []

    for idx, (rid, url, dname) in enumerate(uploads, start=1):
        dest = tmp / rid
        prefix = f"   [{idx}/{total}]"

        if dest.exists() and dest.stat().st_size > 0:
            cached += 1
            manifest.append(rid)
            log(f"{prefix} cache  {rid}  ({dname})")
            continue

        request = urllib.request.Request(url, headers={"Authorization": api_key})
        try:
            with urllib.request.urlopen(request, timeout=120) as response, dest.open("wb") as out:
                shutil.copyfileobj(response, out)
            size = dest.stat().st_size
            downloaded += 1
            manifest.append(rid)
            log(f"{prefix} ok     {rid}  {size/1024:.1f} KB  ({dname})")
        except (urllib.error.URLError, OSError) as exc:
            failed += 1
            log(f"{prefix} FAIL   {rid}  ({dname}): {exc}")
            if dest.exists():
                dest.unlink()

    pathlib.Path("resources-manifest.txt").write_text("\n".join(manifest))
    log(
        f"   resumen: total={total}  descargados={downloaded}  "
        f"cache={cached}  fallos={failed}"
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: download_resources.py <prod-api-key>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
