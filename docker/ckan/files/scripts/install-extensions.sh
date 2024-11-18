#!/bin/bash -e

# load env vars from ${APP_DIR}/.env
set -o allexport
. ${APP_DIR}/.env
set +o allexport

echo "Installing Extensions"

python -m venv ${APP_DIR}/venv
source ${APP_DIR}/venv/bin/activate

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

echo "Installing Datapusher+extension"
pip install -e  git+https://github.com/okfn/datapusher-plus.git@okfn_tmp#egg=datapusher_plus
pip install -r https://raw.githubusercontent.com/okfn/datapusher-plus/okfn_tmp/requirements.txt

echo "Installing API-tracking extension"
pip install -e git+https://github.com/NorwegianRefugeeCouncil/ckanext-api-tracking.git@0.4.1#egg=ckanext-api-tracking
pip install -r https://raw.githubusercontent.com/NorwegianRefugeeCouncil/ckanext-api-tracking/refs/tags/0.4.1/requirements.txt

echo "Installing Apache Superset extension"
pip install -e git+https://github.com/unckan/ckanext-superset.git@0.1.2#egg=ckanext-superset
pip install -r https://raw.githubusercontent.com/unckan/ckanext-superset/refs/tags/0.1.2/requirements.txt

echo "CKAN extensions installed"
