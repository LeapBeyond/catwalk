#!/usr/bin/env bash
set -e

for example in example_models/*/; do
  echo ${example%/}

  catwalk test_model --model-path ${example}
  catwalk test_server --model-path ${example}
done
