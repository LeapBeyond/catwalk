#!/usr/bin/env bash
set -e

PUSH=${1-true}

source .env
docker build . \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VCS_REF=$(git rev-parse --short HEAD) \
  --build-arg VERSION=${CATWALK_VERSION} \
  -t ${DOCKER_TAG}:${CATWALK_VERSION} \
  -t ${DOCKER_TAG}:latest

if [ "$PUSH" = true ]; then
  docker push ${DOCKER_TAG}:${CATWALK_VERSION}
  docker push ${DOCKER_TAG}:latest
fi
