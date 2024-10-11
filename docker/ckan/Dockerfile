FROM debian:stable-slim

# Args
ARG TZ
ARG CKAN_GIT_URL
ARG CKAN_GIT_BRANCH

# Internals, you probably don't need to change these
ENV APP_DIR=/app/unckan
ENV CKAN_INI=${APP_DIR}/ckan.ini

WORKDIR ${APP_DIR}
# RUN mkdir -p ${APP_DIR}

COPY files ${APP_DIR}/files

# Create the ckan user
RUN useradd -m -s /bin/bash ckan

RUN chown ckan -R ${APP_DIR}

EXPOSE 5000

HEALTHCHECK --interval=60s --timeout=5s --retries=5 CMD curl --fail http://localhost:5000/api/3/action/status_show || exit 1

EXPOSE 5000 2222

ENTRYPOINT [ "./files/scripts/entrypoint.sh" ]
