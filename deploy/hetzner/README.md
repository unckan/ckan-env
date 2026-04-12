# Deploy en Hetzner Cloud

Despliegue simple de CKAN + Postgres + Redis + Solr en un VPS de Hetzner usando
`docker compose` y Caddy como reverse proxy con TLS automático.

## 1. Crear el servidor

En la consola de Hetzner Cloud:

- Imagen: **Ubuntu 24.04**
- Tipo de instancia: **x86 (AMD/Intel)** — usar **CPX41** o **CX42**
  (8 vCPU, 16 GB RAM). **NO** usar instancias ARM (`CAX...`): las imágenes
  oficiales de CKAN (`ckan/ckan-postgres-dev`, `ckan/ckan-solr`) se publican
  solo para `linux/amd64`, y correrlas bajo emulación QEMU en ARM es lento e
  inestable. La diferencia de precio con ARM es pequeña y no vale el dolor.
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

El `docker-compose.prod.yml` es **autosuficiente** — no hereda del compose de
dev. Es intencional: al mergear múltiples `-f`, Docker Compose **concatena**
las listas de `ports`, así que quedan activos los bindings de ambos archivos
y colisionan entre sí. Un compose de prod self-contained evita ese problema
y es más predecible.

Solo publica el puerto `5000` del contenedor `ckan_uni` (atado a `127.0.0.1`
para que lo consuma Caddy). Postgres, Redis y Solr no exponen puertos al
host: se comunican entre sí por la red interna del compose usando los
hostnames `postgresql_uni`, `redis_uni` y `solr_uni`.

```bash
cd /home/ckan/ckan-env/deploy/hetzner
docker compose -f docker-compose.prod.yml up -d
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

# Permitir que el usuario `caddy` atraviese /home/ckan/... hasta el symlink.
# Por default /home/ckan es 750 y el servicio caddy (que corre como usuario
# `caddy`) no puede leer el archivo. `o+x` en los directorios permite solo
# traversal (no listado) y `o+r` en el Caddyfile permite la lectura.
chmod o+x /home/ckan /home/ckan/ckan-env /home/ckan/ckan-env/deploy /home/ckan/ckan-env/deploy/hetzner
chmod o+r /home/ckan/ckan-env/deploy/hetzner/Caddyfile

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
docker compose -f docker-compose.prod.yml up -d
```

**Logs**

```bash
docker compose -f docker-compose.prod.yml logs -f ckan_uni
```

**Backup de Postgres**

```bash
docker exec postgresql_uni pg_dumpall -U postgres | gzip > ~/backup-$(date +%F).sql.gz
```

Los volúmenes `pg_data`, `solr_data` y `ckan_storage` están en
`/var/lib/docker/volumes/` — incluirlos en el backup del servidor.

## Sincronizar datos desde producción

El script `scripts/sync-from-prod.sh` trae todos los datos (organizaciones,
grupos, usuarios, datasets con extras y archivos de recursos) desde una
instancia CKAN de producción hacia este server, de forma idempotente.

**Requisitos en el server**:

```bash
# Instalar ckanapi (una sola vez)
uv venv
uv pip install ckanapi
```

**Necesitás dos API keys de sysadmin**: una en prod (para leer) y una en
local (para escribir). Para generar la local:

```bash
docker exec -it ckan_uni ckan user token add <usuario-admin> sync-from-prod
```

**Uso**:

```bash
cd /home/ckan/ckan-env/deploy/hetzner/scripts

PROD_URL=https://ckan-prod.example.org \
PROD_KEY=<token-prod> \
LOCAL_KEY=<token-local> \
./sync-from-prod.sh
```

**Qué hace**:

1. `ckanapi dump` de organizaciones, grupos, usuarios y datasets desde prod.
2. `ckanapi load` (upsert) en el CKAN local — preserva IDs y `extras` (que es
   donde `ckanext-superset` guarda su info).
3. Descarga los archivos binarios de los resources con la API key de prod y
   los copia con `docker cp` al storage del container (`/app/unckan/storage`).

**Idempotencia**: correrlo dos veces no duplica. `ckanapi load` hace upsert,
y los archivos ya existentes en storage se saltean.

**Limitaciones conocidas** (inherentes al API de CKAN, no del script):

- **Passwords de usuarios** no se exportan. Los usuarios deben resetear al
  primer login, o setear manualmente con
  `docker exec -it ckan_uni ckan user setpass <user>`.
- **API tokens** de usuarios deben regenerarse.
- **Activity stream / tracking / revisions** no viajan.

## Ajustes de memoria para servers chicos (8 GB)

Con el stack completo (CKAN + 4 workers gunicorn + Solr + Postgres + Redis)
un server de 8 GB queda muy al límite y el OOM killer mata workers. Para
evitarlo, aplicamos dos ajustes **solo en Hetzner**, sin afectar dev:

1. **Reducir gunicorn a 2 workers**. Se controla con la env var
   `GUNICORN_WORKERS`, que `prepare-supervisor.sh` respeta (default `4` para
   dev, backwards-compatible). En el `local.env` del server (gitignored):

   ```bash
   GUNICORN_WORKERS=2
   ```

   Como los env vars son build-time, después de tocar `local.env` hay que
   `make build` en `docker/` y `up -d` en `deploy/hetzner/`.

2. **Limitar el heap de Solr a 512m**. Ya está aplicado en el
   `docker-compose.prod.yml` (env var `SOLR_HEAP=512m` en el servicio
   `solr_uni`). Sin modificaciones adicionales, se aplica automáticamente
   en el próximo `up -d`.

Con estos dos ajustes el consumo baja ~2 GB y el stack aguanta en 8 GB.
Si en algún momento querés mejor concurrencia, la forma correcta es
resize del server a 16 GB y subir `GUNICORN_WORKERS` a 4 en `local.env`.

## Notas

- Kamal no se usa a propósito: para un único host con un stack estable,
  `docker compose` directo es más simple y suficiente.
- El `docker-compose.prod.yml` es autosuficiente y no hereda del compose
  de dev: Compose mergea listas de `ports` concatenando en vez de
  reemplazar, lo que provoca colisiones. Mantenerlo separado es más
  predecible.
