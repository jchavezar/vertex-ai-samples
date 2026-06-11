#!/usr/bin/env bash
# Wrapper to call register.py with REASONING_ENGINE_ID
set -euo pipefail

if [ -z "${REASONING_ENGINE_ID:-}" ]; then
  echo "ERROR: REASONING_ENGINE_ID is required."
  exit 1
fi

python3 register.py
