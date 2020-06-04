set -e

IMAGE="$DOCKER_USERNAME/ckan-env"
VERSION=$TRAVIS_BRANCH

echo "Building ${IMAGE}:${VERSION}"
docker build -t ${IMAGE}:${VERSION} .
echo "Tagging ${IMAGE}:${VERSION}"
docker tag ${IMAGE}:${VERSION} ${IMAGE}:latest