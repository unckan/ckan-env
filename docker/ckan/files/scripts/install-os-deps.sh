#!/bin/bash -e

echo "Installing OS dependencies"

# =====================================================
# Install more dependencies
apt install -y git libpq-dev postgresql-client

# git: to pull the CKAN source code from GitHub
# libpq-dev: for PostgreSQL support in CKAN (psycopg2)
# postgresql-client: for the psql command-line tool
