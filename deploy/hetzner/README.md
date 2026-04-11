# Deploy en Hetzner Cloud

Despliegue simple de CKAN + Postgres + Redis + Solr en un VPS de Hetzner usando
`docker compose` y Caddy como reverse proxy con TLS automático.

## 1. Crear el servidor

En la consola de Hetzner Cloud:

- Imagen: **Ubuntu 24.04**
- SSH key: la pública generada localmente (`ssh-keygen -t ed25519 -C "hetzner-unckan-dev" -f ~/.ssh/hetzner_unckan_dev`)
- Firewall: abrir `22`, `80`, `443` (todo lo demás cerrado)

### IP

Nos dieron la IP aaa.bbb.ccc.ddd
ssh -i ~/.ssh/hetzner_unckan_dev root@aaa.bbb.ccc.ddd

## 2. Apuntar DNS

Crear un registro `A` del dominio (ej. `ckan.example.org`) a la IP del servidor.

## 3. Provisión inicial del servidor

```bash
ssh -i ~/.ssh/hetzner_unckan_dev root@aaa.bbb.ccc.ddd

# Docker + compose plugin
apt update && apt upgrade -y
apt install -y docker.io docker-compose-v2 git caddy make

# Usuario no-root opcional (recomendado)
adduser --disabled-password --gecos "" ckan
usermod -aG docker ckan
```

## 4. Clonar el repo y preparar env

```bash
su - ckan
git clone https://github.com/unckan/ckan-env.git /home/ckan/ckan-env
cd /home/ckan/ckan-env
cp deploy/hetzner/.env.example deploy/hetzner/.env
# editar deploy/hetzner/.env y poner una password real para Postgres
```

## 5. Build de la imagen CKAN

La imagen `unckan:local` se construye con el Makefile existente del repo,
que ya gestiona el contexto de build correcto (`docker/ckan`) y crea los
archivos auxiliares que hacen falta (`local.env`, etc.):

```bash
cd /home/ckan/ckan-env/docker
make build
```

## 6. Levantar el stack

El compose de prod hereda del de dev y sobrescribe lo necesario (quita bind
mounts de dev, publica puertos solo en `127.0.0.1`, agrega `restart`).

```bash
cd /home/ckan/ckan-env/deploy/hetzner
docker compose \
  -f ../../docker/docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d
```

## 7. Caddy (TLS automático)

Como `root`:

```bash
cp /home/ckan/ckan-env/deploy/hetzner/Caddyfile /etc/caddy/Caddyfile
# editar /etc/caddy/Caddyfile y reemplazar ckan.example.org por el dominio real
systemctl reload caddy
```

Caddy gestiona Let's Encrypt automáticamente en el primer request a `https://`.

## Operación

**Deploy de cambios**

```bash
cd /home/ckan/ckan-env
git pull
cd docker && make build
cd ../deploy/hetzner
docker compose -f ../../docker/docker-compose.yml -f docker-compose.prod.yml up -d
```

**Logs**

```bash
docker compose -f ../../docker/docker-compose.yml -f docker-compose.prod.yml logs -f ckan_uni
```

**Backup de Postgres**

```bash
docker exec postgresql_uni pg_dumpall -U postgres | gzip > ~/backup-$(date +%F).sql.gz
```

Los volúmenes `pg_data`, `solr_data` y `ckan_storage` están en
`/var/lib/docker/volumes/` — incluirlos en el backup del servidor.

## Notas

- Kamal no se usa a propósito: para un único host con un stack estable,
  `docker compose` directo es más simple y suficiente.
- El compose de dev monta extensiones locales (`ckanext-dbquery`, etc.) que en
  prod no existen; por eso el override de prod redefine `volumes` en
  `ckan_uni` dejando solo lo necesario.
