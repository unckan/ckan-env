#!/bin/bash -e

# load env vars from ${APP_DIR}/.env
set -o allexport
. ${APP_DIR}/.env
set +o allexport

echo "Setting up configuration file for $ENV_NAME environment"

cd $APP_DIR

ckan config-tool ckan.ini "SECRET_KEY=${SECRET_KEY}"
ckan config-tool ckan.ini "beaker.session.secret=${BEAKER_SESSION_SECRET}"
ckan config-tool ckan.ini "beaker.session.validate_key = ${BEAKER_SESSION_VALIDATE_KEY}"

# debug
ckan config-tool ckan.ini "debug = ${CKAN_DEBUG}"

ckan config-tool ckan.ini "ckan.site_url = ${CKAN_SITE_URL}"
ckan config-tool ckan.ini "ckan.storage_path = $APP_DIR/${CKAN_STORAGE_FOLDER}"

# Example: postgresql://<user>:<pass>@<name>.postgres.database.azure.com/ckan?sslmode=require
ckan config-tool ckan.ini "sqlalchemy.url = ${SQLALCHEMY_URL}"
# Example: https://<name>.azurewebsites.net/solr/ckan
ckan config-tool ckan.ini "solr_url = ${SOLR_URL}"
# Example: 'rediss://default:<pass>@<name>.redis.cache.windows.net:6380'
ckan config-tool ckan.ini "ckan.redis.url = ${CKAN_REDIS_URL}"

# Example: postgresql://<user>:<pass>@<name>.postgres.database.azure.com/datastore_default?sslmode=require
# ckan config-tool ckan.ini "ckan.datastore.write_url = ${DATASTORE_WRITE_URL}"
# ckan config-tool ckan.ini "ckan.datastore.read_url = ${DATASTORE_READ_URL}"

# It look like the local auth app is different from the dev env app
if [ "$ENV_NAME" = "local" ] ; then
    # Increase vervosity for local environment
    ckan config-tool ckan.ini -s logger_ckan "level = INFO"
    ckan config-tool ckan.ini -s logger_ckanext "level = DEBUG"
else
    ckan config-tool ckan.ini -s logger_ckan "level = INFO"
    ckan config-tool ckan.ini -s logger_ckanext "level = INFO"
fi

echo "Configuration file setup complete"
