#!/bin/sh
set -eu

mkdir -p /app/data
if [ ! -f /app/data/workshop.db ]; then
  echo "No workshop.db found — seeding database..."
  python /app/scripts/seed.py
fi

exec "$@"
