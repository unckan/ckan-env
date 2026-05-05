#!/bin/bash -e

echo "Installing OS dependencies"

# =====================================================
# Install more dependencies
apt update
apt install -y gettext-base file git libmagic1 libpq-dev libuchardet-dev postgresql-client \
    supervisor uchardet unzip vim wget xmlsec1 \
    texlive-latex-extra latexmk curl

# git: to pull the CKAN source code from GitHub
# libmagic1: for the file upload functionality in CKAN
# libpq-dev: for PostgreSQL support in CKAN (psycopg2)
# postgresql-client: for the psql command-line tool
# supervisor: to run CKAN jobs in the background
# gettext-base: for envsubst command
