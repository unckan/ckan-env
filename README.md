[![Docker Stars](https://img.shields.io/docker/stars/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
[![Docker Pulls](https://img.shields.io/docker/pulls/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
[![Docker Automated](https://img.shields.io/docker/automated/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)
[![Docker Build](https://img.shields.io/docker/build/avdata99/ckan-env.svg)](https://hub.docker.com/r/avdata99/ckan-env/tags)

# Entorno CKAN para Universidades Argentinas

Entorno completo CKAN orientado a Universidades Argentinas.  

Permite extraer datos de sistemas SIU con el plugin [ckanext-siu-harvester](https://github.com/avdata99/ckanext-siu-harvester) (que incluye la librería [siu-data](https://github.com/avdata99/pySIUdata)).  

Incluye tambien la extension para previsualizaciones [ckanext-datasetpreview](https://github.com/avdata99/ckanext-datasetpreview/blob/master/README.md).  

El template usado está en el repositorio [ckanext-ui-universidad](https://github.com/avdata99/ckanext-ui-universidad).

ckan-env/develop imagen oficial actual.

## Entorno

El portal completo está compuesto por:
 - CKAN 2.9 (python 3) y CKAN 2.8.4 (Python 2, requiere actualizarse)
   + Portal de datos base
 - ckanext-siu-harvester
   + Extensión para cosechar datos desde sistemas SIU
 - ckanext-datasetpreview
   + Extension para agregar gráficos en la lista de datasets

## Correr localmente

```
docker-compose up
```
