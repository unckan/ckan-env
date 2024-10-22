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
    # En este caso, el archivo pyproject.toml esta en una subcarpeta del repo, en
    # https://github.com/unckan/ckan-env/tree/start_extension/ckanext-unckan
    pip install git+https://github.com/unckan/ckan-env/tree/develop/ckanext-unckan.git#egg=ckanext-unckan
    # Instalar sus requerimientos
    pip install -r https://raw.githubusercontent.com/unckan/ckan-env/refs/heads/develop/ckanext-unckan/requirements.txt
fi

# PDF view https://github.com/ckan/ckanext-pdfview
pip install git+https://github.com/ckan/ckanext-pdfview.git#egg=ckanext-pdfview

echo "CKAN extensions installed"
