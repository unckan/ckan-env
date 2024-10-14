#!/bin/bash -e

echo "Installing OS dependencies"

# =====================================================
# Install more dependencies
apt install -y git libpq-dev

# git: to pull the CKAN source code from GitHub
# libpq-dev: for PostgreSQL support in CKAN (psycopg2)
