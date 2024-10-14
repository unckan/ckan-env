FROM debian:stable-slim

# Args
ARG TZ
ARG ENV_NAME

# Internals, you probably don't need to change these
ENV APP_DIR=/app/unckan
ENV CKAN_INI=${APP_DIR}/ckan.ini

WORKDIR ${APP_DIR}
RUN apt update

# Copy files one by one to ensure Dockerfile is caching layers
# and the change in one file does not invalidate the cache of the others

# Prepare the environment vars
COPY files/scripts/build-env-vars.sh ${APP_DIR}/files/scripts/build-env-vars.sh

COPY files/env/base.env ${APP_DIR}/files/env/base.env
COPY files/env/${ENV_NAME}.env ${APP_DIR}/files/env/${ENV_NAME}.env
RUN ${APP_DIR}/files/scripts/build-env-vars.sh

# Install OS dependencies
COPY files/scripts/install-python.sh ${APP_DIR}/files/scripts/install-python.sh
RUN ${APP_DIR}/files/scripts/install-python.sh

COPY files/scripts/install-os-deps.sh ${APP_DIR}/files/scripts/install-os-deps.sh
RUN ${APP_DIR}/files/scripts/install-os-deps.sh

COPY files/etc/supervisord.base ${APP_DIR}/files/etc/supervisord.conf
COPY files/etc/ckan*.conf ${APP_DIR}/files/etc/
COPY files/scripts/prepare-supervisor.sh ${APP_DIR}/files/scripts/prepare-supervisor.sh
RUN ${APP_DIR}/files/scripts/prepare-supervisor.sh

# Copy all pending files
COPY files/scripts/prepare-local-dev-extensions.sh ${APP_DIR}/files/scripts/prepare-local-dev-extensions.sh
COPY files/cert/localhost.cert ${APP_DIR}/files/cert/localhost.cert
COPY files/cert/localhost.key ${APP_DIR}/files/cert/localhost.key

COPY files/patches ${APP_DIR}/files/patches
COPY files/ckan.ini ${CKAN_INI}
COPY files/scripts/install-ckan.sh ${APP_DIR}/files/scripts/install-ckan.sh
COPY files/scripts/setup-ckan-ini-file.sh ${APP_DIR}/files/scripts/setup-ckan-ini-file.sh
COPY files/scripts/entrypoint.sh ${APP_DIR}/entrypoint.sh 

# Create the ckan user
RUN useradd -m -s /bin/bash ckan
RUN chown ckan -R ${APP_DIR}
USER ckan

# Install CKAN
RUN ${APP_DIR}/files/scripts/install-ckan.sh
RUN ${APP_DIR}/files/scripts/setup-ckan-ini-file.sh

HEALTHCHECK --interval=60s --timeout=5s --retries=5 CMD curl --fail http://localhost:5000/api/3/action/status_show || exit 1
EXPOSE 5000

ENTRYPOINT [ "./entrypoint.sh" ]