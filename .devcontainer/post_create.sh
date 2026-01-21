#!/usr/bin/env bash
set -euo pipefail

echo "[post_create] Starting bootstrap..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is not available in the container. Please use an image with Python 3 installed."
  exit 1
fi

echo "[post_create] Upgrading pip and installing requirements"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "[post_create] Bootstrap complete."
