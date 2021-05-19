[![Build Status](https://travis-ci.org/avdata99/ckan-env.svg?branch=master)](https://travis-ci.org/avdata99/ckan-env)
[![Docker Stars](https://img.shields.io/docker/stars/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
[![Docker Automated](https://img.shields.io/docker/automated/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
[![Docker Build](https://img.shields.io/docker/build/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
# Entorno CKAN para Universidades Argentinas

Entorno completo CKAN orientado a Universidades Argentinas.  

Permite extraer datos de sistemas SIU con el plugin [ckanext-siu-harvester](https://github.com/avdata99/ckanext-siu-harvester) (que incluye la librería [siu-data](https://github.com/avdata99/pySIUdata)).  

Incluye tambien la extension para previsualizaciones [ckanext-datasetpreview](https://github.com/avdata99/ckanext-datasetpreview/blob/master/README.md).  


ckan-env/develop imagen oficial actual.

## Correr localmente

```
docker-compose up
```

## Deploy a dockerhub 

Se realiza automáticamente con cada push (vía _Travis_) a `$DOCKER_USERNAME/ckan-env/latest` (para rama `master`) o `$DOCKER_USERNAME/ckan-env:BRANCH-NAME` (en otras ramas)
