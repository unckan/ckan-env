.PHONY: build clean up debug
	
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

gather:
	docker-compose exec ckan ckan harvester gather-consumer

fetch:
	docker-compose exec ckan ckan harvester fetch-consumer

harvest-run:
	docker-compose exec ckan ckan harvester run

ckan-worker:
	docker-compose exec ckan ckan jobs worker
