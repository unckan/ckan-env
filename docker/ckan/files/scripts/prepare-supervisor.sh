set -o allexport
. ${APP_DIR}/.env
set +o allexport

# Define the "ckan" user as the owner of supervisor processes
envsubst < $APP_DIR/files/etc/supervisord.conf > /etc/supervisor/supervisord.conf
echo "Supervisor configuration"
cat /etc/supervisor/supervisord.conf

# Override the files/etc/ckan-worker.conf file with env vars
envsubst < $APP_DIR/files/etc/ckan-worker.conf > /etc/supervisor/conf.d/ckan-worker.conf
echo "CKAN worker configuration"
cat /etc/supervisor/conf.d/ckan-worker.conf

# Prepaer the ckan supervisor command
if [ "$IS_DEV_ENV" = "true" ] ; then
    CMD="$APP_DIR/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 --chdir $APP_DIR --certfile=$APP_DIR/files/cert/localhost.cert --keyfile=$APP_DIR/files/cert/localhost.key --reload wsgi:application"
else
    CMD="$APP_DIR/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 --chdir $APP_DIR wsgi:application --timeout 360"
fi

envsubst < $APP_DIR/files/etc/ckan.conf > /etc/supervisor/conf.d/ckan.conf
echo "CKAN configuration"
cat /etc/supervisor/conf.d/ckan.conf
