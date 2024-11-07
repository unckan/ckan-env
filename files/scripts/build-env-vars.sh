#!/bin/bash
# Use files/env/base.env as base environment variables and then apply
# the current ENV_NAME to override the base variables.

if [ -z "$ENV_NAME" ]; then
  echo "ENV_NAME is not set. Exiting."
  exit 1
fi

echo "Building UNCKAN for ${ENV_NAME} env"

cat ${APP_DIR}/files/env/base.env > ${APP_DIR}/.env
# if the ${APP_DIR}/files/env/${ENV_NAME}.env file exists, append it
# to the .env file
if [ ! -f ${APP_DIR}/files/env/${ENV_NAME}.env ]; then
  echo "No env file found for ${ENV_NAME}! Continue"
else
    # ensure a newline at the end of the file
    echo "" >> ${APP_DIR}/.env
    cat ${APP_DIR}/files/env/${ENV_NAME}.env >> ${APP_DIR}/.env
fi

# Load env vars from ${APP_DIR}/.env to test them
set -o allexport
. ${APP_DIR}/.env
set +o allexport

# Validate basic env vars
VALIDATE_VARS="CKAN_GIT_URL CKAN_GIT_BRANCH"
for VAR in $VALIDATE_VARS; do
  if [ -z "${!VAR}" ]; then
    echo "$VAR is not set. Exiting."
    exit 1
  fi
done
