#!/bin/bash

echo "Enabling ckanext-harvest"
ckan --config=$CKAN_INI harvester initdb
