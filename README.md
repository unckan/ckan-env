# Entorno CKAN para Universidades Argentinas

Entorno completo CKAN orientado a Universidades Argentinas.  
Este proyecto esta orientado a permitir automatizar la publicación de datos universitario masivamente y sin requerir mayor esfuerzo técnico.  
Por el momento permite automatizar la publicación de datos ya contenidos en los sistemas SIU, que ya utilizan casi todas las universidades argentinas.  
Esta en los planes extraer datos de las instancias de SIGEva de CONICET.  
Al estar desarrollado sobre CKAN este proyecto permite además subir datos manualmente o desarrollar conectores a otros sistemas.  


## Entorno

El portal completo está compuesto por:
 - CKAN 2.10.5 (python 3)
   + Portal de datos base
 - Extensiones (en progreso)
   + [SIU Harvester](https://github.com/unckan/ckanext-siu-harvester): Extensión para cosechar datos desde sistemas [SIU](https://www.siu.edu.ar/) usando la librería [pySIUData](https://github.com/unckan/pySIUdata) (creada especialmente como parte de este proceso).
   + [Dataset previews](https://github.com/unckan/ckanext-datasetpreview): Extensión CKAN para agregar gráficos a los datasets de manera simple.
   + (TODO deprecated) El template CKAN usado está en el repositorio [UI Universidad](https://github.com/unckan/ckanext-ui-universidad).
   + Incluye además otras extensiones desarrolladas por la comunidad CKAN.
   + [En desarrollo](https://github.com/unckan/pysigeva): Integración con el [SIGEva (Sistema Integral de Gestión y Evaluación)](https://sigeva.conicet.gov.ar/) de CONICET.

## Correr localmente

```
docker-compose up
```

## Imagen pública

La compilación de esta imagen esta [disponible en DockerHub](https://hub.docker.com/r/avdata99/unckan/tags?page=1&ordering=last_updated).  
