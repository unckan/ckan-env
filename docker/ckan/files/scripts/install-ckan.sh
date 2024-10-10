#!/bin/bash -e

# load env vars from ${APP_DIR}/.env
echo "Export envs"
set -o allexport
. ${APP_DIR}/.env
set +o allexport

echo "Setup python env for python ver $(python3 --version)"
python3 -m venv ${APP_DIR}/venv
source ${APP_DIR}/venv/bin/activate

echo "Creating CKAN storage directory: $CKAN_STORAGE_PATH"
mkdir -p ${APP_DIR}/${CKAN_STORAGE_PATH}

echo "------ Checking out upstream CKAN: $GIT_BRANCH ------"
cd ${SRC_DIR}
git clone -b "$GIT_BRANCH" https://github.com/ckan/ckan.git ckan
cd ckan

echo "------ Installing requirements ------"
pip install -r requirements.txt

if [ "$ENV_NAME" = "dev" ]; then
  echo "------ Installing dev requirements ------"
  pip install -r dev-requirements.txt
  pip install flask-debugtoolbar
fi

echo "------ Patch CKAN if required ------"
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

echo "------ Installing CKAN ------"
pip install .
