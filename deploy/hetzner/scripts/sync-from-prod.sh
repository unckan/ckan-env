#!/usr/bin/env bash
#
# sync-from-prod.sh — Trae todos los datos de una instancia CKAN de producción
# hacia esta instancia local (Hetzner), de forma idempotente.
#
# Usa `ckanapi` para dump/load de entidades core (organizations, groups,
# users, datasets) y un paso final opcional que copia los archivos binarios
# de los resources al volumen de storage del container.
#
# Requisitos:
#   - ckanapi instalado en el host (uv venv && uv pip install ckanapi)
#   - El container ckan_uni corriendo (docker compose up -d)
#   - API key de sysadmin en prod y en local
#
# Uso:
#   PROD_URL=https://ckan-prod.example.org \
#   PROD_KEY=xxxxxxxx \
#   LOCAL_KEY=yyyyyyyy \
#   ./sync-from-prod.sh
#
# Variables opcionales:
#   LOCAL_URL     URL del CKAN local (default http://127.0.0.1:5000)
#   DUMP_DIR      carpeta para los JSONL y files (default ./sync-dump)
#   COPY_FILES    si es "1" copia los archivos de resources al storage del
#                 container via docker cp (default "1")
#   CONTAINER     nombre del container CKAN local (default ckan_uni)
#   STORAGE_PATH  path del storage dentro del container (default /app/unckan/storage)
#
# Idempotencia:
#   - `ckanapi load` hace upsert (create o update) por ID/nombre — se puede
#     correr múltiples veces sin duplicar.
#   - Los archivos de resources se saltean si ya existen en storage.
#   - Los JSONL se sobreescriben en cada corrida (siempre refrescan el dump).

set -euo pipefail

# --- Validación de variables requeridas -------------------------------------

: "${PROD_URL:?falta PROD_URL (ej. https://ckan-prod.example.org)}"
: "${PROD_KEY:?falta PROD_KEY (API key de sysadmin en prod)}"
: "${LOCAL_KEY:?falta LOCAL_KEY (API key de sysadmin en local)}"

LOCAL_URL="${LOCAL_URL:-http://127.0.0.1:5000}"
DUMP_DIR="${DUMP_DIR:-./sync-dump}"
COPY_FILES="${COPY_FILES:-1}"
CONTAINER="${CONTAINER:-ckan_uni}"
STORAGE_PATH="${STORAGE_PATH:-/app/unckan/storage}"

# Ruta al .py que baja los files. Se resuelve desde la ubicación del bash
# script (no desde el cwd, que después cambiamos a DUMP_DIR).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOWNLOAD_PY="${SCRIPT_DIR}/download_resources.py"
DOWNLOAD_IMAGES_PY="${SCRIPT_DIR}/download_images.py"
SYNC_CONFIG_PY="${SCRIPT_DIR}/sync_config.py"

# --- Sanity checks -----------------------------------------------------------

if ! command -v ckanapi >/dev/null 2>&1; then
    echo "ERROR: ckanapi no está instalado."
    echo "Instalalo con:   pipx install ckanapi   (o: pip install --user ckanapi)"
    exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "ERROR: el container '${CONTAINER}' no está corriendo."
    echo "Levantalo con: docker compose -f docker-compose.prod.yml up -d"
    exit 1
fi

mkdir -p "$DUMP_DIR"
cd "$DUMP_DIR"

echo "=============================================================="
echo " Sync CKAN  (PROD -> LOCAL)"
echo "   PROD_URL=$PROD_URL"
echo "   LOCAL_URL=$LOCAL_URL"
echo "   DUMP_DIR=$DUMP_DIR"
echo "   COPY_FILES=$COPY_FILES"
echo "=============================================================="

# --- 1. Dump desde prod ------------------------------------------------------

dump_entity() {
    local entity="$1"
    local out="${entity}.jsonl"
    echo ">> dump ${entity} desde prod"
    ckanapi dump "$entity" --all \
        --remote="$PROD_URL" \
        --apikey="$PROD_KEY" \
        > "$out"
    local count
    count=$(wc -l < "$out")
    echo "   ${count} ${entity} dumpeadas a ${out}"
}

dump_entity organizations
dump_entity groups
dump_entity users
dump_entity datasets

# --- 2. Load en local --------------------------------------------------------
# Orden importante por FK: orgs -> groups -> users -> datasets

load_entity() {
    local entity="$1"
    local in="${entity}.jsonl"
    echo ">> load ${entity} en local"
    ckanapi load "$entity" \
        --remote="$LOCAL_URL" \
        --apikey="$LOCAL_KEY" \
        < "$in"
}

load_entity organizations
load_entity groups
load_entity users
load_entity datasets

