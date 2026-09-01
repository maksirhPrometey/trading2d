#!/usr/bin/env bash
set -euo pipefail

mkdir -p "${STATIC_ROOT:-/app/staticfiles}" /app/media

echo "==> Waiting for PostgreSQL (${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432})..."
python <<'PY'
import os
import socket
import sys
import time

import psycopg2

url = os.environ.get('DATABASE_URL', '')
host = os.environ.get('POSTGRES_HOST', 'db')
port = int(os.environ.get('POSTGRES_PORT', '5432'))

for _ in range(30):
    try:
        if url:
            psycopg2.connect(url)
        else:
            with socket.create_connection((host, port), timeout=2):
                pass
        print('==> DB ready')
        break
    except (OSError, psycopg2.OperationalError):
        time.sleep(2)
else:
    print('FATAL: DB not ready')
    sys.exit(1)
PY

echo "==> Django check + migrate + compilemessages + collectstatic"
python manage.py check --deploy --fail-level ERROR
python manage.py migrate --noinput
python manage.py compilemessages -l uk -l ru -l en || true
python manage.py collectstatic --noinput

_static_count=$(find "${STATIC_ROOT:-/app/staticfiles}" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "==> static files: ${_static_count}"
if [ "${_static_count:-0}" -lt 10 ]; then
  echo "WARN: staticfiles count low — перевір STATIC_ROOT і collectstatic"
fi

exec "$@"
