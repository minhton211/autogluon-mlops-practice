#!/usr/bin/env bash
set -euo pipefail

# Expected runtime environment variables:
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

# Optional: configure DVC remote endpoint from env
# if AWS_S3_ENDPOINT_URL is set:
if [ -n "${AWS_S3_ENDPOINT_URL:-}" ]; then
  dvc remote modify storage endpointurl "${AWS_S3_ENDPOINT_URL}"
fi

# pull model at container start (requires credentials at runtime)
dvc pull /app/models/autogluonTS.dvc

# exec python with all args
exec python -u /app/app.py "$@"