# --- 3. (opcional) copiar archivos binarios de resources al storage ---------
#
# ckanapi dump datasets incluye los metadatos de cada resource pero NO el
# archivo binario. CKAN guarda los uploads en:
#   ${STORAGE_PATH}/resources/{id[0:3]}/{id[3:6]}/{id[6:]}
#
# Bajamos cada file desde prod usando la URL del resource y lo copiamos al
# volumen del container con `docker cp` (la ruta interna en el container).
#
# Saltea los resources cuyo URL no es una upload (ej. links externos).

if [ "$COPY_FILES" = "1" ]; then
    echo ">> bajando archivos binarios de resources"
    python3 "$DOWNLOAD_PY" "$PROD_KEY"

    echo ">> copiando archivos al storage del container ${CONTAINER}"
    # Por cada archivo en resources-tmp, lo copiamos al path que CKAN espera.
    #   /app/unckan/storage/resources/{id[0:3]}/{id[3:6]}/{id[6:]}
    while read -r rid; do
        [ -z "$rid" ] && continue
        src="resources-tmp/${rid}"
        [ -f "$src" ] || continue
        # verificar si ya está adentro (idempotente)
        internal_dir="${STORAGE_PATH}/resources/${rid:0:3}/${rid:3:3}"
        internal_path="${internal_dir}/${rid:6}"
        if docker exec "$CONTAINER" test -f "$internal_path" 2>/dev/null; then
            continue
        fi
        docker exec "$CONTAINER" mkdir -p "$internal_dir"
        docker cp "$src" "${CONTAINER}:${internal_path}"
    done < resources-manifest.txt

    # permisos dentro del container: CKAN corre como `ckan`
    docker exec "$CONTAINER" chown -R ckan:ckan "${STORAGE_PATH}/resources" 2>/dev/null || true
    echo "   files copiados"

    # --- 4. imágenes de grupos y organizaciones ----------------------------
    # CKAN las guarda en ${STORAGE_PATH}/storage/uploads/group/<filename> y las sirve
    # como ${SITE_URL}/uploads/group/<filename>. El campo image_url de cada
    # entidad contiene el filename (upload) o una URL externa completa.
    echo ">> bajando imágenes de grupos y organizaciones"
    python3 "$DOWNLOAD_IMAGES_PY" "$PROD_URL" "$PROD_KEY"

    echo ">> copiando imágenes al storage del container ${CONTAINER}"
    image_dir="${STORAGE_PATH}/storage/uploads/group"
    docker exec "$CONTAINER" mkdir -p "$image_dir"
    while read -r img; do
        [ -z "$img" ] && continue
        src="images-tmp/${img}"
        [ -f "$src" ] || continue
        internal_path="${image_dir}/${img}"
        if docker exec "$CONTAINER" test -f "$internal_path" 2>/dev/null; then
            continue
        fi
        docker cp "$src" "${CONTAINER}:${internal_path}"
    done < images-manifest.txt

    docker exec "$CONTAINER" chown -R ckan:ckan "$image_dir" 2>/dev/null || true
    echo "   imágenes copiadas"
fi

# --- 5. config del portal (/ckan-admin/config) + logo -----------------------
# Copia título, descripción, about, intro text, logo, etc. vía la API
# (config_option_list/show/update). El logo, si es un upload, se baja y
# copia al storage del container igual que las imágenes de grupo.
echo ">> sincronizando config del portal"
python3 "$SYNC_CONFIG_PY" "$PROD_URL" "$PROD_KEY" "$LOCAL_URL" "$LOCAL_KEY"

if [ -s admin-manifest.txt ]; then
    logo=$(cat admin-manifest.txt)
    src="admin-tmp/${logo}"
    if [ -f "$src" ]; then
        admin_dir="${STORAGE_PATH}/storage/uploads/admin"
        internal_path="${admin_dir}/${logo}"
        if ! docker exec "$CONTAINER" test -f "$internal_path" 2>/dev/null; then
            docker exec "$CONTAINER" mkdir -p "$admin_dir"
            docker cp "$src" "${CONTAINER}:${internal_path}"
            docker exec "$CONTAINER" chown -R ckan:ckan "$admin_dir" 2>/dev/null || true
            echo "   logo copiado al storage"
        else
            echo "   logo ya presente en storage"
        fi
    fi
fi

echo "=============================================================="
echo " Sync completado."
echo " Dumps en: $(pwd)"
echo
echo " NOTA: los passwords de usuarios NO se migran (no salen por API)."
echo "       Los usuarios deberán resetear password en local, o se puede"
echo "       setear manualmente:  docker exec -it ${CONTAINER} ckan user setpass <user>"
echo "=============================================================="
