.PHONY: build clean up debug

build:
	@if [ ! -f docker-compose.yml ]; then cp docker-compose.sample.yml docker-compose.yml; fi
	@if [ ! -f docker/ckan/files/env/local.env ]; then touch ckan/files/env/local.env; fi
	$(eval TZ ?= America/Argentina/Cordoba)
	$(eval ENV_NAME ?= local)
	BUILDKIT_PROGRESS=plain docker build \
		--file ckan/Dockerfile \
		--build-arg ENV_NAME=${ENV_NAME} \
		--build-arg TZ=${TZ} \
		-t unckan:${ENV_NAME} ckan
	echo "Build done unckan:${ENV_NAME}"

down:
	docker compose down

clean:
	docker compose down -v --remove-orphans

debug:
	docker compose build
	docker compose run --service-ports ckan_uni

up:
	docker compose up

build-up:
	docker compose build
	docker compose up

ckan-worker:
	docker compose exec ckan_uni ckan jobs worker

bash:
	docker compose exec ckan_uni bash
