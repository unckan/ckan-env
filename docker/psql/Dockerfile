ARG PG_IMAGE=15-alpine
FROM postgres:$PG_IMAGE
LABEL maintainer="CKAN Tech team"
# from https://github.com/ckan/ckan-postgres-dev

# Postgres settings
ENV POSTGRES_PASSWORD="pass"

# Keep the standard data path used by the Compose volume.
ENV PGDATA="/var/lib/postgresql/data"

# CKAN settings
ENV CKAN_POSTGRES_DB="ckan_test"
ENV CKAN_POSTGRES_USER="ckan_default"
ENV CKAN_POSTGRES_USER_PWD="pass"

ENV CKAN_DATASTORE_POSTGRES_DB="datastore_test"
ENV CKAN_DATASTORE_POSTGRES_READ_USER="datastore_read"
ENV CKAN_DATASTORE_POSTGRES_READ_PWD="pass"
ENV CKAN_DATASTORE_POSTGRES_WRITE_USER="datastore_write"
ENV CKAN_DATASTORE_POSTGRES_WRITE_PWD="pass"

ARG CKAN_VERSION="2.12"
ENV CKAN_VERSION=${CKAN_VERSION}

ADD docker-entrypoint-initdb.d /docker-entrypoint-initdb.d
