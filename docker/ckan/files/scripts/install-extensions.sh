#!/bin/bash -e

# load env vars from ${APP_DIR}/.env
set -o allexport
. ${APP_DIR}/.env
set +o allexport

echo "Installing Extensions"

source ${APP_DIR}/venv/bin/activate

# Create temp directory
TEMP_DIR="${APP_DIR}/tmp"
mkdir -p "$TEMP_DIR"

# Helper function to install extension from git
install_extension() {
    local repo_url=$1
    local branch=$2
    local ext_name=$3
    
    echo "Installing $ext_name extension"
    local ext_dir="$TEMP_DIR/$ext_name"
    git clone --depth 1 --branch "$branch" "$repo_url" "$ext_dir"
    cd "$ext_dir"
    pip install .
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    cd -
}

# Si estamos en el entorno de desarrollo ya esta montada la carpeta de la extension unckan
# Para produccion hay que instalarlo desde el repositorio principal
if [ "$IS_DEV_ENV" != "true" ] ; then
    echo "Installing unckan extension"
    # En este caso, el archivo pyproject.toml esta en una subcarpeta del repo, en
    # https://github.com/unckan/ckan-env/tree/start_extension/ckanext-unckan
    git clone https://github.com/unckan/ckan-env.git
    cd ckan-env/ckanext-unckan
    # Ir al tag CKAN_UNI_VERSION
    git checkout tags/${CKAN_UNI_VERSION}
    pip install .
    # Instalar sus requerimientos
    pip install -r requirements.txt
    cd ../..
fi

# PDF view https://github.com/ckan/ckanext-pdfview
pip install git+https://github.com/ckan/ckanext-pdfview.git#egg=ckanext-pdfview

install_extension "https://github.com/okfn/datapusher-plus.git" "okfn_tmp" "datapusher-plus"
install_extension "https://github.com/NorwegianRefugeeCouncil/ckanext-api-tracking.git" "0.5.2" "ckanext-api-tracking"
install_extension "https://github.com/unckan/ckanext-superset.git" "0.2.1" "ckanext-superset"
install_extension "https://github.com/okfn/ckanext-announcements.git" "0.1.6" "ckanext-announcements"
install_extension "https://github.com/unckan/ckanext-push-errors.git" "0.1.6" "ckanext-push-errors"
install_extension "https://github.com/unckan/ckanext-dbquery.git" "0.2.3" "ckanext-dbquery"
install_extension "https://github.com/DataShades/ckanext-selfinfo.git" "v1.2.0" "ckanext-selfinfo"
install_extension "https://github.com/unckan/ckanext-citeproc.git" "v1.0.1" "ckanext-citeproc"
install_extension "https://github.com/DataShades/ckanext-charts.git" "v1.9.1" "ckanext-charts"

# Clean up temp directory
rm -rf "$TEMP_DIR"

echo "CKAN extensions installed"
