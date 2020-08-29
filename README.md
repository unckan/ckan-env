[![Build Status](https://travis-ci.org/avdata99/ckan-env.svg?branch=master)](https://travis-ci.org/avdata99/ckan-env)
[![Docker Stars](https://img.shields.io/docker/stars/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
[![Docker Automated](https://img.shields.io/docker/automated/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
[![Docker Build](https://img.shields.io/docker/build/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
# Entorno CKAN

Deploy a dockerhub test

## Publicar imagenes

Se realiza automáticamente con cada push (vía _Travis_) a `$DOCKER_USERNAME/ckan-env/latest` (para rama `master`) o `$DOCKER_USERNAME/ckan-env:BRANCH-NAME` (en otras ramas)

## Para trabajo local

Compilar localmente como `ckan-env:latest` (para rama `master`) o `ckan-env:BRANCH-NAME` (en otras ramas)

```
make local-image
```