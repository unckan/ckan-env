# Entorno CKAN para Universidades Argentinas

Entorno completo CKAN orientado a Universidades Argentinas.  
Este proyecto esta orientado a permitir automatizar la publicación de datos universitario masivamente y sin requerir mayor esfuerzo técnico.  
Por el momento permite automatizar la publicación de datos ya contenidos en los sistemas SIU, que ya utilizan casi todas las universidades argentinas.  
Esta en los planes extraer datos de las instancias de SIGEva de CONICET.  
Al estar desarrollado sobre CKAN este proyecto permite además subir datos manualmente o desarrollar conectores a otros sistemas.  


## Entorno

El portal completo está compuesto por:
 - CKAN 2.11.3 (python 3)
   + Portal de datos base
 - Extensiones:
   + UNCKAN: Extension interna para la personaización de este portal.
   + [Superset](https://github.com/unckan/ckanext-superset): Extension de CKAN para conectar con [Apache Superset](https://superset.apache.org/).
   + [API TRacking](https://github.com/NorwegianRefugeeCouncil/ckanext-api-tracking)
   + [Announcements](https://github.com/okfn/ckanext-announcements)
   + [Push Errors](https://github.com/unckan/ckanext-push-errors)
   + [DBQuery](https://github.com/unckan/ckanext-dbquery)
   + Citations with [CiteProc](https://github.com/unckan/ckanext-citeproc)
   + [Charts](https://github.com/DataShades/ckanext-charts)


## Correr localmente

```
docker-compose up
```

## Imagen pública

La compilación de esta imagen esta [disponible en DockerHub](https://hub.docker.com/r/avdata99/unckan/tags?page=1&ordering=last_updated).  

## Crear nuevas extensiones

Se puede crear una nueva extension entrando al contenedor, activando el entorno virtual y corriendo el comando de generación de extensiones.

```bash
make bash
source venv/bin/activate
ckan -c /app/unckan/ckan.ini generate extension -o /app/unckan/src_extensions/
```

## Testear extensiones

Cualquier extension montada localmente en `src_extensions` sera adaptada para que sea posible ser testeada.  
Esto se hace en el script `prepare-local-dev-extensions.sh` con la modificacion de su archivo `test.ini`.  

Para testear `ckanext-unckan` (o cualquier otra extension) se puede correr el siguiente comando:

```bash
# Entrar al contenedor
make bash
# Activar el entorno virtual
source venv/bin/activate
# Pararse en la carpeta de la extension
cd src_extensions/ckanext-unckan
# o cd src_extensions/ckanext-superset
# Correr los tests
pytest --ckan-ini=test.ini -vv --disable-warnings ckanext/unckan
# o pytest --ckan-ini=test.ini -vv --disable-warnings ckanext/superset
```
