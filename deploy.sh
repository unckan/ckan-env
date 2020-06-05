#!/bin/bash
set -e

IMAGE="$DOCKER_USERNAME/ckan-env"
VERSION=$TRAVIS_BRANCH

echo "Docker login"
docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
echo "Docker push 1"
docker push ${IMAGE}:${VERSION}

if [ "$TRAVIS_BRANCH" = "master" ]; then
    echo "Docker push to :latest"
    docker push ${IMAGE}:latest
else
    echo "Docker NO push to :latest"
fi
