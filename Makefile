IMAGE := avdata99/ckan-env
VERSION:= master

test:
	true

image:
	docker build -t ${IMAGE}:${VERSION} .
	docker tag ${IMAGE}:${VERSION} ${IMAGE}:latest

push-image:
	docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
	docker push ${IMAGE}:${VERSION}
	docker push ${IMAGE}:latest
	
.PHONY: image push-image test