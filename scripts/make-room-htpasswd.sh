#!/usr/bin/env bash
# Create deploy/room-auth/htpasswd for the optional nginx Basic Auth gate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/deploy/room-auth/htpasswd"
USER_NAME="${1:-${ROOM_USER:-conference}}"
PASSWORD="${2:-${ROOM_PASSWORD:-secret}}"

if ! command -v openssl >/dev/null 2>&1; then
  echo "openssl is required to hash the password" >&2
  exit 1
fi

HASH="$(openssl passwd -apr1 "$PASSWORD")"
printf '%s:%s\n' "$USER_NAME" "$HASH" > "$OUT"
chmod 644 "$OUT"
echo "Wrote $OUT (user=$USER_NAME)"
echo "Enable gate: docker compose -f docker-compose.yml -f docker-compose.room-auth.yml up -d"
echo "Disable gate: docker compose up -d"
