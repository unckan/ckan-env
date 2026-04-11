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

El `Caddyfile` del repo usa `{$CKAN_DOMAIN}` como placeholder, así el dominio
real nunca queda versionado. Enlazamos el archivo del repo a `/etc/caddy` (así
un `git pull` actualiza la config) e inyectamos el dominio como variable de
entorno del servicio systemd.

Como `root`:

```bash
# Symlink al Caddyfile del repo (no hace falta copiar ni editar nada)
ln -sf /home/ckan/ckan-env/deploy/hetzner/Caddyfile /etc/caddy/Caddyfile

# Inyectar el dominio como variable de entorno del servicio caddy
mkdir -p /etc/systemd/system/caddy.service.d
cat > /etc/systemd/system/caddy.service.d/env.conf <<'EOF'
[Service]
Environment=CKAN_DOMAIN=ckan.tu-dominio.org
EOF

systemctl daemon-reload
systemctl restart caddy
systemctl status caddy
```

Caddy gestiona Let's Encrypt automáticamente en el primer request a `https://`.
Para cambiar el dominio en el futuro, solo se edita
`/etc/systemd/system/caddy.service.d/env.conf` y `systemctl restart caddy`.

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
