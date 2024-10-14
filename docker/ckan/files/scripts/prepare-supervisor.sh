set -o allexport
. ${APP_DIR}/.env
set +o allexport

# Override the files/etc/ckan-worker.conf file with env vars
envsubst < $APP_DIR/files/etc/ckan-worker.conf > /etc/supervisor/conf.d/ckan-worker.conf
envsubst < $APP_DIR/files/etc/ckan-dev.conf > /etc/supervisor/conf.d/ckan-dev.conf
# envsubst < $APP_DIR/files/etc/ckan.conf > /etc/supervisor/conf.d/ckan.conf
