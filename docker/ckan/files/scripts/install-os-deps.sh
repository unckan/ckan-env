#!/bin/bash -e

echo "Installing OS dependencies"

# =====================================================
# Install more dependencies
apt install -y gettext-base git libmagic1 libpq-dev postgresql-client supervisor

# git: to pull the CKAN source code from GitHub
# libmagic1: for the file upload functionality in CKAN
# libpq-dev: for PostgreSQL support in CKAN (psycopg2)
# postgresql-client: for the psql command-line tool
# supervisor: to run CKAN jobs in the background
# gettext-base: for envsubst command
