#!/bin/bash -e

echo "Installing Python"

# =====================================================
# Install Python3 with the default version
apt install -y python3 python3-dev python3-pip python3-venv
echo "Python3 installed $(which python3)"

# Define python alias for the version installed
ln -s /usr/bin/python3 /usr/bin/python

echo "Python installed $(python --version)"
