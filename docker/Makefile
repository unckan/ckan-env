.PHONY: build clean up debug
	
build:
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@if [ ! -f docker-compose.yml ]; then cp docker-compose.example.yml docker-compose.yml; fi
	$(eval -include .env)
	BUILDKIT_PROGRESS=plain docker build \
		--file ckan/Dockerfile \
		--build-arg ENV_NAME=${ENV_NAME} \
		--build-arg CKAN_GIT_URL=${CKAN_GIT_URL} \
		--build-arg CKAN_GIT_BRANCH=${CKAN_GIT_BRANCH} \
		--build-arg TZ=${TZ} \
		-t unckan:${ENV_NAME} ckan
	docker compose build

down:
	docker-compose down

clean:
	docker-compose down -v --remove-orphans

debug:
	docker-compose build
	docker-compose run --service-ports ckan

up:
	docker-compose up

build-up:
	docker-compose build
	docker-compose up

ckan-worker:
	docker-compose exec ckan ckan jobs worker
