#!/bin/bash
set -e

IMAGE="$DOCKER_USERNAME/ckan-env"
VERSION=$TRAVIS_BRANCH

echo "Docker login"
docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD

if [ "$TRAVIS_BRANCH" = "master" ]; then
    echo "Docker push to :latest"
    docker push ${IMAGE}:latest
else
    docker push ${IMAGE}:develop
fi
