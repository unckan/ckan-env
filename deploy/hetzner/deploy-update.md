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
