#!/usr/bin/env python3
"""
sync_config.py — Copia la config del portal (/ckan-admin/config) de prod a local.

Usa las actions ``config_option_list`` / ``config_option_show`` /
``config_option_update`` de la API de CKAN para leer todas las opciones
editables por admin en prod y escribirlas en local.

También baja el logo del sitio (``ckan.site_logo``) si es un upload, y
escribe ``admin-manifest.txt`` con el filename para que el bash lo copie
al storage del container.

Requiere API keys de sysadmin en ambos lados.

Uso:
    ./sync_config.py <prod-url> <prod-key> <local-url> <local-key>
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sys
import urllib.error
import urllib.request


# Keys que NO se copian de prod porque son específicas del deployment local.
# Copiarlas rompe auth, redirects, cookies, notificaciones o integraciones.
EXCLUDED_KEYS = frozenset(
    {
        # Dominio — rompe login, redirects y cookies si se copia
        "ckan.site_url",
        "ckan.site_id",
        # Reglas de creación de usuarios: suelen ser distintas en dev
        "ckan.auth.create_user_via_api",
        "ckan.auth.create_user_via_web",
        "ckan.auth.user_create_organizations",
        "ckan.auth.user_create_groups",
        # SMTP es propio del server, no del contenido
        "smtp.server",
        "smtp.starttls",
        "smtp.user",
        "smtp.password",
        "smtp.mail_from",
        # Tokens específicos del server (ej. XLoader)
        "ckan.xloader.api_token",
        "ckanext.xloader.api_token",
    }
)


def log(msg: str) -> None:
    print(msg, flush=True)


def call_action(base_url: str, api_key: str, action: str, **data) -> object:
    """Llama una action de la API de CKAN y devuelve el ``result``."""
    url = f"{base_url.rstrip('/')}/api/3/action/{action}"
    body = json.dumps(data).encode() if data else b""
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read())
    if not payload.get("success"):
        raise RuntimeError(f"{action} falló: {payload.get('error')}")
    return payload["result"]


def download_logo(prod_url: str, api_key: str, filename: str) -> pathlib.Path | None:
    """Baja el logo del sitio a ``admin-tmp/<filename>`` si es un upload."""
    if filename.startswith(("http://", "https://")):
        log(f"   logo es URL externa, no se baja: {filename}")
        return None

    tmp = pathlib.Path("admin-tmp")
    tmp.mkdir(exist_ok=True)
    dest = tmp / filename

    if dest.exists() and dest.stat().st_size > 0:
        log(f"   cache  {filename}  ({dest.stat().st_size/1024:.1f} KB)")
        return dest

    url = f"{prod_url.rstrip('/')}/uploads/admin/{filename}"
    request = urllib.request.Request(url, headers={"Authorization": api_key})
    try:
        with urllib.request.urlopen(request, timeout=60) as response, dest.open("wb") as out:
            shutil.copyfileobj(response, out)
        log(f"   ok     {filename}  ({dest.stat().st_size/1024:.1f} KB)")
        return dest
    except (urllib.error.URLError, OSError) as exc:
        log(f"   FAIL   {filename}: {exc}")
        if dest.exists():
            dest.unlink()
        return None


def main(prod_url: str, prod_key: str, local_url: str, local_key: str) -> int:
    log(">> leyendo config del portal desde prod")
    all_keys = call_action(prod_url, prod_key, "config_option_list")
    keys = [k for k in all_keys if k not in EXCLUDED_KEYS]
    total = len(keys)
    excluded_count = len(all_keys) - total
    log(f"   {total} opciones a copiar ({excluded_count} excluidas por blacklist)")

    config: dict[str, object] = {}
    for idx, key in enumerate(keys, start=1):
        value = call_action(prod_url, prod_key, "config_option_show", key=key)
        config[key] = value
        shown = repr(value)
        if len(shown) > 70:
            shown = shown[:67] + "..."
        log(f"   [{idx}/{total}] read  {key} = {shown}")

    log(">> escribiendo config en local")
    call_action(local_url, local_key, "config_option_update", **config)
    log(f"   {len(config)} opciones actualizadas")

    logo = (config.get("ckan.site_logo") or "") if isinstance(config.get("ckan.site_logo"), str) else ""
    manifest = pathlib.Path("admin-manifest.txt")
    if logo:
        log(f">> bajando logo del sitio: {logo}")
        result = download_logo(prod_url, prod_key, logo)
        if result is not None:
            manifest.write_text(logo)
        else:
            manifest.write_text("")
    else:
        manifest.write_text("")
        log("   no hay logo para bajar")

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Uso: sync_config.py <prod-url> <prod-key> <local-url> <local-key>",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
