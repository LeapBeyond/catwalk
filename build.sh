#!/usr/bin/env bash
##############################################################################
#
# Copyright 2019 Leap Beyond Emerging Technologies B.V. (unless otherwise stated)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##############################################################################


PUSH=false

help()
{
  echo "Usage: ${0} [--push]"
  echo ""
  echo "Build and optionally push the catwalk docker image"
  echo ""
  echo "  --push                Push the docker image"
  echo "  --help                Print help message and exit"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --push)
      PUSH=true
      ;;
    --help)
      help
      exit 0
      ;;
    *)
      echo -e "Invalid argument: ${1}\n"
      help
      exit 1
      ;;
  esac
  shift
done

set -e

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
