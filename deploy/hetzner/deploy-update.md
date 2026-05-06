# Deploy and update

Access to the server

```
ssh -i ~/.ssh/hetzner_unckan_dev root@ckan-dev-domain.com
# Pasarse al usuario ckan para no correr las cosas como root
su - ckan
```

Traer la ultima versión

```bash
cd /home/ckan/ckan-env
git pull
```

Volver a compilar

```bash
cd docker
make build
cd ../deploy/hetzner
docker compose -f docker-compose.prod.yml up -d
```

`postgresql_uni`, `redis_uni` y `solr_uni` no cambian (no se reinician).
Solo `ckan_uni` se recrea con la imagen nueva.

## Otras tareas en el servidor

Todos los `docker compose` corren desde `/home/ckan/ckan-env/deploy/hetzner`
con el usuario `ckan`. Para abreviar:

```bash
cd /home/ckan/ckan-env/deploy/hetzner
alias dcp='docker compose -f docker-compose.prod.yml'
```

### Entrar al contenedor para correr comandos de CKAN

El usuario por default dentro de `ckan_uni` es `ckan` y el venv ya queda en
`PATH`. La env var `CKAN_INI` apunta al `.ini` activo, así que no hace falta
pasarlo a mano.

```bash
docker exec -it ckan_uni bash
# adentro del container:
ckan -c $CKAN_INI search-index rebuild
ckan -c $CKAN_INI db upgrade
ckan -c $CKAN_INI user list
ckan -c $CKAN_INI user token add <usuario> <nombre-token>
ckan -c $CKAN_INI sysadmin add <usuario>
```

Para un one-shot sin shell interactiva:

```bash
docker exec -it ckan_uni bash -lc "ckan -c \$CKAN_INI search-index rebuild"
```

### Entrar al contenedor como `root` (supervisor, apt, etc.)

CKAN, el worker y `yacron` corren bajo Supervisor. Los procesos registrados
son `ckan`, `ckan-worker` y `yacron`. `supervisorctl` necesita root:

```bash
docker exec -it -u root ckan_uni bash
# adentro del container:
supervisorctl status
supervisorctl restart ckan            # reinicia gunicorn (la app web)
supervisorctl restart ckan-worker     # reinicia el background job worker
supervisorctl restart yacron          # reinicia el cron interno
supervisorctl restart all
```

Reiniciar el container entero (alternativa más pesada, recrea procesos desde
cero pero mantiene los volúmenes):

```bash
dcp restart ckan_uni
```

### Ver logs en vivo

Stdout del container (gunicorn + entrypoint):

```bash
dcp logs -f ckan_uni
dcp logs -f --tail=200 ckan_uni       # últimas 200 líneas y seguir
dcp logs -f                           # todos los servicios
```

Logs de Supervisor (más detallados por proceso, dentro del container):

```bash
docker exec -it ckan_uni tail -f /var/log/supervisor/ckan.log
docker exec -it ckan_uni tail -f /var/log/supervisor/ckan-worker.log
docker exec -it ckan_uni tail -f /var/log/supervisor/yacron.log
```

Caddy (TLS / proxy reverso) corre en el host como servicio systemd:

```bash
journalctl -u caddy -f
systemctl status caddy
```

### Estado y recursos

```bash
dcp ps                                 # estado de los containers
docker stats --no-stream               # CPU / memoria por container
df -h                                  # espacio en disco del host
docker system df                       # espacio usado por imágenes/volúmenes
```

### Acceso directo a Postgres / Redis / Solr

Estos servicios no exponen puertos al host: hay que entrar por la red interna
del compose.

```bash
# psql contra la DB de CKAN
docker exec -it postgresql_uni psql -U ckan -d ckan

# CLI de Redis
docker exec -it redis_uni redis-cli

# Admin UI de Solr — solo accesible vía SSH tunnel desde local:
#   ssh -i ~/.ssh/hetzner_unckan_dev -L 8983:localhost:8983 root@<server>
# y dentro del server:
docker exec -it solr_uni bash -lc "curl -s localhost:8983/solr/admin/cores?action=STATUS"
```

### Backup rápido de Postgres

```bash
docker exec postgresql_uni pg_dumpall -U postgres | gzip > ~/backup-$(date +%F).sql.gz
```

(Para backup completo del server, incluir también los volúmenes
`/var/lib/docker/volumes/{pg_data,solr_data,ckan_storage}`.)

### Limpiar imágenes viejas después de varios `make build`

Cada build deja la imagen anterior como `<none>`. Para liberar espacio:

```bash
docker image prune -f                  # borra solo dangling (<none>)
docker system prune -f                 # borra también redes/build cache no usados
```

**No** correr `docker volume prune` sin revisar antes — los volúmenes de
Postgres / Solr / storage de CKAN viven ahí.
