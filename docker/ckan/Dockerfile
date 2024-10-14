FROM debian:stable-slim

# Args
ARG TZ
ARG ENV_NAME

# Internals, you probably don't need to change these
ENV APP_DIR=/app/unckan
ENV CKAN_INI=${APP_DIR}/ckan.ini

WORKDIR ${APP_DIR}
RUN apt update

COPY files ${APP_DIR}/files

# Prepare the environment vars
RUN ${APP_DIR}/files/scripts/build-env-vars.sh

# Install OS dependencies
RUN ${APP_DIR}/files/scripts/install-python.sh
RUN ${APP_DIR}/files/scripts/install-os-deps.sh

# Create the ckan user
RUN useradd -m -s /bin/bash ckan
RUN chown ckan -R ${APP_DIR}
USER ckan

# Install CKAN
RUN ${APP_DIR}/files/scripts/install-ckan.sh

COPY files/scripts/entrypoint.sh ${APP_DIR}/entrypoint.sh 

HEALTHCHECK --interval=60s --timeout=5s --retries=5 CMD curl --fail http://localhost:5000/api/3/action/status_show || exit 1
EXPOSE 5000

ENTRYPOINT [ "./entrypoint.sh" ]