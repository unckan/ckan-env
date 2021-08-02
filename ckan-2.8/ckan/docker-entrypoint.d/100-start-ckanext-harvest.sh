#!/bin/bash

echo "Enabling ckanext-harvest"
paster --plugin=ckanext-harvest harvester initdb --config=$CKAN_INI