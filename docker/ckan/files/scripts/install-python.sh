#!/bin/bash -e

echo "Installing OS dependencies"

# load env vars from ${APP_DIR}/.env
set -o allexport
. ${APP_DIR}/.env
set +o allexport

apt update

# =====================================================
# Install Python3 with the default version
apt install -y python3 python3-dev python3-pip python3-venv
echo "Python3 installed $(which python3)"

# Define python alias for the version installed
ln -s /usr/bin/python3 /usr/bin/python

echo "Python installed $(python --version)"
