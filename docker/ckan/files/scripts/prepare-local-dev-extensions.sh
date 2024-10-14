#!/bin/bash

# From ckan docker base
# https://github.com/ckan/ckan-docker-base/blob/main/ckan-2.10/dev/setup/start_ckan_development.sh#L9-L48
# All CKAN extensions in this folder will be installed in the CKAN development environment
cd $APP_DIR

SRC_EXTENSIONS_DIR=$APP_DIR/src_extensions
mkdir -p $SRC_EXTENSIONS_DIR

# Install any local extensions in the src_extensions volume
echo "Looking for local extensions to install..."
echo "Extension dir contents:"
ls -la $SRC_EXTENSIONS_DIR
for i in $SRC_EXTENSIONS_DIR/*
do
    if [ -d $i ];
    then

        if [ -f $i/pip-requirements.txt ];
        then
            pip install -r $i/pip-requirements.txt
            echo "Found requirements file in $i"
        fi
        if [ -f $i/requirements.txt ];
        then
            pip install -r $i/requirements.txt
            echo "Found requirements file in $i"
        fi
        if [ -f $i/dev-requirements.txt ];
        then
            pip install -r $i/dev-requirements.txt
            echo "Found dev-requirements file in $i"
        fi
        if [ -f "$i/setup.py" ] || [ -f "$i/pyproject.toml" ];
        then
            cd $i
            echo "*******************************************"
            echo "*******************************************"
            echo "Installing $i ..."
            pip install -e .
            echo "$i installed"
            echo "*******************************************"
            echo "*******************************************"
            cd ..
        fi

        # Point `use` in test.ini to location of `test-core.ini`
        if [ -f $i/test.ini ];
        then
            echo "Updating 'test.ini' reference to 'test-core.ini' for plugin $i"
            ckan config-tool $i/test.ini "use = config:../../ckan/test-core.ini"
            if [ "$i" == "$SRC_EXTENSIONS_DIR/ckanext-uni" ];
            then
                echo "Updating 'test.ini' to allow testing the extension"
                ckan config-tool $i/test.ini "sqlalchemy.url = ${SQLALCHEMY_URL}"
                ckan config-tool $i/test.ini "ckan.redis.url = ${CKAN_REDIS_URL}"
                ckan config-tool $i/test.ini "solr_url = ${SOLR_URL}"
                ckan config-tool $i/test.ini "ckan.datastore.write_url = ${DATASTORE_WRITE_URL}"
                ckan config-tool $i/test.ini "ckan.datastore.read_url = ${DATASTORE_READ_URL}"
            fi
        fi
    fi
done

cd $APP_DIR

# Allow HTTPS locally
ckan config-tool ckan.ini "ckan.devserver.ssl_cert = ${APP_DIR}/files/cert/localhost.cert"
ckan config-tool ckan.ini "ckan.devserver.ssl_key = ${APP_DIR}/files/cert/localhost.key"

echo "prepare-local-dev-extensions Finished"
