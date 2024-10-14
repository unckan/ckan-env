#!/bin/bash -e

# load env vars from ${APP_DIR}/.env
set -o allexport
. ${APP_DIR}/.env
set +o allexport

echo "Executing entrypoint.sh ($IS_DEV_ENV)"

if [ "$IS_DEV_ENV" = "true" ] ; then
    # If we are in the local environment, install the local extensions
    PREPARE_SCRIPT=$APP_DIR/files/scripts/prepare-local-dev-extensions.sh
    $PREPARE_SCRIPT
fi

# The CKAN PostgreSQL image creates the database and user
# https://github.com/ckan/ckan-postgres-dev/blob/main/Dockerfile
# Wait for the database to be ready

until psql -d $SQLALCHEMY_URL -c '\q'; do
  echo "Postgres is unavailable - sleeping. Response: $?"
  sleep 3
done

echo "Postgres is up, continue"

source ${APP_DIR}/venv/bin/activate

echo "CKAN DB init"
ckan db init

# Rebuild search index
ckan search-index rebuild

# Datapusher+ requires a valid API token to operate
echo "Creating a valid API token for Datapusher+"
DATAPUSHER_TOKEN=$(ckan user token add default datapusher_multi expires_in=365 unit=86400 | tail -n 1 | tr -d '\t')
ckan config-tool ckan.ini "ckan.datapusher.api_token=${DATAPUSHER_TOKEN}"
ckan config-tool ckan.ini "ckanext.datapusher_plus.api_token=${DATAPUSHER_TOKEN}"

# Rebuild webassets in can they were patched
ckan asset build

# Start supervidor
echo "Supervisor start"
supervisorctl start
echo "Updating supervisor"
supervisorctl reread
supervisorctl update

# Start the development server as the ckan user with automatic reload
echo "Starting CKAN gunicorn"
if [ "$IS_DEV_ENV" = "true" ] ; then
    supervisorctl start ckan-dev
else
    supervisorctl start ckan
    # $GUNICORN -w 4 -b 0.0.0.0:5000 --chdir $APP_DIR wsgi:application --timeout 360
fi

echo "Finished entrypoint.sh"
