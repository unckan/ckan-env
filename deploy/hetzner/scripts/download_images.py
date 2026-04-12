#!/usr/bin/env python3
"""
download_images.py — Descarga imágenes de grupos y organizaciones de CKAN.

CKAN guarda las imágenes de grupos y orgs en
``{storage_path}/storage/group/<filename>`` y las sirve como
``{site_url}/uploads/group/<filename>``. El campo ``image_url`` del JSON
de la entidad contiene el filename (cuando es un upload) o una URL externa
completa (cuando el admin la setea manualmente).

Lee ``organizations.jsonl`` y ``groups.jsonl`` del directorio actual,
descarga solo las imágenes que son uploads (no URLs externas) desde el
servidor de producción, las deja en ``images-tmp/<filename>`` y escribe
``images-manifest.txt`` con los filenames descargados para que el bash
los copie al volumen del container.

Idempotente: si el archivo ya existe en ``images-tmp/`` con tamaño > 0, no
lo baja de nuevo.

Uso:
    ./download_images.py <prod-url> <prod-api-key>
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request


INPUT_FILES = ("organizations.jsonl", "groups.jsonl")


def is_external_url(image_url: str) -> bool:
    """``image_url`` puede ser un filename (upload) o una URL externa."""
    parsed = urllib.parse.urlparse(image_url)
    return bool(parsed.scheme and parsed.netloc)


def log(msg: str) -> None:
    print(msg, flush=True)


def main(prod_url: str, api_key: str) -> int:
    prod_url = prod_url.rstrip("/")
    tmp = pathlib.Path("images-tmp")
    tmp.mkdir(exist_ok=True)

    # Primera pasada: colectar todas las imágenes a bajar.
    images: list[tuple[str, str]] = []  # (filename, entity_name)
    skipped_no_image = 0
    skipped_external = 0

    for filename in INPUT_FILES:
        path = pathlib.Path(filename)
        if not path.exists():
            log(f"   [warn] no existe {filename}, se saltea")
            continue

        with path.open() as f:
            for line in f:
                entity = json.loads(line)
                ename = entity.get("name", "?")
                image = entity.get("image_url") or ""

                if not image:
                    skipped_no_image += 1
                    continue
                if is_external_url(image):
                    skipped_external += 1
                    continue
                images.append((image, ename))

    total = len(images)
    log(
        f"   {total} imágenes a bajar  "
        f"(sin imagen: {skipped_no_image}, externas: {skipped_external})"
    )

    downloaded = cached = failed = 0
    manifest: list[str] = []

    for idx, (image, ename) in enumerate(images, start=1):
        dest = tmp / image
        prefix = f"   [{idx}/{total}]"

        if dest.exists() and dest.stat().st_size > 0:
            cached += 1
            manifest.append(image)
            log(f"{prefix} cache  {image}  ({ename})")
            continue

        url = f"{prod_url}/uploads/group/{image}"
        request = urllib.request.Request(url, headers={"Authorization": api_key})
        try:
            with urllib.request.urlopen(request, timeout=60) as response, dest.open("wb") as out:
                shutil.copyfileobj(response, out)
            size = dest.stat().st_size
            downloaded += 1
            manifest.append(image)
            log(f"{prefix} ok     {image}  {size/1024:.1f} KB  ({ename})")
        except (urllib.error.URLError, OSError) as exc:
            failed += 1
            log(f"{prefix} FAIL   {image}  ({ename}): {exc}")
            if dest.exists():
                dest.unlink()

    pathlib.Path("images-manifest.txt").write_text("\n".join(manifest))
    log(
        f"   resumen: total={total}  descargadas={downloaded}  "
        f"cache={cached}  fallos={failed}"
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: download_images.py <prod-url> <prod-api-key>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
