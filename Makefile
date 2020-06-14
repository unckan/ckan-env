IMAGE := avdata99/ckan-env
VERSION := $(shell git rev-parse --abbrev-ref HEAD)
TAG := $(shell if [ ${VERSION} = 'master' ] ; then echo 'latest' ; else echo ${VERSION} ; fi)

test:
	true

image:
	echo "Tag: ${IMAGE}:${TAG}"
	docker build -t ${IMAGE}:${TAG} .
	
push-image:
	echo "Push: ${IMAGE}:${TAG}"
	docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
	docker push ${IMAGE}:${TAG}
	
.PHONY: image push-image test