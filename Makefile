IMAGE := avdata99/ckan-env
VERSION := $(shell git rev-parse --abbrev-ref HEAD)
TAG := $(shell if [ ${VERSION} = 'master' ] ; then echo 'latest' ; else echo ${VERSION} ; fi)

.PHONY: build clean up debug image push-image


local-image:
	echo "Tag: ckan-env:${TAG}"
	docker build -t ckan-env:${TAG} .
	
push-image:
	echo "Build: ${IMAGE}:${TAG}"
	docker build -t ${IMAGE}:${TAG} .
	echo "Push: ${IMAGE}:${TAG}"
	docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
	docker push ${IMAGE}:${TAG}
	
build:
	docker-compose build

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

harvest-gather-local:
	docker-compose exec ckan paster --plugin=ckanext-harvest harvester gather_consumer

harvest-fetch-local:
	docker-compose exec ckan paster --plugin=ckanext-harvest harvester fetch_consumer

harvest-run-local:
	docker-compose exec ckan paster --plugin=ckanext-harvest harvester run

ckan-worker:
	docker-compose exec ckan paster --plugin=ckan jobs worker

test-local-siu-ext:
	# require extension mounted in "volumes" at docker-compose.yml
	docker-compose \
		-f docker-compose.yml \
		-f docker-compose-dev.yml \
		exec ckan \
		bash -c "cd src_extensions/ckanext-siu-harvester && \
		nosetests --ckan \
		--with-pylons=test.ini \
		ckanext.siu_harvester.tests"