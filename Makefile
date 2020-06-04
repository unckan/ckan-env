.PHONY: all build clean up debug

all: build

build:
	docker-compose build

clean:
	docker-compose down -v --remove-orphans

debug:
	docker-compose build
	docker-compose run --service-ports ckan

up:
	docker-compose up

up-local:
	# up with local env (to debug exts)
	docker-compose -f docker-compose.yml -f docker-compose-dev.yml up

test-local-siu-ext:
	docker-compose \
		-f docker-compose.yml \
		-f docker-compose-dev.yml \
		exec ckan \
		bash -c "cd src_extensions/ckanext-siu-harvester && \
		nosetests --ckan \
		--with-pylons=test.ini \
		ckanext.siu_harvester.tests"
