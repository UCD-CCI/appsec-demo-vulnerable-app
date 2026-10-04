#!/usr/bin/env bash

set -euo pipefail

echo ""
echo "========================================"
echo " Break the AI App Setup"
echo "========================================"
echo ""

MODEL_PATH="models/SmolLM2-360M-Instruct-Q4_K_M.gguf"

mkdir -p models

if [ -f "$MODEL_PATH" ]; then
    echo "[✓] Model already present"
else
    echo "[ ] Downloading model..."
    python3 scripts/download_model.py
fi

echo ""
echo "[ ] Seeding database..."
python3 scripts/seed.py

echo ""
echo "[ ] Stopping existing containers..."
docker compose down --remove-orphans

echo ""
echo "[ ] Rebuilding containers from scratch..."
docker compose build --no-cache

echo ""
echo "[ ] Starting application..."
docker compose up

echo ""
echo "Application available at:"
echo "http://127.0.0.1:8080"
echo ""
