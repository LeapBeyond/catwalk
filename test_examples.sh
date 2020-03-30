#!/usr/bin/env bash
set -e

for example in example_models/*/; do
  echo ${example%/}

  catwalk test-model --model-path ${example}
  catwalk test-server --model-path ${example}
done
