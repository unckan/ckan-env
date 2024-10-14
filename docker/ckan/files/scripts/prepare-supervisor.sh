set -o allexport
. ${APP_DIR}/.env
set +o allexport

# Define the "ckan" user as the owner of supervisor processes
envsubst < $APP_DIR/files/etc/supervisord.conf > /etc/supervisor/supervisord.conf

# Override the files/etc/ckan-worker.conf file with env vars
envsubst < $APP_DIR/files/etc/ckan-worker.conf > /etc/supervisor/conf.d/ckan-worker.conf
envsubst < $APP_DIR/files/etc/ckan-dev.conf > /etc/supervisor/conf.d/ckan-dev.conf
# envsubst < $APP_DIR/files/etc/ckan.conf > /etc/supervisor/conf.d/ckan.conf
