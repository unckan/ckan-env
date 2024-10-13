#!/bin/bash -e

echo "Installing OS dependencies"

# load env vars from ${APP_DIR}/.env
set -o allexport
. ${APP_DIR}/.env
set +o allexport

apt update

# Install Python according to PY_VERSION
apt install -y software-properties-common wget gnupg

# Add deadsnakes PPA manually
wget -qO - https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x6A755776 | gpg --dearmor -o /usr/share/keyrings/deadsnakes-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/deadsnakes-archive-keyring.gpg] http://ppa.launchpad.net/deadsnakes/ppa/ubuntu focal main" > /etc/apt/sources.list.d/deadsnakes-ppa.list
apt install -y python${PY_VERSION} python${PY_VERSION}-dev python3-pip python3-venv

# Define python alias for the version installed
ln -s /usr/bin/python${PY_VERSION} /usr/bin/python

echo "Python installed $(python --version)"
