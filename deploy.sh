set -e

IMAGE="$DOCKER_USERNAME/ckan-env"
VERSION=$TRAVIS_BRANCH

echo "Docker login"
docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
echo "Docker push 1"
docker push ${IMAGE}:${VERSION}
echo "Docker push 2"
docker push ${IMAGE}:latest