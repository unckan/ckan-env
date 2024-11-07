#!/bin/bash -e

# load env vars from ${APP_DIR}/.env
set -o allexport
. ${APP_DIR}/.env
set +o allexport

echo "Installing CKAN $CKAN_GIT_BRANCH :: $CKAN_GIT_URL :: $(python --version)"

python -m venv ${APP_DIR}/venv
source ${APP_DIR}/venv/bin/activate
pip install gunicorn

echo "Creating CKAN storage directory: $CKAN_STORAGE_FOLDER"
mkdir -p ${APP_DIR}/${CKAN_STORAGE_FOLDER}

# Create a source folder
cd ${APP_DIR}
git clone -b "$CKAN_GIT_BRANCH" $CKAN_GIT_URL ckan
cd ckan

echo "Installing requirements"
pip install -r requirements.txt

# The boolean IS_DEV_ENV define if we need to install dev requirements
if [ "$IS_DEV_ENV" = "true" ] ; then
  echo "Installing dev requirements"
  pip install -r dev-requirements.txt
  pip install flask-debugtoolbar
fi

echo "Installing CKAN package"
pip install .

echo "Patch CKAN if required"
cd ${APP_DIR}

PATCH_FOLDER=$APP_DIR/files/patches
ls -l $PATCH_FOLDER

for dir in ${PATCH_FOLDER}/*; do \
    for file in $(find "$dir"/*.patch | sort -g); do \
        abspath=$(readlink -f "$file");
        echo "$0: Applying patch $abspath";
        (cd ${APP_DIR}/ckan && git apply "$abspath" --verbose);
    done ; \
done

echo "CKAN installed"
