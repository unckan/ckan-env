#!/bin/bash

# =============================================================================

# Local Develop
# Install any local extensions in the src_extensions volume
echo "Looking for local extensions to install..."
echo "Extension dir contents:"
ls -la $SRC_EXTENSIONS_DIR
for i in $SRC_EXTENSIONS_DIR/*
do
    if [ -d $i ];
    then

        if [ -f $i/setup.py ];
        then
            cd $i
            python3 $i/setup.py develop
            echo "Found setup.py file in $i"
            cd $APP_DIR
        fi

        # Point `use` in test.ini to location of `test-core.ini`
        if [ -f $i/test.ini ];
        then
            echo "Updating \`test.ini\` reference to \`test-core.ini\` for plugin $i"
            ckan config-tool $i/test.ini "use = config:../../src/ckan/test-core.ini"
        fi
    fi
done

# Set debug to true
# Requires pip install flask-debugtoolbar
echo "Enabling debug mode"
ckan config-tool $CKAN_INI -s DEFAULT "debug = true"

# =============================================================================

# Run the prerun script to init CKAN and create the default admin user
sudo -u ckan -EH python3 prerun.py

# Run any startup scripts provided by images extending this one
if [[ -d "/docker-entrypoint.d" ]]
then
    for f in /docker-entrypoint.d/*; do
        case "$f" in
            *.sh)     echo "$0: Running init file $f"; . "$f" ;;
            *.py)     echo "$0: Running init file $f"; python3 "$f"; echo ;;
            *)        echo "$0: Ignoring $f (not an sh or py file)" ;;
        esac
        echo
    done
fi

# Start supervisord
supervisord --configuration /etc/supervisord.conf &
# Start uwsgi for Local dev
sudo -u ckan -EH ckan -c $CKAN_INI run -H 0.0.0.0
