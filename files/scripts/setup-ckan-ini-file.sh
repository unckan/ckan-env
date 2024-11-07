#!/bin/bash -e

# load env vars from ${APP_DIR}/.env
set -o allexport
. ${APP_DIR}/.env
set +o allexport

echo "Setting up configuration file for $ENV_NAME environment"
source ${APP_DIR}/venv/bin/activate
cd $APP_DIR

# Validate required env vars
VALIDATE_VARS="SECRET_KEY BEAKER_SESSION_SECRET BEAKER_SESSION_VALIDATE_KEY CKAN_SITE_URL CKAN_STORAGE_FOLDER SQLALCHEMY_URL SOLR_URL CKAN_REDIS_URL"
for VAR in $VALIDATE_VARS; do
  if [ -z "${!VAR}" ]; then
    echo "$VAR is not set. Exiting."
    exit 1
  fi
done

ckan config-tool ${CKAN_INI} "SECRET_KEY=${SECRET_KEY}"
ckan config-tool ${CKAN_INI} "beaker.session.secret=${BEAKER_SESSION_SECRET}"
ckan config-tool ${CKAN_INI} "beaker.session.validate_key = ${BEAKER_SESSION_VALIDATE_KEY}"

# debug
ckan config-tool ${CKAN_INI} "debug = ${CKAN_DEBUG}"

ckan config-tool ${CKAN_INI} "ckan.site_url = ${CKAN_SITE_URL}"
ckan config-tool ${CKAN_INI} "ckan.storage_path = $APP_DIR/${CKAN_STORAGE_FOLDER}"

# Example: postgresql://<user>:<pass>@<name>.postgres.database.azure.com/ckan?sslmode=require
ckan config-tool ${CKAN_INI} "sqlalchemy.url = ${SQLALCHEMY_URL}"
# Example: https://<name>.azurewebsites.net/solr/ckan
ckan config-tool ${CKAN_INI} "solr_url = ${SOLR_URL}"
# Example: 'rediss://default:<pass>@<name>.redis.cache.windows.net:6380'
ckan config-tool ${CKAN_INI} "ckan.redis.url = ${CKAN_REDIS_URL}"

# Example: postgresql://<user>:<pass>@<name>.postgres.database.azure.com/datastore_default?sslmode=require
ckan config-tool ${CKAN_INI} "ckan.datastore.write_url = ${DATASTORE_WRITE_URL}"
ckan config-tool ${CKAN_INI} "ckan.datastore.read_url = ${DATASTORE_READ_URL}"

# It look like the local auth app is different from the dev env app
if [ "$IS_DEV_ENV" = "true" ] ; then
    # Increase vervosity for local environment
    ckan config-tool ckan.ini "ckanext.datapusher_plus.ssl_verify = false"
    ckan config-tool ${CKAN_INI} -s logger_ckan "level = INFO"
    ckan config-tool ${CKAN_INI} -s logger_ckanext "level = DEBUG"
else
    ckan config-tool ${CKAN_INI} -s logger_ckan "level = INFO"
    ckan config-tool ${CKAN_INI} -s logger_ckanext "level = INFO"
fi

echo "Configuration file setup complete"
