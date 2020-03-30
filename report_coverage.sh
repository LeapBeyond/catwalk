#!/usr/bin/env bash
set -e

rm -f .coverage

coverage run -m unittest discover tests

for example in example_models/*/; do
  echo ${example%/}

  coverage run --append -m catwalk test-model --model-path ${example}
  coverage run --append -m catwalk test-server --model-path ${example}
done

coverage report -m
